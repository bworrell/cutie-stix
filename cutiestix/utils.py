# stdlib
import os.path

# stix-validator
import sdv.validators.stix.common as stix_utils


def stix_version(fn):
    return stix_utils.get_version(fn)


def str2bool(s):
    s = str(s).lower()

    if s == "true":
        return True
    elif s == "false":
        return False
    else:
        msg = "Cannot convert %s to boolean." % s
        raise ValueError(msg)


def home():
    return os.path.expanduser("~")  # TODO: Make sure this works on Windows
