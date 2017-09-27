# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import os
import yaml

from pyprelude.file_system import *
from pysimplevcs.git import *
from pysimplevcs.git_util import *

from ptoollib.exceptions import Informational
from ptoollib.util import home_dir, read_yaml_file
from ptoollib.value_source import ValueSource
from ptoollib.version import Version, parse_version_constraint

_CONFIG_YAML_FILE_NAME = "config.yaml"
_DEFAULT_CONFIG_YAML_FILE_NAME = "default-config.yaml"
_TEMPLATES_URL = "https://github.com/rcook/ptool-templates.git"

class Config(object):
    def __init__(self, store_dir, config_yaml_path, repo_dir, ptool_version):
        self._store_dir = store_dir
        self._config_yaml_path = config_yaml_path
        self._repo_dir = repo_dir
        self._ptool_version = ptool_version
        self._value_source = None

    @property
    def store_dir(self): return self._store_dir

    @property
    def config_yaml_path(self): return self._config_yaml_path

    @property
    def repo_dir(self): return self._repo_dir

    @property
    def ptool_version(self): return self._ptool_version

    @property
    def value_source(self):
        if self._value_source is None:
            values = read_yaml_file(self._config_yaml_path)
            self._value_source = ValueSource(self._config_yaml_path, values)
        return self._value_source

    @staticmethod
    def ensure(ptool_repo_dir, repair_templates=False):
        store_dir = make_path(home_dir(), ".ptool")
        if not os.path.isdir(store_dir):
            os.makedirs(store_dir)

        config_yaml_path = make_path(store_dir, "config.yaml")
        if not os.path.isfile(config_yaml_path):
            shutil.copyfile(
                make_path(ptool_repo_dir, _DEFAULT_CONFIG_YAML_FILE_NAME),
                config_yaml_path)

        repo_dir = make_path(store_dir, "ptool-templates")
        if not os.path.isdir(repo_dir):
            git_clone(_TEMPLATES_URL, repo_dir)

        if repair_templates:
            try:
                ptool_version = _perform_version_check(ptool_repo_dir, repo_dir)
            except Informational as e:
                print("Version checked failed: {}".format(e))
                print("Repairing templates at {}".format(repo_dir))
                remove_dir(repo_dir)
                git_clone(_TEMPLATES_URL, repo_dir)
                ptool_version = _perform_version_check(ptool_repo_dir, repo_dir)
        else:
            ptool_version = _perform_version_check(ptool_repo_dir, repo_dir)

        return Config(store_dir, config_yaml_path, repo_dir, ptool_version)

def _perform_version_check(ptool_repo_dir, repo_dir):
    repo_ptool_yaml_path = make_path(repo_dir, "_ptool.yaml")
    if not os.path.isfile(repo_ptool_yaml_path):
        raise Informational("No repository configuration file at {}".format(repo_ptool_yaml_path))

    git = Git(ptool_repo_dir)
    ptool_version = Version.from_git(git)

    with open(repo_ptool_yaml_path, "rt") as f:
        obj = yaml.load(f.read())

    constraint_str = obj.get("ptool-version")
    if constraint_str is None:
        raise Informational("No version constraint found in {}".format(repo_ptool_yaml_path))

    constraint = parse_version_constraint(constraint_str)
    if not constraint.is_satisfied_by(ptool_version):
        raise Informational("This version of ptool ({}) is not compatible with version constraint ({}) in {}".format(ptool_version, constraint, repo_ptool_yaml_path))

    return ptool_version