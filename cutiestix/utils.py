"""
Helper utilities that have use throughout the cutiestix codebase.
"""

# stdlib
import os

# external
import sdv.utils
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
    return os.path.expanduser("~")


def is_stix(fn):
    """Attempts to determine if the input `doc` is a STIX XML instance document.
    If the root-level element falls under a namespace which starts with
    ``http://stix.mitre.org``, this will return True.

    """
    try:
        return sdv.utils.is_stix(fn)
    except Exception:
        return False


def is_iterable(x):
    """Returhs True if `x` is iterable.

    Note:
        This won't work in Python 3 since strings have __iter__ there.
    """
    return hasattr(x, "__iter__")


def list_xml_files(files):
    """Filter the input files and return only the XML file paths.

    Args:
        files: A filename, dirname, or list of filenames/dirnames.

    Returns:
        A list of XML filenames.
    """
    if not is_iterable(files):
        files = [files]

    return sdv.utils.get_xml_files(files, recursive=True)
