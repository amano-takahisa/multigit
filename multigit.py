#!/usr/bin/env python3
"""
Execute a command on multiple git repositories.
"""

import argparse


def add_args(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(
        title="multigit", description="Execute arbitrary command or clone"
    )
    # ------------------------
    parser_command = subparsers.add_parser(
        name="run", help="Execute arbitrary command at each git root directories."
    )
    parser_command.add_argument(
        "command",
        type=str,
        help="Any arbitrary command you want to execute in the root directory "
        "of each repository. Command. For example, 'ls -lha'.",
    )
    parser_command.set_defaults(func=run_command)
    # ------------------------
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


def run_command(*args, **kwargs):
    ...


def clone(*args, **kwargs):
    ...


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="multigit",
    )
    add_args(parser)
    parser.set_defaults(func=lambda _: parser.print_help())
    args = parser.parse_args()
    args.func(args)
