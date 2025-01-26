#!/usr/bin/env python3
"""
Execute a command on multiple git repositories.
"""

import argparse
import json
import os
import pathlib
import subprocess
from typing import NamedTuple


class Bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Default(NamedTuple):
    limit: int = 100
    options: str = ""


DEFAULT = Default()


def add_args(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(
        title="multigit",
        description="Execute arbitrary command or clone",
    )

    # run sub-command ######################
    parser_command = subparsers.add_parser(
        name="run",
        help="Execute arbitrary command at each git root directories.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_command.add_argument(
        "command",
        type=str,
        help="Any arbitrary command you want to execute in the root directory "
        "of each repository. Git directories are searched only up to the "
        "first level. Command need to be given as a string, for example, "
        "'ls -lha'.",
    )
    parser_command.set_defaults(func=run_command)

    # clone sub-command ######################
    parser_git = subparsers.add_parser(
        name="clone",
        help="Clone all repositories of the specified GitHub user.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_git.add_argument(
        "-L",
        "--limit",
        required=False,
        type=int,
        default=DEFAULT.limit,
        help="Maximum number of repositories to list.",
    )
    parser_git.add_argument(
        "-u", "--username", required=True, help="GitHub account name"
    )
    parser_git.add_argument(
        "options",
        type=str,
        nargs="?",
        default=DEFAULT.options,
        help="git clone options.",
    )
    parser_git.set_defaults(func=clone)


def run_command(command: str):
    cwd = pathlib.Path(os.getcwd())
    git_dirs = sorted(list(cwd.glob("*/.git")))
    for git_dir in git_dirs:
        git_root = git_dir.parent
        print(f"\n{Bcolors.HEADER}{git_root.name}{Bcolors.ENDC}")
        subprocess.run(command, shell=True, cwd=git_root)


def clone(username: str, options: str = "", limit: int = DEFAULT.limit):
    cmd = [
        "gh",
        "repo",
        "list",
        "--json",
        "name",
        "--limit",
        str(limit),
        username,
    ]
    output = subprocess.run(cmd, text=True, capture_output=True, check=True)
    repo_names = [item["name"] for item in json.loads(output.stdout)]
    remote_repos = [
        f"git@github.com:{username}/{repo_name}.git"
        for repo_name in repo_names
    ]
    cmd = "git clone " + options
    for i, (repo_name, remote_repo) in enumerate(
        zip(repo_names, remote_repos)
    ):
        print(repo_name)
        if pathlib.Path(os.getcwd()).joinpath(repo_name).exists():
            print(f"{repo_name} is exists.")
            continue
        print(
            f"\n{Bcolors.HEADER}{i+1}/{len(repo_names)}: "
            f"{repo_name}{Bcolors.ENDC}"
        )
        cmd_repo = cmd + f" -- {remote_repo}"
        subprocess.run(cmd_repo, shell=True)


def main():
    parser = argparse.ArgumentParser(
        prog="multigit", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    add_args(parser)
    parser.set_defaults(func=parser.print_help)
    kwargs = vars(parser.parse_args())
    func = kwargs.pop("func")
    func(**kwargs)

if __name__ == "__main__":
    main()
