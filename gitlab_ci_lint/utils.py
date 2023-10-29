import json
import re
import subprocess
import unicodedata
from subprocess import CalledProcessError
from typing import Tuple

import gitlab
import gitlab.exceptions
import giturlparse  # type: ignore
from gitlab.v4.objects import Project as GitlabProject

from gitlab_ci_lint.exceptions import (
    CommandError,
    InvalidGitUrlError,
    PassNotFoundError,
)


def slugify(value: str, allow_unicode: bool = False) -> str:
    """Slugify string.

    Args:
        value (str): String to sugify.
        allow_unicode (bool, optional): Allow unicode. Defaults to False.

    Returns:
        str: Slugified string.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "-", value.lower()).strip()
    return re.sub(r"[-\s]+", "-", value)


def check_pass() -> None:
    """Check if pass in PATH.

    Raises:
        PassNotFoundError: Pass not in PATH.
    """
    try:
        subprocess.run(
            ["pass", "--version"],
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
        raise PassNotFoundError(stderr) from e


def get_access_token(url: str) -> str:
    """Get gitlab access token from pass.

    Args:
        url (str): Gitlab host url.

    Raises:
        CommandError: When pass returns an error.

    Returns:
        str: Personal access token.
    """
    url_slug = slugify(url)

    try:
        show_output = subprocess.run(
            ["pass", "show", "--", f"gitlab-ci-lint/{url_slug}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            universal_newlines=True,
            text=True,
            check=True,
        )
        token = show_output.stdout.strip()
    except CalledProcessError as e:
        stderr: str = e.stderr
        stderr = json.dumps(stderr.strip())
        raise CommandError(stderr) from e
    else:
        return token


def remote_to_project(remote: str) -> Tuple[str, str]:
    """Parse git remote to host url and project path.

    Args:
        remote (str): Git remote.

    Raises:
        RemoteParseError: When remote parsing fails.

    Returns:
        Tuple[str, str]: Host url and project path.
    """
    parsed_url = giturlparse.parse(remote)
    if parsed_url.valid:
        project_path: str = parsed_url.pathname
        project_path = project_path.removeprefix("/").removesuffix(".git")
        host_url = "https://" + parsed_url.host
        return (host_url, project_path)
    else:
        raise InvalidGitUrlError(remote)


def get_gitlab_project(gitlab_url: str, project: str, token: str) -> GitlabProject:
    """Get GitLab project api object.

    Args:
        gitlab_url (str): GitLab http api url.
        project (str): GitLab project path.
        token (str): Private access token.

    Raises:
        GitlabAuthenticationError: When authentication fails.
        GitlabProjectError: When unable to acquire the project.


    Returns:
        GitlabProject: Gitlab project.
    """
    gitlab_server = gitlab.Gitlab(gitlab_url, private_token=token)
    gitlab_project = gitlab_server.projects.get(project, lazy=True)
    return gitlab_project


def lint_gitlab_api(project: GitlabProject, yml: str) -> None:
    """Lint yaml string using GitLab api.

    Args:
        project (GitlabProject): GitLab project.
        yml (str): Yaml pipeline.

    Raises:
        GitlabCiLintError: When linting fails.
    """
    project.ci_lint.validate({"content": yml})
