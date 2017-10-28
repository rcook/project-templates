#!/usr/bin/env python
# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

from __future__ import print_function
import argparse
import sys

from pyprelude.temp_util import *
from pysimplevcs.git import *

from ptool import __description__, __project_name__, __version__
from ptool.arg_util import parse_key_value_pair
from ptool.config import Config
from ptool.exceptions import Informational
from ptool.template_spec import TemplateSpec
from ptool.template_util import TemplateContext
from ptool.value_source import ValueSource

def _do_new(ptool_repo_dir, args):
    config = Config.ensure(ptool_repo_dir)

    if os.path.exists(args.output_dir):
        if args.force_overwrite:
            remove_dir(args.output_dir)
        else:
            raise Informational("Output directory \"{}\" already exists: force overwrite with --force".format(args.output_dir))

    template_spec = TemplateSpec.try_read(config.repo_dir, args.template_name)
    if template_spec is None:
        raise Informational("No template \"{}\" found in {}".format(args.template_name, config.repo_dir))

    project_name = os.path.basename(args.output_dir)

    values = ValueSource.merge_values(
        ValueSource.project(project_name),
        template_spec.value_source,
        config.value_source,
        ValueSource.command_line(args.key_value_pairs))

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

    values_without_sources = { key : value for key, (value, _) in values.iteritems() }
    ctx = TemplateContext(
        [template_spec.template_dir, config.repo_dir],
        template_spec.filters,
        values_without_sources)
    for key, global_ in template_spec.globals.iteritems():
        values_without_sources[key] = ctx.render_from_template_string(global_, values_without_sources)

    for file in template_spec.files:
        file.generate(ctx, values_without_sources, args.output_dir)

    with temp_cwd(args.output_dir):
        for command in template_spec.commands:
            command.run(ctx, values_without_sources)

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

    template_spec = TemplateSpec.try_read(config.repo_dir, args.template_name)
    if template_spec is None:
        raise Informational("No template \"{}\" found in {}".format(args.template_name, config.repo_dir))

    values = ValueSource.merge_values(
        ValueSource.project("example-project-name-ABC"),
        template_spec.value_source,
        config.value_source,
        ValueSource.command_line(args.key_value_pairs))

    for key in sorted(values.keys()):
        value, source = values[key]
        if isinstance(value, str):
            lines = value.splitlines()
            if len(lines) > 1:
                print("{}:".format(key))
                for line in lines:
                    print("  {}".format(line))
            else:
                print("{}: {}".format(key, value))
        elif isinstance(value, dict):
            print("{}:".format(key))
            for key in sorted(value.keys()):
                print("  {}: {}".format(key, value[key]))
        elif isinstance(value, list):
            print("{}:".format(key))
            for item in value:
                print("  {}".format(item))
        else:
            raise RuntimeError("Unsupported value type {}".format(type(value)))

        print("  [from {}]".format(source.path))
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

def _main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog=__project_name__, description=__description__)
    parser.add_argument("--version", action="version", version="{} version {}".format(__project_name__, __version__))

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
