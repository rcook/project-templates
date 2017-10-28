# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import os

from pyprelude.temp_util import *
from pysimplevcs.git import *

def _get_prefix(git):
    return git.rev_parse("--show-prefix").strip()

def _hash_object(git, content):
    return git.hash_object("-w", "--stdin", stdin=content).strip()

# Inspired by https://coderwall.com/p/z86txw/make-symlink-on-windows-in-a-git-repo
def git_symlink(repo_dir, source_path, target_path):
    rel_path = os.path.relpath(source_path, os.path.dirname(target_path))
    git = Git(repo_dir)
    prefix = _get_prefix(git)
    hash = _hash_object(git, rel_path)
    git.update_index("--add", "--cacheinfo", "120000", hash, "{}{}".format(prefix, target_path))
    git.checkout("--", target_path)

def git_execute_attribute(repo_dir, path):
    git = Git(repo_dir)
    git.update_index("--chmod=+x", path)
    git.checkout("--", path)
