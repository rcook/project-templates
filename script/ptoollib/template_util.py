# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

from jinja2 import Environment
import string

"""
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
"""

def _git_url_filter(project_name, git_server):
    protocol = git_server["protocol"]
    if protocol == "https":
        host = git_server["host"]
        group = git_server["group"]
        return "{}://{}/{}/{}".format(protocol, host, group, project_name)
    else:
        raise RuntimeError("Unsupported Git protocol {}".format(protocol))

class _Template(object):
    def __init__(self, template):
        self._template = template

    def render(self, values):
        return self._template.render(values)

class TemplateContext(object):
    def __init__(self):
        self._env = Environment()
        self._env.filters["git_url"] = _git_url_filter
        self._source_templates = {}
        self._file_templates = {}

    def template_from_source(self, source):
        template = self._source_templates.get(source)
        if template is None:
            template = _Template(self._env.from_string(source))
            self._source_templates[source] = template
        return template

    def template_from_file(self, path):
        template = self._file_templates.get(path)
        if template is None:
            with open(path, "rt") as f:
                template = _Template(self._env.from_string(unicode(f.read())))
            self._file_templates[path] = template
        return template

    def render_from_template_source(self, source, values):
        template = self.template_from_source(source)
        return template.render(values)

    def render_from_template_file(self, path, values):
        template = self.template_from_file(path)
        return template.render(values)

def template_tokens(*args):
    """
    keys = []
    for s in args:
        keys.extend(_template_tokens_helper(s))
    return sorted(list(set(keys)))
    """
    return []