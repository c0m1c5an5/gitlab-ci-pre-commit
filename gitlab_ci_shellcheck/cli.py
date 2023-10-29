# ruff: noqa: C901, PLR0911, PLR0912, PLR0915
# C901 `main` is too complex
# PLR0911 Too many return statements
# PLR0912 Too many branches
# PLR0915 Too many statements

import argparse
import logging
import os
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

logging.basicConfig(format="%(levelname)s: %(filename)s:%(lineno)d %(message)s")
logger = logging.getLogger(__name__)


def cli(argv: list[str] = sys.argv[1:]) -> int:
    """GitLab CI shellcheck cli.

    Args:
        argv (List[str], optional): Input arguments. Defaults to sys.argv[1:].

    Returns:
        int: Return code.
    """
    parser = argparse.ArgumentParser(
        description="ShelllCheck gitlab-ci formatted yaml file.",
        prog="gitlab-ci-fmt",
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
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="verbose output"
    )

    args = parser.parse_args(argv)
    files: List[Path] = args.files
    color: bool = args.color
    severity = args.severity
    verbose: bool = args.verbose

    if verbose or os.environ.get("DEBUG") not in [None, "false", "no", "0"]:
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Args: {args._get_kwargs()}")

    try:
        check_shellcheck()
    except ShellcheckNotFoundError as e:
        logger.error(f"Shellcheck check failed: {e!s}")
        return 1

    with TemporaryDirectory() as temp_dir_a:
        temp_dir = Path(temp_dir_a)
        file_map = {}

        logger.debug(f"Temporary directory path: {temp_dir!s}")

        for file in files:
            try:
                with file.open("r") as stream:
                    data = yaml.safe_load(stream)
            except YAMLError as e:
                error_message = str(e).replace("\n", "")
                logger.error(f"Failed load yaml file '{file!s}': {error_message}")
                return 1
            except OSError as e:
                logger.error(f"Failed to access '{file!s}': {e.strerror}")
                return 1

            logger.debug(f"Yaml data: {data!s}")

            if not isinstance(data, dict):
                logger.error(
                    f"Object type of '{file!s}' is '{type(data).__name__!s}', expected 'Dict'"
                )
                return 1

            for job_key, job in data.items():
                if isinstance(job, dict):
                    for script_key, script in job.items():
                        if script_key in ["before_script", "script", "after_script"]:
                            id = uuid.uuid4()
                            temp_file = temp_dir / str(id)

                            logger.debug(f"Temporary file path: {temp_file!s}")
                            logger.debug(f"Script: {script}")

                            try:
                                with temp_file.open("w") as tf:
                                    tf.write("\n".join(script))
                                    tf.flush()
                            except OSError as e:
                                logger.error(
                                    f"Failed to access '{file!s}': {e.strerror}"
                                )
                                return 1

                            mapping = f"{file}@{job_key}.{script_key}"
                            file_map[str(temp_file)] = mapping
                            logger.debug(f"File map entry: {temp_file!s} => {mapping}")

        shellcheck_files = set(file_map.keys())

        if not shellcheck_files:
            return 0

        cmd = [
            "shellcheck",
            f"-C{color}",
            f"--severity={severity}",
            "--",
            *shellcheck_files,
        ]

        logger.debug(f"Running command: {cmd}")

        process = subprocess.run(  # noqa: PLW1510
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
