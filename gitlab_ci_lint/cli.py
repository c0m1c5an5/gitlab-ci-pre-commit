# ruff: noqa: C901, PLR0911, PLR0912, PLR0915
# C901 `main` is too complex
# PLR0915 Too many statements
# PLR0911 Too many return statements
# PLR0912 Too many branches

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List

import git

from gitlab_ci_lint.utils import (
    check_pass,
    get_access_token,
    get_gitlab_project,
    lint_gitlab_api,
    remote_to_project,
)

logging.basicConfig(format="%(levelname)s: %(filename)s:%(lineno)d %(message)s")
logger = logging.getLogger(__name__)


def cli(argv: list[str] = sys.argv[1:]) -> int:
    """GitLab CI lint cli.

    Args:
        argv (List[str], optional): Input arguments. Defaults to sys.argv[1:].

    Returns:
        int: Return code.
    """
    parser = argparse.ArgumentParser(
        prog="gitlab-ci-lint", description="Lint gitlab-ci files."
    )
    parser.add_argument("files", nargs="+", type=Path, help="files to lint")
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="verbose output"
    )

    args = parser.parse_args(argv)
    files: List[Path] = args.files
    verbose: bool = args.verbose

    if verbose or os.environ.get("DEBUG") not in [None, "false", "no", "0"]:
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Args: {args._get_kwargs()}")

    try:
        check_pass()
    except Exception as e:
        logger.error(f"Pass check failed: {e!s}", exc_info=verbose)
        return 1

    try:
        repo = git.Repo(Path.cwd(), search_parent_directories=True)
    except Exception as e:
        logger.error(f"Failed to access git repo: {e!s}", exc_info=verbose)
        return 1

    logger.debug(f"Repo: {repo.working_dir}")

    try:
        origin = repo.remotes["origin"].url
    except IndexError:
        logger.error("Repository does not have an 'origin' remote", exc_info=verbose)
        return 1

    logger.debug(f"Origin url: {origin}")

    try:
        (gitlab_url, project_name) = remote_to_project(origin)
    except Exception as e:
        logger.error(f"Failed to parse git url: {e!s}", exc_info=verbose)
        return 1

    logger.debug(f"Gitlab URL: {gitlab_url}")
    logger.debug(f"Project name: {project_name}")

    try:
        token = get_access_token(gitlab_url)
    except Exception as e:
        logger.error(f"Failed to get access token: {e!s}", exc_info=verbose)
        return 1

    logger.debug(f"Access token: {token}")

    try:
        project = get_gitlab_project(gitlab_url, project_name, token)
    except Exception as e:
        logger.error(f"Failed to access gitlab project: {e!s}", exc_info=verbose)
        return 1

    for file in files:
        logger.debug(f"Linting file '{file}'")
        try:
            with file.open("r") as src_file:
                yml = src_file.read()
        except OSError as e:
            logger.error(f"Failed to access '{file!s}': {e.strerror}", exc_info=verbose)
            return 1
        except Exception as e:
            logger.error(f"Failed to access '{file!s}': {e!s}", exc_info=verbose)
            return 1

        try:
            lint_gitlab_api(project, yml)
        except Exception as e:
            logger.error(f"Linting of file '{file!s}' failed: {e!s}", exc_info=verbose)
            return 1
        else:
            logger.debug(f"Linting of file '{file}' successful", exc_info=verbose)

    return 0
