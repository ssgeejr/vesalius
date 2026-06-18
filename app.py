"""Tkinter app for checking the current Windows user's AD login details.

The app is read-only. It queries Active Directory for only the currently
logged-in Windows user and shows a plain-English summary.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext
from typing import Any


APP_TITLE = "My AD Login Check"
LOG_FILE = Path(__file__).with_name("my_ad_login_check.log")


def configure_logging() -> None:
    """Configure local file logging for application errors."""
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.ERROR,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    )


def get_windows_username() -> str:
    """Return the current Windows username in plain display form."""
    username = os.environ.get("USERNAME", "").strip()
    domain = os.environ.get("USERDOMAIN", "").strip()

    if username and domain:
        return f"{domain}\\{username}"

    return username or "Unknown user"


def run_ad_lookup() -> dict[str, Any]:
    """Run a read-only AD lookup for the current Windows user.

    Returns:
        A dictionary produced by PowerShell's ConvertTo-Json output.

    Raises:
        RuntimeError: If AD tools are missing, the lookup fails, or no user is
            returned.
    """
    if platform.system() != "Windows":
        raise RuntimeError("This app is designed to run on Windows.")

    username = os.environ.get("USERNAME", "").strip()
    if not username:
        raise RuntimeError("Could not determine the current Windows username.")

    script = """
$ErrorActionPreference = 'Stop'
try {
    Import-Module ActiveDirectory -ErrorAction Stop
} catch {
    Write-Output '__AD_TOOLS_MISSING__'
    exit 0
}

