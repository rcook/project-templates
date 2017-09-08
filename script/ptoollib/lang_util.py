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

def safe_namespace(s):
    fragments = s.replace("-", "_").split("_")
    namespace = "_".join(map(_safe_token, fragments))
    return namespace
