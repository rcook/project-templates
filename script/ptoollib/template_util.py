# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import string

def _template_tokens_helper(template_source):
    tokens = []
    for escaped, named, braced, invalid in string.Template.pattern.findall(template_source):
        escaped_length = len(escaped)
        named_length = len(named)
        braced_length = len(braced)
        invalid_length = len(invalid)
        total_length = escaped_length + named_length + braced_length + invalid_length
        if escaped_length > 0:
            assert escaped_length == total_length
        elif named_length > 0:
            assert named_length == total_length
            tokens.append(named)
        elif braced_length > 0:
            assert braced_length == total_length
            tokens.append(braced)
        else:
            assert invalid_length == total_length
            raise ValueError("Template is invalid")
    return tokens

def template_tokens(*args):
    keys = []
    for s in args:
        keys.extend(_template_tokens_helper(s))
    return sorted(list(set(keys)))

def render_template_string(template_source, values):
    return string.Template(template_source).substitute(values)

def render_template_file(path, values):
    with open(path, "rt") as f:
        return render_template_string(f.read(), values)
