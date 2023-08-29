import subprocess
import sys
from subprocess import CalledProcessError

from gitlab_ci_shellcheck.exceptions import ShellcheckNotFoundError


def print_err(message: str) -> None:
    """Print to stderr.

    Args:
        message (str): Message to print
    """
    print(message, file=sys.stderr)


def check_shellcheck() -> None:
    """Check if shellcheck in PATH.

    Raises:
        ShellcheckNotFoundError: Shellcheck not in PATH
    """
    try:
        subprocess.run(
            ["shellcheck", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            universal_newlines=True,
            text=True,
            check=True,
        )
    except CalledProcessError as e:
        stderr: str = e.stderr
        stderr = stderr.strip().encode("string_escape")
        raise ShellcheckNotFoundError(e.returncode, stderr) from e
