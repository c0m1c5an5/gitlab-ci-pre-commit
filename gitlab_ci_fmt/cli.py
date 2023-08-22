import argparse
import sys
from pathlib import Path
from typing import List

from gitlab_ci_fmt.exceptions import FormatError, YqNotFoundError, YqVersionError
from gitlab_ci_fmt.utils import check_yq, format_gitlab_ci


def cli(argv: List[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description="Format gitlab-ci files.", prog=__package__
    )
    parser.add_argument("files", nargs="+", type=Path, help="files to format")
    args = parser.parse_args(argv)

    files: List[Path] = args.files

    try:
        check_yq()
    except YqNotFoundError as e:
        print(f"Error: yq not found: {str(e)}", file=sys.stderr)
        print("Use yq v4.x.x (https://github.com/mikefarah/yq)", file=sys.stderr)
        return 1
    except YqVersionError as e:
        print(f"Error: yq version incompatible: {str(e)}", file=sys.stderr)
        print("Use yq v4.x.x (https://github.com/mikefarah/yq)", file=sys.stderr)
        return 1

    for file in files:
        try:
            with file.open("r") as f:
                source = f.read()
        except OSError as e:
            print(
                f"Error: Failed to read file '{str(file)}': {e.strerror}",
                file=sys.stderr,
            )
            return 1

        try:
            result = format_gitlab_ci(source)
        except FormatError as e:
            print(
                f"Error: Failed to format file '{str(file)}': {str(e)}", file=sys.stderr
            )
            return 1

        try:
            if result != source:
                with file.open("w") as f:
                    f.write(result)
        except OSError as e:
            print(
                f"Error: Failed to write file '{str(file)}': {e.strerror}",
                file=sys.stderr,
            )
            return 1

    return 0
