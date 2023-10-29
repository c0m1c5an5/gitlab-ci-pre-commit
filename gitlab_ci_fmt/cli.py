import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List

from gitlab_ci_fmt.exceptions import CommandError, MalformedError
from gitlab_ci_fmt.utils import check_yq, format_gitlab_ci

logging.basicConfig(format="%(levelname)s: %(filename)s:%(lineno)d %(message)s")
logger = logging.getLogger(__name__)


def cli(argv: List[str] = sys.argv[1:]) -> int:
    """GitLab CI format cli.

    Args:
        argv (List[str], optional): Input arguments. Defaults to sys.argv[1:].

    Returns:
        int: Return code.
    """
    parser = argparse.ArgumentParser(
        description="Format gitlab-ci files.",
        prog="gitlab-ci-fmt",
    )
    parser.add_argument("files", nargs="+", type=Path, help="files to format")
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
        check_yq()
    except CommandError as e:
        logger.error(f"yq check failed: {e!s}")
        return 1

    for file in files:
        logger.debug(f"Formatting file: {file}")
        try:
            with file.open("r") as f:
                source = f.read()
        except OSError as e:
            logger.error(f"Failed to access '{file!s}': {e.strerror}")
            return 1

        try:
            result = format_gitlab_ci(source)
        except (CommandError, MalformedError) as e:
            logger.error(f"Failed to format file '{file!s}': {e!s}")
            return 1

        logger.debug(f"Formatting result:\n{result}")

        try:
            if result != source:
                with file.open("w") as f:
                    f.write(result)
        except OSError as e:
            logger.error(f"Failed to access '{file!s}': {e.strerror}")
            return 1

    return 0
