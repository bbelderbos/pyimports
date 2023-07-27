# List modules and their origins

Does not work yet, figuring out if something is Standard Library is quite easy, but PyPI vs own module is harder and I need to revisit ...

## Simple example

Running it against the script.py of this project, quickly adding another file + import

```
$ touch dummy.py
# adding it to script.py
$ python script.py

dummy.py
No imports

script.py
Stdlib: ast, collections, enum, pathlib, sys, typing
External: stdlib_list
Project: dummy
```
