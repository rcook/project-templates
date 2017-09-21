# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import os
import yaml

def home_dir():
    return os.path.expanduser("~")

def read_yaml_file(path):
    with open(path, "rt") as f:
        return yaml.load(f)
