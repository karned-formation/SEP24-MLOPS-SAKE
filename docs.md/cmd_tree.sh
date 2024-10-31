#tree .. --gitignore -d -L 2
git ls-tree -r --name-only HEAD | tree --fromfile