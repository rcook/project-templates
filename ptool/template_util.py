# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import imp
import inflection
import jinja2
import string
import sys

from pyprelude.file_system import *

from ptool.lang_util import TokenList

_REGISTER_ENTRYPOINT_NAME = "ptool_register"

def _public_callable_attrs(cls):
    for f in dir(cls):
        attr = getattr(cls, f)
        if not f.startswith("_") and callable(attr):
            yield attr

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

def _git_group_filter(git_server):
    return git_server["group"]

def _make_template(env, s):
    try:
        return env.from_string(unicode(s))
    except jinja2.exceptions.TemplateSyntaxError as e:
        sys.stderr.write("Syntax error \"{}\" in {} at line {}:\n".format(
            e.message,
            "(unknown)" if e.filename is None else e.filename,
            e.lineno))
        lines = s.splitlines()
        for i in range(len(lines)):
            sys.stderr.write("{}: {}\n".format(i + 1, lines[i]))
        raise

class _Template(object):
    def __init__(self, template):
        self._template = template

    def render(self, globals):
        return self._template.render(globals)

def _make_filter(ctx, body):
    b = eval(body)
    return lambda *args, **kwargs: b(ctx, *args, **kwargs)

class TemplateContext(object):
    def __init__(self, loader_dirs, filters, template_dir, globals):
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(loader_dirs),
            undefined=jinja2.StrictUndefined)

        self._env.filters["git_clone_url"] = _git_clone_url_filter
        self._env.filters["git_url"] = _git_url_filter
        self._env.filters["git_group"] = _git_group_filter

        for f in _public_callable_attrs(inflection):
            self._env.filters[f.__name__] = f

        for name, body in filters.iteritems():
            self._env.filters[name] = _make_filter(self, body)

        self._globals = globals
        self._templates_from_strings = {}
        self._templates_from_files = {}
        self._token_lists = {}

        template_module_path = make_path(template_dir, "_ptool.py")
        template_module_name = os.path.basename(template_dir)
        if os.path.isfile(template_module_path):
            module = imp.load_source(template_module_name, template_module_path)
            register_func = getattr(module, _REGISTER_ENTRYPOINT_NAME, None)
            if register_func is None:
                print("WARNING: Template module {} has no ptool entrypoint {}".format(
                    template_module_path,
                    _REGISTER_ENTRYPOINT_NAME))
            else:
                register_func(self)

    @property
    def filters(self): return self._env.filters

    @property
    def globals(self): return self._globals

    def render_from_template_string(self, s, globals):
        template = self._template_from_string(s)
        return template.render(globals)

    def render_from_template_file(self, path, globals):
        template = self._template_from_file(path)
        return template.render(globals)

    def tokenize(self, s):
        token_list = self._token_lists.get(s)
        if token_list is None:
            token_list = TokenList(s)
            self._token_lists[s] = token_list
        return token_list.safe_tokens

    def __getitem__(self, key):
        return self._globals[key]

    def __getattr__(self, name):
        attr = self._globals.get(name)
        if attr is not None:
            return attr
        raise AttributeError("'{}' object has no attribute '{}'".format(type(self).__name__, name))

    def _template_from_string(self, s):
        template = self._templates_from_strings.get(s)
        if template is None:
            template = _Template(_make_template(self._env, s))
            self._templates_from_strings[s] = template
        return template

    def _template_from_file(self, path):
        template = self._templates_from_files.get(path)
        if template is None:
            with open(path, "rt") as f:
                template = _Template(_make_template(self._env, unicode(f.read())))
            self._templates_from_files[path] = template
        return template

def template_tokens(*args):
    """
    keys = []
    for s in args:
        keys.extend(_template_tokens_helper(s))
    return sorted(list(set(keys)))
    """
    return []
