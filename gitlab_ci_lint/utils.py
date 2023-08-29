import sys
from typing import Tuple

import gitlab
import gitlab.exceptions
import giturlparse
from gitlab.v4.objects import Project as GitlabProject

from gitlab_ci_lint.exceptions import RemoteParseError


def print_err(message: str) -> None:
    """Print to stderr.

    Args:
        message (str): Message to print
    """
    print(message, file=sys.stderr)


def remote_to_project(remote: str) -> Tuple[str, str]:
    """Parse git remote to host url and project path.

    Args:
        remote (str): git remote

    Raises:
        RemoteParseError: When remote parsing fails

    Returns:
        Tuple[str, str]: Host url and project path
    """
    parsed_url = giturlparse.parse(remote)
    if parsed_url.valid:
        project_path: str = parsed_url.pathname
        project_path = project_path.removeprefix("/").removesuffix(".git")
        host_url = "https://" + parsed_url.host
        return (host_url, project_path)
    else:
        raise RemoteParseError(remote)


def get_gitlab_project(gitlab_url: str, project: str, token: str) -> GitlabProject:
    """Get GitLab project api object.

    Args:
        gitlab_url (str): GitLab http api url
        project (str): GitLab project path
        token (str): Private access token

    Raises:
        GitlabAuthenticationError: _description_
        GitlabProjectError: _description_


    Returns:
        GitlabProject: _description_
    """
    gitlab_server = gitlab.Gitlab(gitlab_url, private_token=token)
    gitlab_project = gitlab_server.projects.get(project, lazy=True)
    return gitlab_project


def lint_gitlab_api(project: GitlabProject, yml: str) -> None:
    """Lint yaml string using GitLab api.

    Args:
        project (GitlabProject): GitLab project object
        yml (str): yaml string
    """
    project.ci_lint.validate({"content": yml, "dry_run": True})
