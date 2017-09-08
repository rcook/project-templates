# -----------------------------------------------------------------------------
#
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# -----------------------------------------------------------------------------

import argparse

def parse_key_value_pair(s):
    fragments = s.split("=")
    if len(fragments) != 2 or len(fragments[0]) < 1:
        raise argparse.ArgumentTypeError("Must be a key-value pair")
    return fragments[0], fragments[1]
