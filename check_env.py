"""Print a safe API-key prefix and the SEC User-Agent from the local .env."""

from pathlib import Path
import sys


def read_env(path: Path) -> dict[str, str]:
    """Read simple KEY=value entries without requiring an extra package."""
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def main() -> int:
    env_path = Path(".env")
    if not env_path.is_file():
        print("Error: .env is missing. Run this program from the project folder.")
        return 1

    values = read_env(env_path)
    api_key = values.get("API_KEY") or values.get("PURDUE_GENAI_API_KEY", "")
    user_agent = values.get("SEC_USER_AGENT", "")

    if not api_key:
        print("Error: API_KEY is empty. Add your key to .env locally; do not share it.")
        return 1
    if not user_agent:
        print("Error: SEC_USER_AGENT is empty. Add your name and Purdue email to .env.")
        return 1

    print(f"API_KEY: {api_key[:4]}...")
    print(f"SEC_USER_AGENT: {user_agent}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
