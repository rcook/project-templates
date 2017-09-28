# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import jinja2
import string

from ptoollib.lang_util import TokenList

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

def _git_clone_url_filter(project_name, git_server):
    protocol = git_server["protocol"]
    if protocol == "https":
        host = git_server["host"]
        group = git_server["group"]
        return "{}://{}/{}/{}.git".format(protocol, host, group, project_name)
    else:
        raise RuntimeError("Unsupported Git protocol {}".format(protocol))

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
    def __init__(self, filters, values):
        self._env = jinja2.Environment(undefined=jinja2.StrictUndefined)

        self._env.filters["git_clone_url"] = _git_clone_url_filter
        self._env.filters["git_url"] = _git_url_filter
        for name, body in filters.iteritems():
            self._env.filters[name] = lambda s: (eval(body))(self._token_list(s).safe_tokens)

        self._values = values
        self._templates_from_strings = {}
        self._templates_from_files = {}
        self._token_lists = {}

    def render_from_template_string(self, s, values):
        template = self._template_from_string(s)
        return template.render(values)

    def render_from_template_file(self, path, values):
        template = self._template_from_file(path)
        return template.render(values)

    def _template_from_string(self, s):
        template = self._templates_from_strings.get(s)
        if template is None:
            template = _Template(self._env.from_string(s))
            self._templates_from_strings[s] = template
        return template

    def _template_from_file(self, path):
        template = self._templates_from_files.get(path)
        if template is None:
            with open(path, "rt") as f:
                template = _Template(self._env.from_string(unicode(f.read())))
            self._templates_from_files[path] = template
        return template

    def _token_list(self, s):
        token_list = self._token_lists.get(s)
        if token_list is None:
            token_list = TokenList(s)
            self._token_lists[s] = token_list
        return token_list

def template_tokens(*args):
    """
    keys = []
    for s in args:
        keys.extend(_template_tokens_helper(s))
    return sorted(list(set(keys)))
    """
    return []