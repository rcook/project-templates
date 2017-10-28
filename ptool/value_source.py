# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import datetime

from pyprelude.util import *

class ValueSource(object):
    @staticmethod
    def project(project_name):
        return ValueSource("(project)", {
            "copyright_year": str(datetime.datetime.now().year),
            "project_name": project_name
        })

    @staticmethod
    def command_line(values):
        return ValueSource("(command line)", values)

    @staticmethod
    def merge_values(*sources):
        values = {}
        for source in unpack_args(*sources):
            values.update(source.values)
        return values

    def __init__(self, path, values):
        self._path = path
        items = values if isinstance(values, list) else values.iteritems()
        self._values = { key : (value, self) for key, value in items }

    @property
    def path(self): return self._path

    @property
    def values(self): return self._values
