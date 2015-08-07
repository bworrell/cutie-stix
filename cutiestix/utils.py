# stdlib
import os.path

# stix-validator
import sdv.validators.stix.common as stix_utils


def stix_version(fn):
    """Return the version of the STIX file.

    Args:
        fn: A STIX document filename.

    Returns:
        A STIX version number.
    """
    return stix_utils.get_version(fn)


def str2bool(s):
    """Return a boolean value corresponding to the input "true"/"false" string.

    PyQt or Qt seems to keep converting my boolean model values into lowercase
    strings so I wrote this to coerce them back into bools.

    I feel like I'm overlooking something super obvious when I stare at this
    function...

    Args:
        s: A string value. Can be "False" or "True" (case-insensitive).

    Returns:
        True or False.

    Raises:
        ValueError: If `s` is not case-insensitive equal to "True" or "False".
    """
    s = str(s).lower()

    if s == "true":
        return True
    elif s == "false":
        return False
    else:
        msg = "Cannot convert %s to boolean." % s
        raise ValueError(msg)


def home():
    """Return the path to the home directory of the current user."""
    return os.path.expanduser("~")  # TODO: Make sure this works on Windows
