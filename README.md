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