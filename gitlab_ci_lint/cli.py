# ruff: noqa: C901, PLR0911, PLR0912
# C901 `main` is too complex
# PLR0911 Too many return statements
# PLR0912 Too many branches

import argparse
import os
import sys
from pathlib import Path
from typing import List

import git
import git.exc
import gitlab.exceptions

from gitlab_ci_lint.exceptions import Error
from gitlab_ci_lint.utils import (
    get_gitlab_project,
    lint_gitlab_api,
    print_err,
    remote_to_project,
)


def cli(argv: list[str] = sys.argv[1:]) -> int:
    """GitLab CI lint cli.

    Args:
        argv (List[str], optional): Input arguments. Defaults to sys.argv[1:].

    Returns:
        int: Return code
    """
    sys.tracebacklimit = 0
    parser = argparse.ArgumentParser(
        description="Lint gitlab-ci files.", prog=__package__
    )
    parser.add_argument("files", nargs="+", type=Path, help="files to lint")
    parser.add_argument(
        "-t", "--token", type=str, required=False, help="gitlab personal access token"
    )
    args = parser.parse_args(argv)
    files: List[Path] = args.files

    if args.token:
        token = args.token
    elif os.environ.get("GCL_PERSONAL_ACCESS_TOKEN"):
        token = os.environ.get("GCL_PERSONAL_ACCESS_TOKEN")
    else:
        print_err("Error: GitLab token not provided")
        print_err(
            "Use GCL_PERSONAL_ACCESS_TOKEN environment variable or -t/--token tag"
        )
        return 1

    try:
        workdir = Path.cwd()
        repo = git.Repo(workdir, search_parent_directories=True)
    except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
        print_err(f"Error: '{workdir}' is not a valid git repository")
        return 1

    try:
        origin = repo.remotes["origin"].url
    except IndexError:
        print_err("Error: Repository does not have an 'origin' remote")
        return 1

    try:
        (gitlab_url, project) = remote_to_project(origin)
    except Error as e:
        print_err(f"Error: Unable to get GitLab host: {e!s}")
        return 1

    try:
        project = get_gitlab_project(gitlab_url, project, token)
    except gitlab.exceptions.GitlabAuthenticationError as e:
        print_err(
            f"Error: Failed to authenticate with '{gitlab_url}': {e.error_message}"
        )
        return 1
    except gitlab.exceptions.GitlabGetError as e:
        print_err(f"Error: GET request to '{gitlab_url}' failed: {e.error_message}")
        return 1

    for file in files:
        try:
            with file.open("r") as src_file:
                yml = src_file.read()
        except OSError as e:
            print_err(f"Error: Failed to read file '{file!s}': {e.strerror}")
            return 1

        try:
            lint_gitlab_api(project, yml)
        except gitlab.exceptions.GitlabCiLintError as e:
            print_err(f"Error: Linting of file '{file!s}' failed: {e.error_message}")
            return 1

    return 0
