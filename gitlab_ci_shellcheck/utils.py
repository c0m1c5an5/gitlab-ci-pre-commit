import subprocess
from subprocess import CalledProcessError

from gitlab_ci_shellcheck.exceptions import ShellcheckNotFoundError


def check_shellcheck() -> None:
    try:
        subprocess.run(
            ["shellcheck", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            text=True,
            check=True,
        )
    except CalledProcessError as e:
        stderr: str = e.stderr
        stderr = stderr.strip().encode("string_escape")
        raise ShellcheckNotFoundError(f"Command failed: {repr(stderr)}") from e
