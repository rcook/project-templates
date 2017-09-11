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

_PREFIXES = [
    ("==", _EQ),
    (">=", _GE),
    (">", _GT),
    ("<=", _LE),
    ("<", _LT)
]

class VersionConstraint(object):
    @staticmethod
    def parse(s):
        temp = s.strip()
        kind = _EQ
        for prefix, ck in _PREFIXES:
            if temp.startswith(prefix):
                kind = ck
                temp = temp[len(prefix):].strip()
                break

        major, minor = _parse_major_minor(temp)
        version = Version(major, minor)
        return VersionConstraint(kind, version)

    def __init__(self, kind, version):
        self._kind = kind
        self._version = version

    @property
    def kind(self): return self._kind

    @property
    def version(self): return self._version

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

    def satisfies(self, constraint):
        res = _cmp_versions(self, constraint.version)
        if constraint.kind == _EQ:
            return res == _EQ
        if constraint.kind == _GT:
            return res == _GT
        if constraint.kind == _GE:
            return res == _EQ or res == _GT
        if constraint.kind == _LT:
            return res == _LT
        if constraint.kind == _LE:
            return res == _EQ or res == _LT
        raise RuntimeError("Unsupported constraint kind {}".format(constraint.kind))

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
