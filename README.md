# totaliterm

Tools to run commands in multiple directory.

Useful for performing commands such as `git pull`, `git status` on several
local repositories at once.

## Installation

```console
pip install .
```

## Usage

Register a local git repository to be managed by totaliterm.

```console
totaliterm add /path/to/dir
```

The above command will add `config` file to `$XDG_CONFIG_HOME/totaliterm` or
`~/.config/totaliterm` with the following content.

```ini
[directories]
default = [
    "/path/to/dir"
]
```

With `--tag` option, you can specify a group to which directories belong.

```console
totaliterm add path/to/dir1 path/to/dir2 --tag my_project
```

The above command will add `config` file to `$XDG_CONFIG_HOME/totaliterm` or
`~/.config/totaliterm` with the following content.

```ini
[directories]
my_project = [
    "/path/to/dir1",
    "/path/to/dir2",
]
```

`totaliterm list` lists all directories registered to totaliterm.

```console
totaliterm list
```

`totaliterm run` runs a command in all directories managed by totaliterm.

```console
# Run 'git status' in all git repositories
totaliterm run 'git status'
```

## Development

### Testing

Test in a container

```console
docker build \
    -t totaliterm \
    -f docker/Dockerfile \
    --build-arg USER_NAME=$(whoami) \
    .

docker run -it --rm \
    -v $(pwd):/home/$(whoami)/repos \
    -w /home/$(whoami)/repos \
    totaliterm:latest \
    bash
```

Then, in the container

```console
pip install -e .
totaliterm
```

Test locally

```console
pixi install
pixi shell --environment dev
totaliterm
```

```console
ruff check --fix
ruff format -v
```

Install globally

```console
pipx install .
```
