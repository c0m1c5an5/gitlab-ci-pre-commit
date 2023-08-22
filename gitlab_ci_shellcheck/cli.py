import argparse
import subprocess
import sys
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import yaml
from yaml import YAMLError

from gitlab_ci_shellcheck.exceptions import ShellcheckNotFoundError
from gitlab_ci_shellcheck.utils import check_shellcheck


def cli(argv: list[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description="ShelllCheck gitlab-ci formatted yaml file.", prog=__package__
    )

    parser.add_argument(
        "files",
        type=Path,
        nargs="+",
        default=[".gitlab-ci.yml"],
        help="files to check",
    )

    parser.add_argument(
        "-S",
        "--severity",
        type=str,
        default="warning",
        choices=["error", "warning", "info", "style"],
        help="minimum severity of errors to consider",
    )

    parser.add_argument(
        "-C",
        "--color",
        type=str,
        default="always",
        choices=["auto", "always", "never"],
        help="use color",
    )

    args = parser.parse_args(argv)
    files: List[Path] = args.files
    color: bool = args.color
    severity = args.severity

    try:
        check_shellcheck()
    except ShellcheckNotFoundError as e:
        print(f"Error: shellcheck not found: {str(e)}", file=sys.stderr)
        print(
            "Install shellcheck (https://github.com/koalaman/shellcheck)",
            file=sys.stderr,
        )
        return 1

    with TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        file_map = dict()

        for file in files:
            try:
                with open(file, "r") as stream:
                    data = yaml.safe_load(stream)
            except YAMLError as e:
                print(
                    f"Error: Failed load yaml file '{str(file)}':\n{str(e)}",
                    file=sys.stderr,
                )
                return 1
            except OSError as e:
                print(
                    f"Error: Failed to read file '{str(file)}': {e.strerror}",
                    file=sys.stderr,
                )
                return 1

            if type(data) != dict:
                print(
                    f"Error: Object type of '{str(file)}' is not Dict",
                    file=sys.stderr,
                )
                return 1

            for job_key, job in data.items():
                if type(job) is dict:
                    for script_key, script in job.items():
                        if script_key in ["before_script", "script", "after_script"]:
                            id = uuid.uuid4()
                            temp_file = temp_dir_path / str(id)

                            try:
                                with temp_file.open("w") as tf:
                                    tf.write("\n".join(script))
                                    tf.flush()
                            except OSError as e:
                                print(
                                    f"Error: Failed to write file '{str(temp_file)}': {e.strerror}",
                                    file=sys.stderr,
                                )
                                return 1

                            file_map[str(temp_file)] = f"{file}@{job_key}.{script_key}"

        shellcheck_files = [f for f in file_map.keys()]
        cmd = [
            "shellcheck",
            f"-C{color}",
            f"--severity={severity}",
            "--",
        ] + shellcheck_files

        process = subprocess.run(
            cmd, shell=False, capture_output=True, universal_newlines=True, text=True
        )

        message = str()
        if process.stderr:
            message += process.stderr

        if process.stdout:
            message += process.stdout

        if message:
            for k, v in file_map.items():
                message = message.replace(k, v)

        if process.returncode != 0:
            print(message, end="", file=sys.stderr)
            return 1

        return 0
