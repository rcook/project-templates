# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import jinja2
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

class _Template(object):
    @staticmethod
    def from_source(source):
        return _Template(string.Template(source))

    @staticmethod
    def from_file(path):
        with open(path, "rt") as f:
            return _Template(string.Template(f.read()))

    def __init__(self, template):
        self._template = template

    def render(self, values):
        return self._template.substitute(values)

class TemplateContext(object):
    def __init__(self):
        self._source_templates = {}
        self._file_templates = {}

    def template_from_source(self, source):
        template = self._source_templates.get(source)
        if template is None:
            template = _Template.from_source(source)
            self._source_templates[source] = template
        return template

    def template_from_file(self, path):
        template = self._file_templates.get(path)
        if template is None:
            template = _Template.from_file(path)
            self._file_templates[path] = template
        return template

    def render_from_template_source(self, source, values):
        template = self.template_from_source(source)
        return template.render(values)

    def render_from_template_file(self, path, values):
        template = self.template_from_file(path)
        return template.render(values)

def template_tokens(*args):
    keys = []
    for s in args:
        keys.extend(_template_tokens_helper(s))
    return sorted(list(set(keys)))
