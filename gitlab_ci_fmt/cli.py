import argparse
import sys
from pathlib import Path
from typing import List

from gitlab_ci_fmt.exceptions import Error
from gitlab_ci_fmt.utils import check_yq, format_gitlab_ci, print_err


def cli(argv: List[str] = sys.argv[1:]) -> int:
    """GitLab CI format cli.

    Args:
        argv (List[str], optional): Input arguments. Defaults to sys.argv[1:].

    Returns:
        int: Return code
    """
    parser = argparse.ArgumentParser(
        description="Format gitlab-ci files.", prog=__package__
    )
    parser.add_argument("files", nargs="+", type=Path, help="files to format")
    args = parser.parse_args(argv)

    files: List[Path] = args.files

    try:
        check_yq()
    except Error as e:
        print_err(f"Error: yq not found: {e!s}")
        print_err("Use yq v4.x.x (https://github.com/mikefarah/yq)")
        return 1

    for file in files:
        try:
            with file.open("r") as f:
                source = f.read()
        except OSError as e:
            print_err(f"Error: Failed to read file '{file!s}': {e.strerror}")
            return 1

        try:
            result = format_gitlab_ci(source)
        except Error as e:
            print_err(f"Error: Failed to format file '{file!s}': {e!s}")
            return 1

        try:
            if result != source:
                with file.open("w") as f:
                    f.write(result)
        except OSError as e:
            print_err(f"Error: Failed to write file '{file!s}': {e.strerror}")
            return 1

    return 0
