# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import os

from pyprelude.file_system import *

from ptool.project_yaml import read_command, read_file
from ptool.util import read_yaml_file
from ptool.value_source import ValueSource

_PTOOL_YAML_FILE_NAME = "_ptool.yaml"

class TemplateSpec(object):
    @staticmethod
    def read(repo_dir, template_name):
        template_spec = TemplateSpec.try_read(repo_dir, template_name)
        if template_spec is not None:
            return template_spec

        raise RuntimeError("No template \"{}\" directory found under {}".format(template_name, repo_dir))

    @staticmethod
    def try_read(repo_dir, template_name):
        template_dir = make_path(repo_dir, template_name)
        template_yaml_path = make_path(template_dir, _PTOOL_YAML_FILE_NAME)

        if not os.path.isfile(template_yaml_path):
            return

        obj = read_yaml_file(template_yaml_path)
        return TemplateSpec(template_yaml_path, template_dir, obj)

    def __init__(self, path, template_dir, obj):
        self._path = path
        self._template_dir = template_dir
        self._obj = obj

        self._name = os.path.basename(self._template_dir)
        self._description = self._obj.get("description", "(no description)")
        self._value_source = None
        self._filters = None
        self._globals = None
        self._files = None
        self._commands = None

    @property
    def template_dir(self): return self._template_dir

    @property
    def name(self): return self._name

    @property
    def description(self): return self._description

    @property
    def value_source(self):
        if self._value_source is None:
            values = self._obj.get("template-values", {})
            self._value_source = ValueSource(self._path, values)
        return self._value_source

    @property
    def files(self):
        if self._files is None:
            self._files = map(lambda o: read_file(o, self._template_dir), self._obj.get("files", []))
        return self._files

    @property
    def commands(self):
        if self._commands is None:
            self._commands = map(lambda o: read_command(o), self._obj.get("commands", []))
        return self._commands
