# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import os

from pyprelude.file_system import *
from pysimplevcs.git import *
from pysimplevcs.git_util import *

from ptoollib.util import home_dir

_TEMPLATES_URL = "https://github.com/rcook/ptool-templates.git"

def ensure_templates():
    store_dir = make_path(home_dir(), ".ptool")
    if not os.path.isdir(store_dir):
        os.makedirs(store_dir)

    templates_dir = make_path(store_dir, "ptool-templates")
    if not os.path.isdir(templates_dir):
        git_clone(_TEMPLATES_URL, templates_dir)

    return templates_dir