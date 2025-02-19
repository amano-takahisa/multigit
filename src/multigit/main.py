#!/usr/bin/env python3
"""Execute a command on multiple git repositories."""

import json
import pathlib
import subprocess

import click


class Bcolors:
    """Colors for the terminal."""

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Defaults:
    """Default values."""

    LIMIT: int = 100
    OPTIONS: str = ''


@click.group(
    help='Execute a command on multiple git repositories.',
)
def main() -> None:
    """Execute a command on multiple git repositories."""


@main.command(
    help='Clone all repositories of a GitHub account.',
)
@click.option(
    '--username',
    required=True,
    type=str,
    help='GitHub account name',
)
@click.option(
    '--options',
    type=str,
    default=Defaults.OPTIONS,
    show_default=True,
    help='git clone options.',
)
@click.option(
    '-L',
    '--limit',
    type=int,
    default=Defaults.LIMIT,
    show_default=True,
    help='Maximum number of repositories to list.',
)
def clone(
    username: str,
    options: str = '',
    limit: int = Defaults.LIMIT,
) -> None:
    """Clone all repositories of a GitHub account."""
    click.echo(f'username: {username}')
    cmd = [
        'gh',
        'repo',
        'list',
        '--json',
        'name',
        '--limit',
        str(limit),
        username,
    ]
    output = subprocess.run(cmd, text=True, capture_output=True, check=True)
    repo_names = sorted([item['name'] for item in json.loads(output.stdout)])
    remote_repos = [
        f'git@github.com:{username}/{repo_name}.git'
        for repo_name in repo_names
    ]
    cmd = 'git clone ' + options
    for i, (repo_name, remote_repo) in enumerate(
        zip(repo_names, remote_repos, strict=False)
    ):
        click.echo(repo_name)
        if pathlib.Path.cwd().joinpath(repo_name).exists():
            click.echo(f'{repo_name} is exists.')
            continue
        click.echo(
            f'\n{Bcolors.HEADER}{i + 1}/{len(repo_names)}: '
            f'{repo_name}{Bcolors.ENDC}'
        )
        cmd_repo = cmd + f' -- {remote_repo}'
        click.echo(f'cmd_repo: {cmd_repo}')
        subprocess.run(cmd_repo, shell=True, check=False)


@main.command(
    help='Execute a command at the root directory of each repository.',
)
@click.option(
    '--command',
    type=str,
    help='Any arbitrary command you want to execute in the root directory '
    'of each repository. Git directories are searched only up to the '
    'first level. Command need to be given as a string, for example, '
    "'ls -lha'.",
)
def run(command: str) -> None:
    """Execute a command at the root directory of each repository."""
    click.echo(f'command: {command}')
    cwd = pathlib.Path.cwd()
    git_dirs = sorted(cwd.glob('*/.git'))
    for i, git_dir in enumerate(git_dirs):
        git_root = git_dir.parent
        click.echo(f'\n{Bcolors.HEADER}{i + 1}: {git_root.name}{Bcolors.ENDC}')
        subprocess.run(command, shell=True, cwd=git_root, check=False)


@main.command(
    name='list',
    help='List all repositories.',
)
@click.option(
    '--github',
    is_flag=True,
    help=(
        'List all repositories of your GitHub account.'
        'You need to install and authenticate gh-cli.'
    ),
)
@click.option(
    '-L',
    '--limit',
    type=int,
    default=Defaults.LIMIT,
    show_default=True,
    help='Maximum number of repositories to list.',
)
def list_repos(
    *,
    github: bool = False,
    limit: int = Defaults.LIMIT,
) -> None:
    """List all repositories."""
    if github:
        cmd = [
            'gh',
            'repo',
            'list',
            '--limit',
            str(limit),
            '--json',
            'name',
        ]
        output = subprocess.run(
            cmd, text=True, capture_output=True, check=True
        )
        repo_names = sorted(
            [item['name'] for item in json.loads(output.stdout)]
        )
        for i, repo_name in enumerate(repo_names):
            click.echo(f'{i + 1}: {repo_name}')
    else:
        cwd = pathlib.Path.cwd()
        git_dirs = sorted(cwd.glob('*/.git'))
        for i, git_dir in enumerate(git_dirs):
            git_root = git_dir.parent
            click.echo(f'{i + 1}: {git_root.name}')


if __name__ == '__main__':
    main()
