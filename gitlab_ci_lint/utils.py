from typing import Tuple

import gitlab
import gitlab.exceptions
import giturlparse
from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError
from gitlab.v4.objects import Project as GitlabProject

from gitlab_ci_lint.exceptions import GitlabProjectError, RemoteParseError


def remote_to_project(remote: str) -> Tuple[str, str]:
    """Parse git remote to host url and project path

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
        raise RemoteParseError(f"Failed to parse remote '{remote}' as git url")


def get_gitlab_project(gitlab_url: str, project: str, token: str) -> GitlabProject:
    """Get GitLab project api object

    Args:
        gitlab_url (str): GitLab http api url
        project (str): GitLab project path
        token (str): Private access token

    Raises:
        GitlabProjectError: _description_
        GitlabProjectError: _description_
        RemoteParseError: _description_

    Returns:
        GitlabProject: _description_
    """
    gitlab_server = gitlab.Gitlab(gitlab_url, private_token=token)

    try:
        gitlab_project = gitlab_server.projects.get(project, lazy=True)
    except GitlabAuthenticationError as e:
        raise GitlabProjectError(
            f"Failed to authenticate with '{gitlab_url}': {e.error_message}"
        ) from e
    except GitlabGetError as e:
        raise GitlabProjectError(
            f"GET request to '{gitlab_url}' failed: {e.error_message}"
        ) from e
    return gitlab_project


def lint_gitlab_api(project: GitlabProject, yml: str) -> None:
    """Lint yaml string using GitLab api

    Args:
        project (GitlabProject): GitLab project object
        yml (str): yaml string
    """
    project.ci_lint.validate({"content": yml, "dry_run": True})
