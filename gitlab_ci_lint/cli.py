import argparse
import os
import sys
from pathlib import Path
from typing import List

import git
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from gitlab.exceptions import GitlabCiLintError

from gitlab_ci_lint.exceptions import GitlabProjectError, RemoteParseError
from gitlab_ci_lint.utils import get_gitlab_project, lint_gitlab_api, remote_to_project


def cli(argv: list[str] = sys.argv[1:]) -> int:
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
        print("Error: GitLab token not provided", file=sys.stderr)
        print(
            "Use GCL_PERSONAL_ACCESS_TOKEN environment variable or -t/--token tag",
            file=sys.stderr,
        )
        return 1

    try:
        workdir = os.getcwd()
        repo = git.Repo(workdir, search_parent_directories=True)
    except (InvalidGitRepositoryError, NoSuchPathError):
        print(f"Error: '{workdir}' is not a valid git repository", file=sys.stderr)
        return 1

    try:
        origin = repo.remotes["origin"].url
    except IndexError:
        print("Error: Repository does not have an 'origin' remote", file=sys.stderr)
        return 1

    try:
        (gitlab_url, project) = remote_to_project(origin)
    except RemoteParseError as e:
        print(f"Error: Unable to get GitLab host: {str(e)}", file=sys.stderr)

    try:
        project = get_gitlab_project(gitlab_url, project, token)
    except GitlabProjectError as e:
        print(f"Error: GitLab api unavailable: {str(e)}", file=sys.stderr)
        return 1

    for file in files:
        try:
            with file.open("r") as src_file:
                yml = src_file.read()
        except OSError as e:
            print(
                f"Error: Failed to read file '{str(file)}': {e.strerror}",
                file=sys.stderr,
            )
            return 1

        try:
            lint_gitlab_api(project, yml)
        except GitlabCiLintError as e:
            print(
                f"Error: Linting of file '{str(file)}' failed: {e.error_message}",
                file=sys.stderr,
            )
            return 1

    return 0
