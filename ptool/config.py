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

from ptool.exceptions import Informational
from ptool.util import read_yaml_file
from ptool.value_source import ValueSource

_CONFIG_YAML_FILE_NAME = "config.yaml"
_DEFAULT_CONFIG = {
    "author": "Some Author",
    "author_email": "some@author.org",
    "git_server": {
        "protocol": "https",
        "group": "someauthor",
        "host": "github.com"
    }
}
_TEMPLATES_URL = "https://github.com/rcook/ptool-templates.git"

class Config(object):
    def __init__(self, config_dir):
        self._config_dir = config_dir

        if not os.path.isdir(self._config_dir):
            os.makedirs(self._config_dir)

        self._config_yaml_path = make_path(self._config_dir, "config.yaml")
        if not os.path.isfile(self._config_yaml_path):
            with open(self._config_yaml_path, "wt") as f:
                f.write(yaml.dump(_DEFAULT_CONFIG))

        self._repo_dir = make_path(self._config_dir, "ptool-templates")
        if not os.path.isdir(self._repo_dir):
            git_clone(_TEMPLATES_URL, self._repo_dir)

        self._value_source = None

    @property
    def config_dir(self): return self._config_dir

    @property
    def config_yaml_path(self): return self._config_yaml_path

    @property
    def repo_dir(self): return self._repo_dir

    @property
    def value_source(self):
        if self._value_source is None:
            values = read_yaml_file(self._config_yaml_path)
            self._value_source = ValueSource(self._config_yaml_path, values)
        return self._value_source

# TODO: Implement version checks and repairs
"""
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
"""
