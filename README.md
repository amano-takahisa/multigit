# multigit

Tools to run commands in multiple git repositories.

Useful for performing commands such as `git pull`, `git status` on several
local repositories at once.

## Installation

```console
pip install .
```

## Usage

Register a local git repository to be managed by multigit.

```console
multigit add /path/to/repo
```

The above command will add `config` file to `$XDG_CONFIG_HOME/multigit` or
`~/.config/multigit` with the following content.

```ini
[repositories]
default = [
    "/path/to/repo"
]
```

With `--group` option, you can add a repository to a group.

```console
multigit add /path/to/repo --group my_group
```

The above command will add `config` file to `$XDG_CONFIG_HOME/multigit` or
`~/.config/multigit` with the following content.

```ini
[repositories]
my_group = [
    "/path/to/repo"
]
```

`multigit list` lists all repositories registered to be managed by multigit.

```console
multigit list
```

`multigit run` runs a command in all git repositories in the current directory.

```console
# Run 'git fetch' in all git repositories
multigit run 'git fetch'
```

`multigit clone `

## Examples

```console
/home/takahisa/repos/$ ls -lha
dotfiles    numheader    multigit    web_search_filter
/home/takahisa/repos/$ ./multigit/multigit.py run 'git pull'
dotfiles
Already up to date.

numheader
Already up to date.

multigit
Already up to date.

web_search_filter
Already up to date.
```

## Development

### Testing

Test in a container

```console
docker build \
    -t multigit \
    -f docker/Dockerfile \
    --build-arg USER_NAME=$(whoami) \
    .

docker run -it --rm \
    -v $(pwd):/home/$(whoami)/repos \
    -w /home/$(whoami)/repos \
    multigit:latest \
    bash
```

Then, in the container

```console
pip install -e .
multigit
```

Test locally

```console
pixi install
pixi shell --environment dev
multigit
```

```console
ruff check --fix
ruff format -v
```
