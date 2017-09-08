#!/usr/bin/env python
# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

from __future__ import print_function
import argparse
import datetime
import sys
import yaml

from pyprelude.file_system import *
from pyprelude.temp_util import *
from pysimplevcs.git import *

from ptoollib.arg_util import parse_key_value_pair
from ptoollib.config import Config
from ptoollib.lang_util import safe_namespace
from ptoollib.project_yaml import read_command, read_file
from ptoollib.util import home_dir

_PROJECT_YAML_FILE_NAME = "project.yaml"

class Informational(Exception):
    def __init__(self, message):
        super(Informational, self).__init__(message)

def _template_values(config, args):
    project_name = os.path.basename(args.output_dir)
    values = {
        "copyright_year": str(datetime.datetime.now().year),
        "project_name": project_name,
        "namespace": safe_namespace(project_name)
    }

    with open(config.config_yaml_path, "rt") as f:
        values.update(yaml.load(f))

    for key, value in args.key_value_pairs:
        values[key] = value

    return values

def _do_new(ptool_repo_dir, args):
    config = Config.ensure(ptool_repo_dir)

    if os.path.exists(args.output_dir):
        if args.force_overwrite:
            remove_dir(args.output_dir)
        else:
            raise Informational("Output directory \"{}\" already exists: force overwrite with --force".format(args.output_dir))

    template_dir = make_path(config.repo_dir, args.template_name)
    yaml_path = make_path(template_dir, _PROJECT_YAML_FILE_NAME)

    if not os.path.isfile(yaml_path):
        raise RuntimeError("No template \"{}\" directory found under {}".format(args.template_name, config.repo_dir))

    with open(yaml_path, "rt") as f:
        obj = yaml.load(f)

    values = _template_values(config, args)
    for key, value in args.key_value_pairs:
        values[key] = value

    files = map(lambda o: read_file(o, template_dir), obj.get("files", []))
    commands = map(lambda o: read_command(o), obj.get("commands", []))

    unsorted_keys = []
    for file in files:
        unsorted_keys.extend(file.keys)
    for command in commands:
        unsorted_keys.extend(command.keys)

    keys = sorted(list(set(unsorted_keys)))

    missing_keys = []
    for key in keys:
        if key not in values:
            missing_keys.append(key)

    if len(missing_keys) > 0:
        raise Informational("Provide values for {} in ~/.project.yaml or via command line".format(", ".join(map(lambda k: "\"{}\"".format(k), missing_keys))))

    for file in files:
        file.generate(values, args.output_dir)

    with temp_cwd(args.output_dir):
        for command in commands:
            command.run(values)

def _do_templates(ptool_repo_dir, args):
    config = Config.ensure(ptool_repo_dir)

    templates = []
    for item in sorted(os.listdir(config.repo_dir)):
        yaml_path = make_path(config.repo_dir, item, _PROJECT_YAML_FILE_NAME)
        if os.path.isfile(yaml_path):
            with open(yaml_path, "rt") as f:
                obj = yaml.load(f.read())

            templates.append((os.path.basename(item), obj.get("description", "(no description)")))

    width = 0
    for project_name, _ in templates:
        t = len(project_name)
        if t > width:
            width = t

    for project_name, description in templates:
        print("{}    {}".format(project_name.ljust(width), description))

def _do_update(ptool_repo_dir, args):
    config = Config.ensure(ptool_repo_dir)

    git = Git(config.repo_dir)
    original_commit = git.rev_parse("HEAD")
    git.pull("--rebase")
    new_commit = git.rev_parse("HEAD")

    if original_commit == new_commit:
        print("Repository already at latest revision {}".format(new_commit))
    else:
        print("Repository updated to latest revision {}".format(new_commit))

def _main():
    parser = argparse.ArgumentParser(description="Create project from template")
    subparsers = parser.add_subparsers(help="subcommand help")

    new_parser = subparsers.add_parser("new", help="Create new project from template")
    new_parser.set_defaults(func=_do_new)
    new_parser.add_argument(
        "-f",
        "--force",
        dest="force_overwrite",
        action="store_true",
        help="Force overwrite of existing output directory")
    new_parser.add_argument(
        "template_name",
        metavar="TEMPLATENAME",
        type=str,
        help="Template name")
    new_parser.add_argument(
        "output_dir",
        metavar="OUTPUTDIR",
        type=make_path,
        help="Project output directory")
    new_parser.add_argument(
        "key_value_pairs",
        metavar="KEYVALUEPAIRS",
        type=parse_key_value_pair,
        nargs="*",
        help="Key-value pairs for substitutions in templates")

    templates_parser = subparsers.add_parser("templates", help="List available templates")
    templates_parser.set_defaults(func=_do_templates)

    update_parser = subparsers.add_parser("update", help="Update local template repository")
    update_parser.set_defaults(func=_do_update)

    args = parser.parse_args()

    script_dir = make_path(os.path.dirname(__file__))
    ptool_repo_dir = os.path.dirname(script_dir)

    try:
        args.func(ptool_repo_dir, args)
    except Informational as e:
        print(e.message)
        sys.exit(1)

if __name__ == "__main__":
    _main()
