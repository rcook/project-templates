# ptool

Python tool for generating skeleton projects in various programming languages

Templates are available [here][ptool-templates]

## Install prerequisites

### Linux (Ubuntu)

```
sudo apt-get install python-minimal python-pip
pip install --upgrade pip
sudo pip install virtualenv
```

## Installation

Until I can be motivated to write a proper installer&hellip;

### Linux and macOS

```
git clone git@github.com:rcook/ptool.git
cp ptool/ptool-sample /path/to/ptool
```

The location `/path/to/ptool` should be somewhere on the system search path. Edit the contents of the result file to point to the "real" `ptool` in the `script` subdirectory of the Git repo.

## Usage

```
usage: project.py [-h] {new,templates} ...

Create project from template

positional arguments:
  {new,templates}  subcommand help
    new            Create new project from template
    templates      List available templates

optional arguments:
  -h, --help       show this help message and exit
```

## Licence

Released under [MIT License][licence]

[licence]: LICENSE
[ptool-templates]: https://github.com/rcook/ptool-templates