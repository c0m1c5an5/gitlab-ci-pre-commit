import re
import subprocess
from subprocess import CalledProcessError

from gitlab_ci_fmt.exceptions import FormatError, YqNotFoundError, YqVersionError

YQ_RE = re.compile(
    r"yq \(https:\/\/github.com\/mikefarah\/yq\/\) version v4.(0|[1-9]\d*).(0|[1-9]\d*)"
)


def check_yq() -> None:
    try:
        process = subprocess.run(
            ["yq", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            text=True,
            check=True,
        )
        stdout = process.stdout.strip()
        if not YQ_RE.match(stdout):
            raise YqVersionError("Yq version does not match regex")
    except CalledProcessError as e:
        stderr: str = e.stderr
        stderr = stderr.strip().encode("string_escape")
        raise YqNotFoundError(f"Command failed: {repr(stderr)}") from e


def yq_sort_keys(yml: str) -> str:
    """Get deterministic yaml string by sorting with yq

    Args:
        yml (str): yaml string to sort

    Returns:
        str: sorted yaml string
    """
    return subprocess.run(
        ["yq", "-P", "sort_keys(..)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=yml,
        universal_newlines=True,
        text=True,
        check=True,
    ).stdout


def yq_compare(src: str, dst: str) -> bool:
    """Compare two yaml string

    Args:
        src (str): Source yaml string
        dst (str): Target yaml string

    Returns:
        bool: True if yaml strings are equivalent
    """
    return yq_sort_keys(src) == yq_sort_keys(dst)


def yq_order_top_keys(yml: str) -> str:
    """Reorder top level keys

    Args:
        yml (str): yaml string

    Returns:
        str: Formatted yaml string
    """
    return subprocess.run(
        [
            "yq",
            '. |= pick(([ "workflow", "stages", "variables", "include", "default"] + keys) | unique)',
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=yml,
        universal_newlines=True,
        text=True,
        check=True,
    ).stdout


def yq_order_job_keys(yml: str) -> str:
    """Reorder job keys

    Args:
        yml (str): yaml string

    Returns:
        str: Formatted yaml string
    """
    return subprocess.run(
        [
            "yq",
            '.[] |= (select(tag == "!!map") | pick(([ "extends", "stage", "tags", "image", "services", "only", "except", "rules", "when", "dependencies", "secrets", "needs", "artifacts", "coverage", "dast_configuration", "pages", "environment", "release", "trigger", "retry", "timeout", "parallel", "allow_failure", "interruptible", "resource_group", "variables", "inherit", "cache", "before_script", "script", "after_script"] + keys) | unique))',  # noqa: E501
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=yml,
        universal_newlines=True,
        text=True,
        check=True,
    ).stdout


def format_gitlab_ci(yml: str) -> str:
    """Format gitlab-ci yaml string

    Args:
        yml (str): yaml string

    Raises:
        FormatError: When query fails to process
        FormatError: When formatting result is not equivalent to source

    Returns:
        str: Formatted yaml string
    """
    try:
        result = yq_order_top_keys(yml)
        result = yq_order_job_keys(result)
        if not yq_compare(yml, result):
            raise FormatError("Formatted result not equivalent to source")
    except CalledProcessError as e:
        stderr: str = e.stderr
        stderr = stderr.strip()
        raise FormatError(f"Query failed: {repr(stderr)}") from e

    return result
