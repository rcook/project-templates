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

from pyprelude.temp_util import *
from pysimplevcs.git import *

from ptoollib.arg_util import parse_key_value_pair
from ptoollib.config import Config
from ptoollib.exceptions import Informational
from ptoollib.lang_util import TokenList
from ptoollib.template_spec import TemplateSpec
from ptoollib.util import home_dir, read_yaml_file

def _template_values(project_name, *args):
    token_list = TokenList(project_name)

    values = {
        "copyright_year": str(datetime.datetime.now().year),
        "project_name": project_name,
        "cpp_namespace": token_list.cpp_namespace,
        "hs_module_name": token_list.hs_module_name
    }

    for d in unpack_args(*args):
        values.update(d)

    return values

def _do_new(ptool_repo_dir, args):
    config = Config.ensure(ptool_repo_dir)

    if os.path.exists(args.output_dir):
        if args.force_overwrite:
            remove_dir(args.output_dir)
        else:
            raise Informational("Output directory \"{}\" already exists: force overwrite with --force".format(args.output_dir))

    template_spec = TemplateSpec.read(config.repo_dir, args.template_name)
    project_name = os.path.basename(args.output_dir)

    values = _template_values(
        project_name,
        template_spec.template_values,
        read_yaml_file(config.config_yaml_path),
        args.key_value_pairs)

    unsorted_keys = []
    for file in template_spec.files:
        unsorted_keys.extend(file.keys)
    for command in template_spec.commands:
        unsorted_keys.extend(command.keys)

    keys = sorted(list(set(unsorted_keys)))

    missing_keys = []
    for key in keys:
        if key not in values:
            missing_keys.append(key)

    if len(missing_keys) > 0:
        raise Informational(
            "Provide values for {} in {} or via command line".format(
                ", ".join(map(lambda k: "\"{}\"".format(k), missing_keys)),
                config.config_yaml_path))

    for file in template_spec.files:
        file.generate(values, args.output_dir)

    with temp_cwd(args.output_dir):
        for command in template_spec.commands:
            command.run(values)

def _do_templates(ptool_repo_dir, args):
    config = Config.ensure(ptool_repo_dir)

    templates = []
    for item in sorted(os.listdir(config.repo_dir)):
        template_spec = TemplateSpec.try_read(config.repo_dir, item)
        if template_spec is not None:
            templates.append((template_spec.name, template_spec.description))

    width = 0
    for project_name, _ in templates:
        t = len(project_name)
        if t > width:
            width = t

    for project_name, description in templates:
        print("{}    {}".format(project_name.ljust(width), description))

def _do_values(ptool_repo_dir, args):
    config = Config.ensure(ptool_repo_dir)

    template_spec = TemplateSpec.read(config.repo_dir, args.template_name)

    values = _template_values(
        "example-project-name-ABC",
        template_spec.template_values,
        read_yaml_file(config.config_yaml_path),
        args.key_value_pairs)

    for key in sorted(values.keys()):
        value = values[key]
        lines = value.splitlines()
        if len(lines) > 1:
            print("{}:".format(key))
            for line in lines:
                print("  {}".format(line))
        else:
            print("{}: {}".format(key, value))
        print()

def _do_update(ptool_repo_dir, args):
    config = Config.ensure(ptool_repo_dir, repair_templates=args.repair_templates)

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

    values_parser = subparsers.add_parser("values", help="List all values available to templates")
    values_parser.add_argument(
        "template_name",
        metavar="TEMPLATENAME",
        type=str,
        help="Template name")
    values_parser.add_argument(
        "key_value_pairs",
        metavar="KEYVALUEPAIRS",
        type=parse_key_value_pair,
        nargs="*",
        help="Key-value pairs for substitutions in templates")
    values_parser.set_defaults(func=_do_values)

    update_parser = subparsers.add_parser("update", help="Update local template repository")
    update_parser.set_defaults(func=_do_update)
    update_parser.add_argument(
        "-r",
        "--repair",
        dest="repair_templates",
        action="store_true",
        help="Repair templates by overwriting existing Git repo")

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
