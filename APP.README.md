# My AD Login Check

My AD Login Check is a tiny local Windows desktop app. It lets the currently signed-in Windows user click one button and see basic read-only Active Directory login information in plain English.

## What It Shows

- Current Windows username
- AD display name, if available
- Last logon timestamp, if available
- Bad password count, if available
- Account locked status, if available
- First 10 Active Directory users returned by AD, when requested
- Read-only lookup details for an entered username, when requested
- A demo-only password reset popup that makes no account changes
- AD timestamps are shown in Central Time

## Safety

- Read-only only
- No account unlocks
- No account changes
- The password reset popup is only a demo and has no reset backend
- No cloud APIs
- No external AI APIs
- No command entry box
- The login check only checks the currently logged-in Windows user
- The user list check is read-only and limited to 10 users
- The user lookup check is read-only and shows only available AD fields
- App errors are written only to `my_ad_login_check.log`

## Requirements

- Windows
- Python 3
- Tkinter, which is included with most Python for Windows installs
- Microsoft Active Directory PowerShell tools installed on the workstation

If the Active Directory tools are not installed, the app shows:

```text
This workstation does not have the AD tools installed.
```

## How To Run

From this folder, run:

```powershell
python app.py
```

Then click **Check My Login**.

To see a short read-only user list, click **See User List (First 10)**.

To look up one AD user, click **User Lookup**, enter a username, and click **Submit**. The app shows available details such as display name, locked/unlocked status, last login, bad password count, and password last set. If a last computer login is not available from the user record, the app says so.

To try the demo-only password reset popup, click **Demo Password Reset**, enter sample text, and click **Submit**. The app will show:

```text
Demo only - no changes made
```
