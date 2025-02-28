#!/usr/bin/env python3
"""Execute a command on multiple git repositories."""

import json
import pathlib
import subprocess
import tomllib

import click
import tomlkit
import tomlkit.items
import tomlkit.toml_file


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


# path to a config file in $XDG_CONFIG_HOME/multigit/config or
# ~/.config/multigit/config or ~/.multigit/config
CONFIG_FILE_PATH = pathlib.Path(click.get_app_dir('multigit')).joinpath(
    'config.toml'
)
if not CONFIG_FILE_PATH.exists():
    CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE_PATH.touch()


@click.group(
    help='Execute a command on multiple directories.',
)
def main() -> None:
    """Execute a command on multiple directories."""


@main.command(
    help='Add directories to the configuration file.',
)
@click.argument(
    'path',
    nargs=-1,
    type=pathlib.Path,
)
@click.option(
    '--domain',
    type=str,
    default='default',
    show_default=True,
    help='Domain of directories.',
)
def add(
    path: tuple[pathlib.Path],
    domain: str = 'default',
) -> None:
    """Add directories to the configuration file."""
    click.echo(f'path: {path}')
    config_file = tomlkit.toml_file.TOMLFile(CONFIG_FILE_PATH)
    doc = config_file.read()
    dir_table: tomlkit.items.Table = doc.get('directories', tomlkit.table())
    doc.update({'directories': dir_table})
    dir_array: tomlkit.items.Array = dir_table.get(
        domain, tomlkit.array().multiline(multiline=True)
    )
    dir_table[domain] = dir_array
    for p in path:
        if not p.exists():
            click.echo(f'{p} does not exist.')
            continue
        if not p.is_dir():
            click.echo(f'{p} is not a directory.')
            continue
        if p.resolve().as_posix() in dir_array:
            click.echo(f'{p} is already in the list.')
            continue
        dir_array.append(p.resolve().as_posix())
    config_file.write(doc)


@main.group()
def config() -> None:
    """Set configuration."""
    click.echo('group: ')


@main.group()
def second_level_2() -> None:
    """Second level 2."""


@second_level_2.command()
def third_level_command_3() -> None:
    """Third level command under 2nd level 2."""


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
