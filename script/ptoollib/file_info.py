# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

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

    def generate(self, ctx, values, output_dir):
        unresolved_path = ctx.render_from_template_string(self._output_path_template, values)

        target_path = make_path(output_dir, unresolved_path)
        target_dir = os.path.dirname(target_path)

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        if self._is_template:
            with open(target_path, "wt") as f:
                f.write(ctx.render_from_template_file(self._source_path, values))
        else:
            shutil.copyfile(self._source_path, target_path)
