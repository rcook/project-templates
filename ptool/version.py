# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

_EQ = 0
_GE = 1
_GT = 2
_LE = 3
_LT = 4
_CONSTRAINT_KINDS = {
    "==": _EQ,
    ">=": _GE,
    ">": _GT,
    "<=": _LE,
    "<": _LT
}
_AND_OP = "&&"

def _constraint_kind(s):
    kind = _CONSTRAINT_KINDS.get(s)
    if kind is not None:
        return kind
    raise RuntimeError("Unsupported constraint kind {}".format(s))

def _parse_major_minor(s):
    parts = map(int, s.split("."))
    if len(parts) != 2:
        raise RuntimeError("Invalid version string \"{}\"".format(s))
    return parts

def _cmp_versions(a, b):
    res = cmp(a.major, b.major)
    if res < 0: return _LT
    if res > 0: return _GT
    res = cmp(a.minor, b.minor)
    if res < 0: return _LT
    if res > 0: return _GT
    return _EQ

class _AndVersionConstraint(object):
    def __init__(self, constraints):
        self._constraints = constraints

    def is_satisfied_by(self, version):
        for constraint in self._constraints:
            if not constraint.is_satisfied_by(version):
                return False
        return True

    def __repr__(self):
        return " ".join(map(str, self._constraints))

class _SimpleVersionConstraint(object):
    def __init__(self, kind, version):
        self._kind = kind
        self._version = version

    def is_satisfied_by(self, version):
        res = _cmp_versions(version, self._version)
        if self._kind == _EQ:
            return res == _EQ
        if self._kind == _GT:
            return res == _GT
        if self._kind == _GE:
            return res == _EQ or res == _GT
        if self._kind == _LT:
            return res == _LT
        if self._kind == _LE:
            return res == _EQ or res == _LT
        raise RuntimeError("Unsupported constraint kind {}".format(self._kind))

    def __repr__(self):
        if self._kind == _EQ:
            temp = "=="
        elif self._kind == _GE:
            temp = ">="
        elif self._kind == _GT:
            temp = ">"
        elif self._kind == _LE:
            temp = "<="
        elif self._kind == _LT:
            temp = "<"
        else:
            raise RuntimeError("Unsupported constraint kind {}".format(self._kind))
        return "{} {}".format(temp, self._version)

class Version(object):
    @staticmethod
    def from_git(git):
        description = git.describe().strip()

        fragments = description.split("-")
        if len(fragments) == 1:
            version_str = fragments[0]
            commit_count = None
            commit_hash = None
        elif len(fragments) == 3:
            version_str, commit_count_str, commit_hash_with_prefix = fragments

            commit_count = int(commit_count_str)

            if not commit_hash_with_prefix.startswith("g"):
                raise RuntimeError("Invalid prefixed commit hash \"{}\"".format(commit_hash_with_prefix))

            commit_hash = commit_hash_with_prefix[1:]
        else:
            raise RuntimeError("Could not parse Git description \"{}\"".format(description))

        if not version_str.startswith("v"):
            raise RuntimeError("Invalid version string \"{}\"".format(version_srt))

        major, minor = _parse_major_minor(version_str[1:])
        return Version(major, minor, commit_count, commit_hash)

    def __init__(self, major, minor, commit_count=None, commit_hash=None):
        self._major = major
        self._minor = minor
        self._commit_count = commit_count
        self._commit_hash = commit_hash

    @property
    def major(self): return self._major

    @property
    def minor(self): return self._minor

    @property
    def commit_count(self): return self._commit_count

    @property
    def commit_hash(self): return self._commit_hash

    def __repr__(self):
        s = "v{}.{}".format(self._major, self._minor)
        if self._commit_count is not None:
            s += "-{}".format(self._commit_count)
            if self._commit_hash is not None:
                s += "-g{}".format(self._commit_hash)
        return s

def parse_version_constraint(s):
    i = iter(s.strip().split())
    constraints = []
    while True:
        token = next(i)
        kind = _constraint_kind(token)
        version_str = next(i)
        major, minor = _parse_major_minor(version_str)
        version = Version(major, minor)
        constraints.append(_SimpleVersionConstraint(kind, version))

        token = next(i, None)
        if token is None:
            break
        elif token != _AND_OP:
            raise RuntimeError("Invalid token {}".format(token))

    constraint_count = len(constraints)
    if constraint_count == 0:
        raise RuntimeError("Invalid constraint {}".format(s))
    elif constraint_count == 1:
        return constraints[0]
    else:
        return _AndVersionConstraint(constraints)