function Convert-ToCentralTimeText {
    param($DateValue)

    if ($null -eq $DateValue) {
        return $null
    }

    $centralTime = [System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId($DateValue, 'Central Standard Time')
    return $centralTime.ToString('yyyy-MM-dd HH:mm:ss zzz')
}

$user = Get-ADUser -Identity $env:USERNAME -Properties DisplayName,LastLogonDate,BadPwdCount,LockedOut
if ($null -eq $user) {
    Write-Output '__USER_NOT_FOUND__'
    exit 0
}

[PSCustomObject]@{
    SamAccountName = $user.SamAccountName
    DisplayName = $user.DisplayName
    LastLogonDate = Convert-ToCentralTimeText $user.LastLogonDate
    BadPwdCount = $user.BadPwdCount
    LockedOut = $user.LockedOut
} | ConvertTo-Json -Compress
"""

    startupinfo = None
    if hasattr(subprocess, "STARTUPINFO"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
            startupinfo=startupinfo,
        )
    except subprocess.TimeoutExpired as exc:
        logging.exception("Active Directory lookup timed out.")
        raise RuntimeError("The Active Directory lookup timed out.") from exc
    except OSError as exc:
        logging.exception("PowerShell could not be started.")
        raise RuntimeError("PowerShell could not be started on this workstation.") from exc

    output = completed.stdout.strip()

    if output == "__AD_TOOLS_MISSING__":
        raise RuntimeError("This workstation does not have the AD tools installed.")

    if output == "__USER_NOT_FOUND__":
        raise RuntimeError("No Active Directory record was found for this Windows user.")

    if completed.returncode != 0:
        logging.error(
            "Active Directory lookup failed. Return code: %s. Error: %s",
            completed.returncode,
            completed.stderr.strip(),
        )
        raise RuntimeError("The Active Directory lookup failed.")

    try:
        result = json.loads(output)
    except json.JSONDecodeError as exc:
        logging.exception("Active Directory lookup returned unreadable output.")
        raise RuntimeError("The Active Directory lookup returned unreadable results.") from exc

    if not isinstance(result, dict):
        logging.error("Active Directory lookup returned unexpected JSON: %r", result)
        raise RuntimeError("The Active Directory lookup returned unexpected results.")

    return result


def run_user_list_lookup() -> list[dict[str, Any]]:
    """Run a read-only AD lookup for the first 10 users returned by AD.

    Returns:
        A list of dictionaries produced by PowerShell's ConvertTo-Json output.

    Raises:
        RuntimeError: If AD tools are missing or the lookup fails.
    """
    if platform.system() != "Windows":
        raise RuntimeError("This app is designed to run on Windows.")

    script = """
$ErrorActionPreference = 'Stop'
try {
    Import-Module ActiveDirectory -ErrorAction Stop
} catch {
    Write-Output '__AD_TOOLS_MISSING__'
    exit 0
}

Get-ADUser -Filter * -ResultSetSize 10 -Properties DisplayName |
    Select-Object SamAccountName,DisplayName |
    ConvertTo-Json -Compress
"""

    startupinfo = None
    if hasattr(subprocess, "STARTUPINFO"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
            startupinfo=startupinfo,
        )
    except subprocess.TimeoutExpired as exc:
        logging.exception("Active Directory user list lookup timed out.")
        raise RuntimeError("The Active Directory user list lookup timed out.") from exc
    except OSError as exc:
        logging.exception("PowerShell could not be started.")
        raise RuntimeError("PowerShell could not be started on this workstation.") from exc

    output = completed.stdout.strip()

    if output == "__AD_TOOLS_MISSING__":
        raise RuntimeError("This workstation does not have the AD tools installed.")

    if completed.returncode != 0:
        logging.error(
            "Active Directory user list lookup failed. Return code: %s. Error: %s",
            completed.returncode,
            completed.stderr.strip(),
        )
        raise RuntimeError("The Active Directory user list lookup failed.")

    if not output:
        return []

    try:
        result = json.loads(output)
    except json.JSONDecodeError as exc:
        logging.exception("Active Directory user list lookup returned unreadable output.")
        raise RuntimeError("The Active Directory user list lookup returned unreadable results.") from exc

    if isinstance(result, dict):
        return [result]

    if isinstance(result, list) and all(isinstance(item, dict) for item in result):
        return result

    logging.error("Active Directory user list lookup returned unexpected JSON: %r", result)
    raise RuntimeError("The Active Directory user list lookup returned unexpected results.")


def run_named_user_lookup(username: str) -> dict[str, Any]:
    """Run a read-only AD lookup for a specific username.

    Args:
        username: The AD username to look up.

    Returns:
        A dictionary produced by PowerShell's ConvertTo-Json output.

    Raises:
        RuntimeError: If AD tools are missing, the lookup fails, or the user is
            not found.
    """
    if platform.system() != "Windows":
        raise RuntimeError("This app is designed to run on Windows.")

    clean_username = username.strip()
    if not clean_username:
        raise RuntimeError("Please enter a username.")

    script = """
$ErrorActionPreference = 'Stop'
try {
    Import-Module ActiveDirectory -ErrorAction Stop
} catch {
    Write-Output '__AD_TOOLS_MISSING__'
    exit 0
}

function Convert-ToCentralTimeText {
    param($DateValue)

    if ($null -eq $DateValue) {
        return $null
    }

    $centralTime = [System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId($DateValue, 'Central Standard Time')
    return $centralTime.ToString('yyyy-MM-dd HH:mm:ss zzz')
}

$lookupUsername = $env:AD_LOOKUP_USERNAME
$user = Get-ADUser -Identity $lookupUsername -Properties DisplayName,LastLogonDate,LastBadPasswordAttempt,BadPwdCount,LockedOut,Enabled,PasswordLastSet,whenCreated,Modified
if ($null -eq $user) {
    Write-Output '__USER_NOT_FOUND__'
    exit 0
}

[PSCustomObject]@{
    SamAccountName = $user.SamAccountName
    DisplayName = $user.DisplayName
    Enabled = $user.Enabled
    LockedOut = $user.LockedOut
    LastLogonDate = Convert-ToCentralTimeText $user.LastLogonDate
    LastBadPasswordAttempt = Convert-ToCentralTimeText $user.LastBadPasswordAttempt
    BadPwdCount = $user.BadPwdCount
    PasswordLastSet = Convert-ToCentralTimeText $user.PasswordLastSet
    Created = Convert-ToCentralTimeText $user.whenCreated
    Modified = Convert-ToCentralTimeText $user.Modified
} | ConvertTo-Json -Compress
"""

    startupinfo = None
    if hasattr(subprocess, "STARTUPINFO"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    lookup_env = os.environ.copy()
    lookup_env["AD_LOOKUP_USERNAME"] = clean_username

    try:
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
            startupinfo=startupinfo,
            env=lookup_env,
        )
    except subprocess.TimeoutExpired as exc:
        logging.exception("Active Directory named user lookup timed out.")
        raise RuntimeError("The Active Directory user lookup timed out.") from exc
    except OSError as exc:
        logging.exception("PowerShell could not be started.")
        raise RuntimeError("PowerShell could not be started on this workstation.") from exc

    output = completed.stdout.strip()

    if output == "__AD_TOOLS_MISSING__":
        raise RuntimeError("This workstation does not have the AD tools installed.")

    if output == "__USER_NOT_FOUND__":
        raise RuntimeError("No Active Directory record was found for that username.")

    if completed.returncode != 0:
        logging.error(
            "Active Directory named user lookup failed. Return code: %s. Error: %s",
            completed.returncode,
            completed.stderr.strip(),
        )
        raise RuntimeError("The Active Directory user lookup failed.")

    try:
        result = json.loads(output)
    except json.JSONDecodeError as exc:
        logging.exception("Active Directory named user lookup returned unreadable output.")
        raise RuntimeError("The Active Directory user lookup returned unreadable results.") from exc

    if not isinstance(result, dict):
        logging.error("Active Directory named user lookup returned unexpected JSON: %r", result)
        raise RuntimeError("The Active Directory user lookup returned unexpected results.")

    return result


def describe_value(value: Any, missing_text: str) -> str:
    """Return a friendly text value for optional AD fields."""
    if value is None or value == "":
        return missing_text

    return str(value)


def format_results(ad_info: dict[str, Any]) -> str:
    """Format AD lookup results as plain-English text."""
    display_name = describe_value(ad_info.get("DisplayName"), "Not available")
    last_logon = describe_value(ad_info.get("LastLogonDate"), "Not available")
    bad_password_count = describe_value(ad_info.get("BadPwdCount"), "Not available")

    locked_out = ad_info.get("LockedOut")
    if locked_out is True:
        locked_text = "Yes, this account is currently locked."
    elif locked_out is False:
        locked_text = "No, this account is not locked."
    else:
        locked_text = "Not available"

    return "\n".join(
        [
            f"Current Windows username: {get_windows_username()}",
            f"AD display name: {display_name}",
            f"Last logon timestamp: {last_logon}",
            f"Bad password count: {bad_password_count}",
            f"Account locked status: {locked_text}",
        ]
    )


def format_user_list(users: list[dict[str, Any]]) -> str:
    """Format a short AD user list as plain-English text."""
    if not users:
        return "No Active Directory users were returned."

    lines = ["First 10 Active Directory users returned:"]
    for index, user in enumerate(users, start=1):
        username = describe_value(user.get("SamAccountName"), "Username not available")
        display_name = describe_value(user.get("DisplayName"), "Display name not available")
        lines.append(f"{index}. {display_name} ({username})")

    return "\n".join(lines)


def format_named_user_results(user_info: dict[str, Any]) -> str:
    """Format a named AD user lookup as plain-English text."""
    enabled = user_info.get("Enabled")
    if enabled is True:
        enabled_text = "Enabled"
    elif enabled is False:
        enabled_text = "Disabled"
    else:
        enabled_text = "Not available"

    locked_out = user_info.get("LockedOut")
    if locked_out is True:
        locked_text = "Locked"
    elif locked_out is False:
        locked_text = "Unlocked"
    else:
        locked_text = "Not available"

    return "\n".join(
        [
            "User lookup results:",
            f"Username: {describe_value(user_info.get('SamAccountName'), 'Not available')}",
            f"Display name: {describe_value(user_info.get('DisplayName'), 'Not available')}",
            f"Account status: {enabled_text}",
            f"Locked status: {locked_text}",
            f"Last login: {describe_value(user_info.get('LastLogonDate'), 'Not available')}",
            "Last computer login: Not available from this user lookup",
            f"Last bad password attempt: {describe_value(user_info.get('LastBadPasswordAttempt'), 'Not available')}",
            f"Bad password count: {describe_value(user_info.get('BadPwdCount'), 'Not available')}",
            f"Password last set: {describe_value(user_info.get('PasswordLastSet'), 'Not available')}",
            f"Account created: {describe_value(user_info.get('Created'), 'Not available')}",
            f"Account last changed: {describe_value(user_info.get('Modified'), 'Not available')}",
        ]
    )


class MyAdLoginCheckApp:
    """Tiny Tkinter GUI for the AD login check."""

    def __init__(self, root: tk.Tk) -> None:
        """Build the app window."""
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("620x360")
        self.root.minsize(520, 300)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(padx=16, pady=(16, 8), anchor="w")

        self.check_button = tk.Button(
            self.button_frame,
            text="Check My Login",
            command=self.check_my_login,
            width=18,
            height=2,
        )
        self.check_button.pack(side=tk.LEFT)

        self.user_list_button = tk.Button(
            self.button_frame,
            text="See User List (First 10)",
            command=self.see_user_list,
            width=24,
            height=2,
        )
        self.user_list_button.pack(side=tk.LEFT, padx=(8, 0))

        self.demo_reset_button = tk.Button(
            self.button_frame,
            text="Demo Password Reset",
            command=self.open_demo_reset_popup,
            width=20,
            height=2,
        )
        self.demo_reset_button.pack(side=tk.LEFT, padx=(8, 0))

        self.second_button_frame = tk.Frame(root)
        self.second_button_frame.pack(padx=16, pady=(0, 8), anchor="w")

        self.user_lookup_button = tk.Button(
            self.second_button_frame,
            text="User Lookup",
            command=self.open_user_lookup_popup,
            width=18,
            height=2,
        )
        self.user_lookup_button.pack(side=tk.LEFT)

        self.results_box = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            height=10,
            state=tk.DISABLED,
        )
        self.results_box.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        self.clear_button = tk.Button(root, text="Clear", command=self.clear_results, width=12)
        self.clear_button.pack(padx=16, pady=(4, 16), anchor="w")

    def set_results(self, text: str) -> None:
        """Replace the results box contents."""
        self.results_box.configure(state=tk.NORMAL)
        self.results_box.delete("1.0", tk.END)
        self.results_box.insert(tk.END, text)
        self.results_box.configure(state=tk.DISABLED)

    def clear_results(self) -> None:
        """Clear the results box."""
        self.set_results("")

    def check_my_login(self) -> None:
        """Look up and display the current user's AD login information."""
        self.check_button.configure(state=tk.DISABLED)
        self.user_list_button.configure(state=tk.DISABLED)
        self.demo_reset_button.configure(state=tk.DISABLED)
        self.user_lookup_button.configure(state=tk.DISABLED)
        self.set_results("Checking your login information...")
        self.root.update_idletasks()

        try:
            ad_info = run_ad_lookup()
            self.set_results(format_results(ad_info))
        except RuntimeError as exc:
            logging.exception("Could not complete AD login check.")
            self.set_results(str(exc))
        finally:
            self.check_button.configure(state=tk.NORMAL)
            self.user_list_button.configure(state=tk.NORMAL)
            self.demo_reset_button.configure(state=tk.NORMAL)
            self.user_lookup_button.configure(state=tk.NORMAL)

    def see_user_list(self) -> None:
        """Look up and display the first 10 AD users returned."""
        self.check_button.configure(state=tk.DISABLED)
        self.user_list_button.configure(state=tk.DISABLED)
        self.demo_reset_button.configure(state=tk.DISABLED)
        self.user_lookup_button.configure(state=tk.DISABLED)
        self.set_results("Getting the first 10 users...")
        self.root.update_idletasks()

        try:
            users = run_user_list_lookup()
            self.set_results(format_user_list(users))
        except RuntimeError as exc:
            logging.exception("Could not complete AD user list lookup.")
            self.set_results(str(exc))
        finally:
            self.check_button.configure(state=tk.NORMAL)
            self.user_list_button.configure(state=tk.NORMAL)
            self.demo_reset_button.configure(state=tk.NORMAL)
            self.user_lookup_button.configure(state=tk.NORMAL)

    def open_demo_reset_popup(self) -> None:
        """Open a demo-only password reset popup with no backend action."""
        popup = tk.Toplevel(self.root)
        popup.title("Demo Password Reset")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text="Username:").grid(row=0, column=0, padx=12, pady=(12, 6), sticky="e")
        username_entry = tk.Entry(popup, width=32)
        username_entry.grid(row=0, column=1, padx=12, pady=(12, 6))

        tk.Label(popup, text="MyPassword:").grid(row=1, column=0, padx=12, pady=6, sticky="e")
        password_entry = tk.Entry(popup, width=32, show="*")
        password_entry.grid(row=1, column=1, padx=12, pady=6)

        def submit_demo() -> None:
            self.set_results("Demo only - no changes made")
            popup.destroy()

        submit_button = tk.Button(popup, text="Submit", command=submit_demo, width=12)
        submit_button.grid(row=2, column=1, padx=12, pady=(8, 12), sticky="e")

        username_entry.focus_set()

    def open_user_lookup_popup(self) -> None:
        """Open a read-only user lookup popup."""
        popup = tk.Toplevel(self.root)
        popup.title("User Lookup")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text="Username:").grid(row=0, column=0, padx=12, pady=(12, 6), sticky="e")
        username_entry = tk.Entry(popup, width=32)
        username_entry.grid(row=0, column=1, padx=12, pady=(12, 6))

        def submit_lookup() -> None:
            username = username_entry.get().strip()
            popup.destroy()
            self.lookup_named_user(username)

        submit_button = tk.Button(popup, text="Submit", command=submit_lookup, width=12)
        submit_button.grid(row=1, column=1, padx=12, pady=(8, 12), sticky="e")

        username_entry.bind("<Return>", lambda _event: submit_lookup())
        username_entry.focus_set()

    def lookup_named_user(self, username: str) -> None:
        """Look up and display a specific AD user's details."""
        self.check_button.configure(state=tk.DISABLED)
        self.user_list_button.configure(state=tk.DISABLED)
        self.demo_reset_button.configure(state=tk.DISABLED)
        self.user_lookup_button.configure(state=tk.DISABLED)
        self.set_results("Looking up the user...")
        self.root.update_idletasks()

        try:
            user_info = run_named_user_lookup(username)
            self.set_results(format_named_user_results(user_info))
        except RuntimeError as exc:
            logging.exception("Could not complete named AD user lookup.")
            self.set_results(str(exc))
        finally:
            self.check_button.configure(state=tk.NORMAL)
            self.user_list_button.configure(state=tk.NORMAL)
            self.demo_reset_button.configure(state=tk.NORMAL)
            self.user_lookup_button.configure(state=tk.NORMAL)


def main() -> None:
    """Start the Tkinter app."""
    configure_logging()
    root = tk.Tk()
    MyAdLoginCheckApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
