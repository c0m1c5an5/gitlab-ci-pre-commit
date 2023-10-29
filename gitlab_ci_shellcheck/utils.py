import json
import subprocess
from subprocess import CalledProcessError

from gitlab_ci_shellcheck.exceptions import ShellcheckNotFoundError


def check_shellcheck() -> None:
    """Check if shellcheck in PATH.

    Raises:
        ShellcheckNotFoundError: Shellcheck not in PATH.
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
        stderr = json.dumps(stderr.strip())
        raise ShellcheckNotFoundError(stderr) from e
