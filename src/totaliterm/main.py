#!/usr/bin/env python3
"""Execute a command on multiple git repositories."""

import json
import pathlib
import subprocess

import click
import tomlkit
import tomlkit.items
import tomlkit.toml_file
from rich import pretty, print  # noqa: A004

pretty.install()


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


# path to a config file in $XDG_CONFIG_HOME/totaliterm/config or
# ~/.config/totaliterm/config or ~/.totaliterm/config
CONFIG_FILE_PATH = pathlib.Path(click.get_app_dir('totaliterm')).joinpath(
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
    '--tag',
    type=str,
    default='default',
    show_default=True,
    help='tag of directories.',
)
def add(
    path: tuple[pathlib.Path],
    tag: str = 'default',
) -> None:
    """Add directories to the configuration file."""
    config_file = tomlkit.toml_file.TOMLFile(CONFIG_FILE_PATH)
    doc = config_file.read()
    dir_table: tomlkit.items.Table = doc.get('directories', tomlkit.table())
    doc.update({'directories': dir_table})
    dir_array: tomlkit.items.Array = dir_table.get(
        tag, tomlkit.array()
    ).multiline(multiline=True)
    dir_table[tag] = dir_array
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
    help='Execute a command at the each directory.',
)
@click.option(
    '-c',
    '--command',
    type=str,
    required=True,
    help='Any arbitrary command you want to execute in the directory. '
    'Command need to be given as a string, for example, '
    "'ls -lha'.",
)
@click.option(
    '-t',
    '--tag',
    type=str,
    default='default',
    show_default=True,
    help='tag of directories.',
)
@click.option(
    '-y',
    '--yes',
    is_flag=True,
    help='Execute the command without confirmation.',
)
def run(
    command: str,
    *,
    tag: str = 'default',
    yes: bool = False,
) -> None:
    """Any arbitrary command you want to execute in the directory."""
    for i, dir_ in enumerate(
        tomlkit.toml_file.TOMLFile(CONFIG_FILE_PATH).read()['directories'][tag]
    ):
        print(f'{i + 1}: {dir_}')
        if not yes and not click.confirm(
            f'Run the following command?\n  $ {command} ',
            default=True,
        ):
            continue
        cmd = command.split()
        # run cmd and show standard output and standard error
        subprocess.run(cmd, cwd=dir_, check=False)


@main.command(
    name='list',
    help='List registered directories.',
)
@click.option(
    '--tag',
    type=str,
    default='default',
    show_default=True,
    help='tag of directories.',
)
@click.option(
    '-a',
    '--all',
    'show_all_tags',
    is_flag=True,
    help='List all directories of all tags.',
)
def list_dirs(
    tag: str = 'default',
    *,
    show_all_tags: bool = False,
) -> None:
    """List registered directories."""
    config_file = tomlkit.toml_file.TOMLFile(CONFIG_FILE_PATH)
    doc = config_file.read()
    dir_table: tomlkit.items.Table = doc.get('directories', tomlkit.table())
    for tag_, dir_array in dir_table.items():
        if not show_all_tags and tag_ != tag:
            continue
        print(f'{tag_}:')
        for i, dir_ in enumerate(dir_array):
            print(f'{i + 1}: {dir_}')


if __name__ == '__main__':
    main()
