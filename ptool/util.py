# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import yaml

def read_yaml_file(path):
    with open(path, "rt") as f:
        return yaml.load(f)
