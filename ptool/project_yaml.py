# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

from pyprelude.file_system import *

from ptoollib.commands import GitExecuteAttributeCommandInfo, GitSymlinkCommandInfo, SimpleCommandInfo
from ptoollib.file_info import FileInfo

def read_file(obj, template_dir):
    if isinstance(obj, dict):
        path = obj["path"]
        output_path_template = obj.get("output-path", path)
        is_template = obj.get("preprocess", True)
        source_path = make_path(template_dir, path)
        return FileInfo(source_path, output_path_template, is_template=is_template)
    elif isinstance(obj, str):
        source_path = make_path(template_dir, obj)
        return FileInfo(source_path, obj, is_template=True)
    else:
        raise RuntimeError("Unsupported node type {}".format(type(obj)))

def read_command(obj):
    if isinstance(obj, dict):
        t = list(obj)
        if len(t) != 1:
            raise RuntimeError("Invalid command {}".format(obj))
        tool_name = t[0]
        if tool_name == "git-execute-attribute":
            o = obj["git-execute-attribute"]
            path_template = o["path"]
            return GitExecuteAttributeCommandInfo(path_template)
        elif tool_name == "git-symlink":
            o = obj["git-symlink"]
            source_path_template = o["source-path"]
            target_path_template = o["target-path"]
            return GitSymlinkCommandInfo(source_path_template, target_path_template)
        else:
            raise RuntimeError("Unsupported tool \"{}\"".format(tool_name))
    elif isinstance(obj, str):
        return SimpleCommandInfo(obj)
    else:
        raise RuntimeError("Unsupported command type {}".format(type(obj)))

