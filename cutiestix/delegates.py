"""
This module contains Qt Delegates which define how to render or present
View data.
"""

# external
from PyQt4 import QtGui

# internal
from . import utils


class ResultsDelegate(QtGui.QStyledItemDelegate):
    """A validation result delegate.

    This is used to render the stix-validator ValidationResults object which
    is attached to model items during validation.

    If an exception occurred during validition, the word "Error" will be
    presented.
    """

    def displayText(self, value, locale=None):
        """Return the text to display for a stix-validator ValidationResults
        object that is attached to a model item after validation..
        """
        if value is None:
            return ""

        value   = value.toPyObject()

        if isinstance(value, Exception):
            result = "Error"
        else:
            results = value.xml, value.profile, value.best_practices
            invalid = any(getattr(x, 'is_valid', None) is False for x in results)
            result  = "Invalid" if invalid else "Valid"

        return super(ResultsDelegate, self).displayText(result, locale)


class BoolDelegate(QtGui.QStyledItemDelegate):
    """Render boolean data in a model.

    By default, True will be rendered as "true" and False as "false." This
    forces the intended capitalization.
    """
    def displayText(self, value, locale=None):
        value = utils.str2bool(value.toPyObject())
        return super(BoolDelegate, self).displayText(str(value), locale)
