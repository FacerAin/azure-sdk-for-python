#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute mypy within a tox environment.

from subprocess import check_call, CalledProcessError
import argparse
import os
import logging
import sys

from ci_tools.environment_exclusions import (
    is_check_enabled, is_typing_ignored
)
from ci_tools.variables import in_ci
from gh_tools.vnext_issue_creator import create_vnext_issue


logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run mypy against target folder. ")

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to run mypy will be <target_package>/azure.",
        required=True,
    )

    parser.add_argument(
        "--next",
        default=False,
        help="Next version of mypy is being tested.",
        required=False 
    )

    args = parser.parse_args()
    package_name = os.path.basename(os.path.abspath(args.target_package))
    if not args.next and in_ci():
        if not is_check_enabled(args.target_package, "mypy", True) or is_typing_ignored(package_name):
            logging.info(
                f"Package {package_name} opts-out of mypy check. See https://aka.ms/python/typing-guide for information."
            )
            exit(0)

    commands = [
        sys.executable,
        "-m",
        "mypy",
        "--python-version",
        "3.7",
        "--show-error-codes",
        "--ignore-missing-imports",
    ]
    src_code = [*commands, os.path.join(args.target_package, "azure")]
    src_code_error = None
    sample_code_error = None
    try:
        logging.info(
            f"Running mypy commands on src code: {src_code}"
        )
        check_call(src_code)
    except CalledProcessError as src_err:
        src_code_error = src_err

    if not args.next and in_ci() and not is_check_enabled(args.target_package, "type_check_samples", True):
        logging.info(
            f"Package {package_name} opts-out of mypy check on samples."
        )
    else:
        sample_code = [
            *commands,
            "--check-untyped-defs",
            "--follow-imports=silent",
            os.path.join(args.target_package, "samples")
        ]
        try:
            logging.info(
                f"Running mypy commands on sample code: {sample_code}"
            )
            check_call(sample_code)
        except CalledProcessError as sample_err:
            sample_code_error = sample_err

    if args.next and in_ci() and is_check_enabled(args.target_package, "mypy") and not is_typing_ignored(package_name):
        if src_code_error or sample_code_error:
            create_vnext_issue(package_name, "mypy")

    if src_code_error and sample_code_error:
        raise Exception(
            [
                src_code_error,
                sample_code_error,
            ],
        )
    if src_code_error:
        raise src_code_error
    if sample_code_error:
        raise sample_code_error
