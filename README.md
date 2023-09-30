# multigit

Tools to run commands in multiple git repositories.

Useful for performing commands such as `git pull`, `git status` on several
local repositories at once.

## Usage

Run `multigit.py run <command>` in a directory which contains multiple git repositories.

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
