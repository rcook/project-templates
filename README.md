# ptool

[![View on PyPI](https://img.shields.io/pypi/v/ptool.svg)](https://pypi.python.org/pypi/ptool)
[![Licence](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/rcook/ptool/master/LICENSE)

Skeleton project generator for various programming languages

Templates are available [here][ptool-templates]

## Developer notes

Various package properties are defined in `ptool/__init__py`:

* `__project_name__`
* `__version__`
* `__description__`

When publishing a new build of the package, ensure that `__version__` is incremented as appropriate.

## Usage

```
usage: ptool [-h] [--version] {new,templates,values,update} ...

Skeleton project generator for various programming languages

positional arguments:
  {new,templates,values,update}
                        subcommand help
    new                 Create new project from template
    templates           List available templates
    values              List all values available to templates
    update              Update local template repository

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

## Licence

Released under [MIT License][licence]

[licence]: LICENSE
[ptool-templates]: https://github.com/rcook/ptool-templates