#!/usr/bin/env python3
"""
Execute a command on multiple git repositories.
"""

import argparse
import os
import pathlib
import subprocess


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def add_args(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(
        title="multigit", description="Execute arbitrary command or clone"
    )

    # run sub-command ######################
    parser_command = subparsers.add_parser(
        name="run", help="Execute arbitrary command at each git root directories."
    )
    parser_command.add_argument(
        "command",
        type=str,
        help="Any arbitrary command you want to execute in the root directory "
        "of each repository. Git directories are searched only up to the first "
        "level. Command need to be given as a string, for example, 'ls -lha'.",
    )
    parser_command.set_defaults(func=run_command)

    # clone sub-command ######################
    parser_git = subparsers.add_parser(
        name="clone", help="Clone all repositories of the specified GitHub user."
    )
    parser_git.add_argument(
        "-u", "--username", required=True, help="GitHub account name"
    )
    parser_git.add_argument(
        "-n",
        "--max-repos",
        default=50,
        help="Maximum number of repositories to be cloned.",
    )

    parser_git.set_defaults(func=clone)


def run_command(command: str):
    cwd = pathlib.Path(os.getcwd())
    git_dirs = cwd.glob("*/.git")
    for git_dir in git_dirs:
        git_root = git_dir.parent
        print(f"\n{bcolors.HEADER}{git_root.name}{bcolors.ENDC}")
        subprocess.run(command, shell=True, cwd=git_root)


def clone(*args, **kwargs):
    raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="multigit",
    )
    add_args(parser)
    parser.set_defaults(func=parser.print_help)
    kwargs = vars(parser.parse_args())
    func = kwargs.pop("func")
    func(**kwargs)
