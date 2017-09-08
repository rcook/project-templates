# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import string

from pyprelude.file_system import *

from ptoollib.template_util import template_tokens

class FileInfo(object):
    def __init__(self, source_path, output_path_template, is_template):
        self._source_path = source_path
        self._output_path_template = output_path_template
        self._is_template = is_template
        self._content = None
        self._keys = None

    @property
    def keys(self):
        if self._keys is None:
            self._keys = template_tokens(self._output_path_template, self.content if self._is_template else "")
        return self._keys

    @property
    def content(self):
        if not self._is_template:
            raise RuntimeError("Not a template")

        if self._content is None:
            with open(self._source_path, "rt") as f:
                self._content = f.read()

        return self._content

    def generate(self, values, output_dir):
        t0 = string.Template(self._output_path_template)
        t1 = t0.substitute(values)

        target_path = make_path(output_dir, t1)
        target_dir = os.path.dirname(target_path)

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        if self._is_template:
            with open(self._source_path, "rt") as f:
                template = string.Template(f.read())

            with open(target_path, "wt") as f:
                f.write(template.substitute(values))
        else:
            shutil.copyfile(self._source_path, target_path)
