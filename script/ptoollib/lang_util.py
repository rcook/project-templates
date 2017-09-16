# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

def _safe_token(s):
    h, t = s[0], s[1:]
    h = h if h.isalpha() else "_"
    t = "".join(map(lambda c: c if c.isalnum() else "_", t))
    return h + t

class TokenList(object):
    def __init__(self, s):
        self._fragments = s.replace("-", "_").split("_")
        self._safe_tokens = map(_safe_token, self._fragments)
        self._cpp_namespace = None
        self._hs_module_name = None

    @property
    def fragments(self): return self._fragments

    @property
    def cpp_namespace(self):
        if self._cpp_namespace is None:
            self._cpp_namespace = "_".join(self._safe_tokens)
        return self._cpp_namespace

    @property
    def hs_module_name(self):
        if self._hs_module_name is None:
            self._hs_module_name = "".join(map(lambda s: s.title(), self._safe_tokens))
        return self._hs_module_name
