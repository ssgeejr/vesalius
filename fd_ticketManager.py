"""Validate Freshdesk credentials stored in the user's home directory.

The script reads ``~/.freshdesk/api.key`` on Windows or any platform where
``Path.home()`` resolves to the user's home directory. It verifies that every
expected credential key exists and has a non-empty value. Secret values are
never printed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import requests


VERSION = "1.0"
REQUEST_TIMEOUT_SECONDS = 30


class FreshdeskCredentialFile:
    """Reads and parses the Freshdesk credential file."""

    def __init__(self, credential_path: Path | None = None) -> None:
        """Initialize the credential file reader.

        Args:
            credential_path: Optional explicit path for testing. When omitted,
                the reader uses ``~/.freshdesk/api.key``.
        """
        self.credential_path = credential_path or Path.home() / ".freshdesk" / "api.key"

    def read_text(self) -> str:
        """Read the credential file as text.

        Returns:
            The raw file contents.

        Raises:
            OSError: If the file is missing or cannot be read.
        """
        return self.credential_path.read_text(encoding="utf-8")

    def parse(self) -> dict[str, str]:
        """Parse key/value credentials from the credential file.

        Returns:
            A dictionary containing credential names and their values.
        """
        credentials: dict[str, str] = {}

        for line in self.read_text().splitlines():
            stripped_line = line.strip()

            if not stripped_line or stripped_line.startswith("#"):
                continue

            separator = ":" if ":" in stripped_line else "=" if "=" in stripped_line else ""
            if not separator:
                continue

            key, value = stripped_line.split(separator, maxsplit=1)
            credentials[key.strip()] = value.strip()

        return credentials


class FreshdeskCredentialPrinter:
    """Prints credential status without revealing secret values."""

    def __init__(self, credentials: dict[str, str], required_keys: tuple[str, ...]) -> None:
        """Initialize the credential printer.

        Args:
            credentials: Parsed credential key/value pairs.
            required_keys: Credential keys expected by the application.
        """
        self.credentials = credentials
        self.required_keys = required_keys

    def print_masked(self) -> None:
        """Print each credential key with a safe, non-secret value display."""
        for key in self.required_keys:
            value = self.credentials.get(key, "").strip()
            display_value = self._display_value(key, value)
            print(f"{key}: {display_value}")

    def _display_value(self, key: str, value: str) -> str:
        """Return a safe value display for a credential key."""
        if not value:
            return "[missing]"

        if key == "api_key":
            return self._mask_api_key(value)

        return "[set]"

    @staticmethod
    def _mask_api_key(value: str) -> str:
        """Mask an API key, showing only the last four characters."""
        if len(value) <= 4:
            return "********"

        return f"********{value[-4:]}"


class FreshdeskCredentialValidator:
    """Validates that required Freshdesk credential keys are populated."""

    REQUIRED_KEYS = (
        "api_key",
        "domain",
        "email",
        "agent_id",
        "location",
        "group_id",
        "dept_id",
        "resp_id",
        "contact_nbr",
    )

    def __init__(self, credential_file: FreshdeskCredentialFile) -> None:
        """Initialize the validator.

        Args:
            credential_file: The credential file reader to validate.
        """
        self.credential_file = credential_file

    def has_all_required_values(self) -> bool:
        """Return True when all required keys are present and non-empty."""
        try:
            credentials = self.credential_file.parse()
        except OSError:
            return False

        return self.credentials_are_complete(credentials)

    def credentials_are_complete(self, credentials: dict[str, str]) -> bool:
        """Return True when parsed credentials include all required values."""
        return all(credentials.get(key, "").strip() for key in self.REQUIRED_KEYS)


class FreshserviceClient:
    """Client for Freshservice API calls."""

    def __init__(self, api_key: str, domain: str) -> None:
        """Initialize the Freshservice API client.

        Args:
            api_key: Freshservice API key.
            domain: Freshservice company domain.
        """
        self.api_key = api_key
        self.domain = domain

    def get_current_agent(self) -> dict[str, Any]:
        """Fetch the current agent record from Freshservice.

        Returns:
            Parsed JSON response from the Freshservice API.

        Raises:
            requests.RequestException: If the request fails.
            ValueError: If the API response is not valid JSON.
        """
        response = requests.get(
            self.current_agent_url,
            auth=(self.api_key, "X"),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()

    def search_tickets_by_agent(self, agent_id: str) -> dict[str, Any]:
        """Search Freshservice tickets assigned to an agent.

        Args:
            agent_id: Freshservice agent ID from the credential file.

        Returns:
            Parsed JSON response from the Freshservice API.

        Raises:
            requests.RequestException: If the request fails.
            ValueError: If the API response is not valid JSON.
        """
        response = requests.get(
            self.ticket_search_url,
            auth=(self.api_key, "X"),
            params={
                "query": f'"agent_id:{agent_id}"',
                "per_page": 1,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()

    def create_ticket(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a Freshservice ticket.

        Args:
            payload: JSON payload for the Freshservice create-ticket API.

        Returns:
            Parsed JSON response from the Freshservice API.

        Raises:
            requests.RequestException: If the request fails.
            ValueError: If the API response is not valid JSON.
        """
        response = requests.post(
            self.tickets_url,
            auth=(self.api_key, "X"),
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()

    @property
    def current_agent_url(self) -> str:
        """Return the Freshservice current-agent endpoint URL."""
        return f"{self.base_url}/api/v2/agents/me"

    @property
    def ticket_search_url(self) -> str:
        """Return the Freshservice ticket search endpoint URL."""
        return f"{self.base_url}/api/v2/tickets/filter"

    @property
    def tickets_url(self) -> str:
        """Return the Freshservice tickets endpoint URL."""
        return f"{self.base_url}/api/v2/tickets"

    @property
    def base_url(self) -> str:
        """Return the Freshservice base URL."""
        domain = self.domain.strip()

        if domain.startswith("http://") or domain.startswith("https://"):
            return domain.rstrip("/")

        return f"https://{domain}.freshservice.com"


class SafeFreshserviceResponsePrinter:
    """Prints API results without exposing credentials or personal details."""

    REDACTED_KEYS = {
        "address",
        "agent_id",
        "api_key",
        "contact_number",
        "description",
        "description_text",
        "email",
        "employeeid",
        "external_id",
        "first_name",
        "id",
        "job_title",
        "last_name",
        "location",
        "location_id",
        "mobile_phone_number",
        "name",
        "phone",
        "phone_number",
        "reporting_manager_id",
        "signature",
        "subject",
        "work_phone_number",
        "work_schedule_id",
    }

    def __init__(self, api_key: str, domain: str, url: str) -> None:
        """Initialize the safe response printer.

        Args:
            api_key: Freshservice API key to mask in command output.
            domain: Freshservice domain to include in the filled-in URL.
            url: Freshservice URL called by the client.
        """
        self.api_key = api_key
        self.domain = domain
        self.url = url

    def print_filled_curl(self) -> None:
        """Print the equivalent curl command with the API key masked."""
        masked_api_key = FreshdeskCredentialPrinter._mask_api_key(self.api_key)
        display_url = self._mask_url_domain()
        print("Filled curl command:")
        print(f"curl -u '{masked_api_key}:X' '{display_url}'")

    def print_agent_ticket_search_curl(self, agent_id: str) -> None:
        """Print the ticket-search curl command with secret values masked."""
        masked_api_key = FreshdeskCredentialPrinter._mask_api_key(self.api_key)
        display_url = (
            f"{self._mask_url_domain()}?"
            'query="agent_id:[agent_id]"&per_page=1'
        )
        print("Filled curl command:")
        print(f"curl -s -u '{masked_api_key}:X' '{display_url}'")

    def print_create_ticket_curl(self) -> None:
        """Print the create-ticket curl command with secret values masked."""
        masked_api_key = FreshdeskCredentialPrinter._mask_api_key(self.api_key)
        display_url = self._mask_url_domain()
        print("Filled curl command:")
        print(
            "curl -s "
            f'-u "{masked_api_key}:X" '
            '-H "Content-Type: application/json" '
            "-d '[redacted ticket payload]' "
            f'"{display_url}"'
        )

    def print_response(self, response_data: dict[str, Any]) -> None:
        """Print a redacted API response."""
        print("Redacted API result:")
        self._print_value(response_data)

    def print_redacted_json(self, response_data: dict[str, Any]) -> None:
        """Print a jq-style JSON response with sensitive fields redacted."""
        print("Redacted JSON result:")
        print(json.dumps(self._redact_value(response_data), indent=2))

    def _print_value(self, value: Any, indent: int = 0, key_name: str = "") -> None:
        """Print a value with sensitive fields redacted."""
        prefix = " " * indent

        if isinstance(value, dict):
            for key, child_value in value.items():
                if key in self.REDACTED_KEYS:
                    print(f"{prefix}{key}: [redacted]")
                    continue

                if isinstance(child_value, dict):
                    print(f"{prefix}{key}:")
                    self._print_value(child_value, indent + 2, key)
                elif isinstance(child_value, list):
                    print(f"{prefix}{key}: [list with {len(child_value)} item(s)]")
                else:
                    self._print_value(child_value, indent, key)
            return

        if isinstance(value, str) and self._looks_sensitive(key_name):
            print(f"{prefix}{key_name}: [redacted]")
            return

        if isinstance(value, int) and self._looks_sensitive(key_name):
            print(f"{prefix}{key_name}: [redacted]")
            return

        if key_name:
            print(f"{prefix}{key_name}: {value}")
        else:
            print(f"{prefix}{value}")

    def _looks_sensitive(self, key_name: str) -> bool:
        """Return True when a field name suggests personal or secret data."""
        lowered_key = key_name.lower()
        return any(
            word in lowered_key
            for word in ("email", "employee", "external", "id", "name", "phone", "token")
        )

    def _mask_url_domain(self) -> str:
        """Return the called URL with the configured Freshservice domain masked."""
        parsed_url = urlparse(self.url)
        masked_url = parsed_url._replace(netloc="[domain].freshservice.com")
        return urlunparse(masked_url)

    def _redact_value(self, value: Any, key_name: str = "") -> Any:
        """Return a copy of an API value with sensitive data redacted."""
        if key_name in self.REDACTED_KEYS or self._looks_sensitive(key_name):
            return "[redacted]"

        if isinstance(value, dict):
            return {
                key: self._redact_value(child_value, key)
                for key, child_value in value.items()
            }

        if isinstance(value, list):
            return [self._redact_value(child_value, key_name) for child_value in value]

        return value


class FreshdeskTicketManagerApp:
    """Command-line application for checking Freshdesk credentials."""

    def __init__(
        self,
        credential_file: FreshdeskCredentialFile,
        validator: FreshdeskCredentialValidator,
    ) -> None:
        """Initialize the application.

        Args:
            credential_file: The credential file reader used by the app.
            validator: Credential validator used by the app.
        """
        self.credential_file = credential_file
        self.validator = validator

    def run(self, args: argparse.Namespace) -> int:
        """Run the credential check and print the result.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code 0 when credentials are valid; otherwise 1.
        """
        if args.creds:
            return self._print_credentials()

        if args.mytickets:
            return self._print_my_tickets()

        if args.agent:
            return self._print_agent_tickets()

        if args.new:
            return self._create_new_ticket(args)

        if self.validator.has_all_required_values():
            print("[Success]")
            return 0

        print("[credential file corrupted]")
        return 1

    def _print_my_tickets(self) -> int:
        """Call the current-agent endpoint and print a safe result summary."""
        try:
            credentials = self.credential_file.parse()
        except OSError:
            print("[credential file corrupted]")
            return 1

        if not self.validator.credentials_are_complete(credentials):
            print("[credential file corrupted]")
            return 1

        client = FreshserviceClient(
            api_key=credentials["api_key"],
            domain=credentials["domain"],
        )
        printer = SafeFreshserviceResponsePrinter(
            api_key=credentials["api_key"],
            domain=credentials["domain"],
            url=client.current_agent_url,
        )
        printer.print_filled_curl()

        try:
            response_data = client.get_current_agent()
        except requests.HTTPError as error:
            self._print_safe_http_error(error)
            return 1
        except requests.RequestException:
            print("[Freshservice request failed] Network request failed")
            return 1
        except ValueError:
            print("[Freshservice request failed] API response was not valid JSON")
            return 1

        printer.print_response(response_data)
        print("[Success]")
        return 0

    def _print_agent_tickets(self) -> int:
        """Search tickets for the configured agent and print a safe result."""
        try:
            credentials = self.credential_file.parse()
        except OSError:
            print("[credential file corrupted]")
            return 1

        if not self.validator.credentials_are_complete(credentials):
            print("[credential file corrupted]")
            return 1

        client = FreshserviceClient(
            api_key=credentials["api_key"],
            domain=credentials["domain"],
        )
        printer = SafeFreshserviceResponsePrinter(
            api_key=credentials["api_key"],
            domain=credentials["domain"],
            url=client.ticket_search_url,
        )
        printer.print_agent_ticket_search_curl(credentials["agent_id"])

        try:
            response_data = client.search_tickets_by_agent(credentials["agent_id"])
        except requests.HTTPError as error:
            self._print_safe_http_error(error)
            return 1
        except requests.RequestException:
            print("[Freshservice request failed] Network request failed")
            return 1
        except ValueError:
            print("[Freshservice request failed] API response was not valid JSON")
            return 1

        printer.print_redacted_json(response_data)
        print("[Success]")
        return 0

    def _create_new_ticket(self, args: argparse.Namespace) -> int:
        """Create a new Freshservice ticket from CLI arguments."""
        if not args.subject or not args.description:
            print("[new ticket missing required arguments] --subject and --description are required")
            return 1

        try:
            credentials = self.credential_file.parse()
        except OSError:
            print("[credential file corrupted]")
            return 1

        if not self.validator.credentials_are_complete(credentials):
            print("[credential file corrupted]")
            return 1

        client = FreshserviceClient(
            api_key=credentials["api_key"],
            domain=credentials["domain"],
        )
        payload = self._build_new_ticket_payload(credentials, args.subject, args.description)
        printer = SafeFreshserviceResponsePrinter(
            api_key=credentials["api_key"],
            domain=credentials["domain"],
            url=client.tickets_url,
        )
        printer.print_create_ticket_curl()

        try:
            response_data = client.create_ticket(payload)
        except requests.HTTPError as error:
            self._print_safe_http_error(error)
            return 1
        except requests.RequestException:
            print("[Freshservice request failed] Network request failed")
            return 1
        except ValueError:
            print("[Freshservice request failed] API response was not valid JSON")
            return 1

        printer.print_redacted_json(response_data)
        print("[Success]")
        return 0

    @staticmethod
    def _build_new_ticket_payload(
        credentials: dict[str, str],
        subject: str,
        description: str,
    ) -> dict[str, Any]:
        """Build the Freshservice create-ticket payload."""
        return {
            "subject": subject,
            "description": description,
            "email": credentials["email"],
            "workspace_id": 2,
            "status": 2,
            "source": 3,
            "priority": 2,
            "impact": 1,
            "urgency": 1,
            "group_id": int(credentials["group_id"]),
            "responder_id": int(credentials["resp_id"]),
            "department_id": int(credentials["dept_id"]),
            "custom_fields": {
                "location": credentials["location"],
                "contact_number": credentials["contact_nbr"],
            },
        }

    @staticmethod
    def _print_safe_http_error(error: requests.HTTPError) -> None:
        """Print HTTP error details without exposing URLs or identifiers."""
        response = error.response

        if response is None:
            print("[Freshservice request failed] HTTP error")
            return

        reason = response.reason or "Request failed"
        print(f"[Freshservice request failed] HTTP {response.status_code}: {reason}")

    def _print_credentials(self) -> int:
        """Print masked credential status and return a validation exit code."""
        try:
            credentials = self.credential_file.parse()
        except OSError:
            print("[credential file corrupted]")
            return 1

        printer = FreshdeskCredentialPrinter(
            credentials,
            self.validator.REQUIRED_KEYS,
        )
        printer.print_masked()

        if self.validator.credentials_are_complete(credentials):
            print("[Success]")
            return 0

        print("[credential file corrupted]")
        return 1


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Validate Freshdesk credentials stored in ~/.freshdesk/api.key.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
        help="show the program version and exit",
    )
    parser.add_argument(
        "--creds",
        action="store_true",
        help="show credential status with the API key masked",
    )
    parser.add_argument(
        "--mytickets",
        action="store_true",
        help="call the Freshservice current-agent endpoint with masked output",
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="search tickets for the configured Freshservice agent",
    )
    parser.add_argument(
        "--new",
        action="store_true",
        help="create a new Freshservice ticket",
    )
    parser.add_argument(
        "--subject",
        help="subject for a new Freshservice ticket",
    )
    parser.add_argument(
        "--description",
        help="description for a new Freshservice ticket",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Create and run the Freshdesk ticket manager app."""
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    credential_file = FreshdeskCredentialFile()
    validator = FreshdeskCredentialValidator(credential_file)
    app = FreshdeskTicketManagerApp(credential_file, validator)
    return app.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
