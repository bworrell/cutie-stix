"""View delegates."""

import logging

from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from . import utils

LOG = logging.getLogger(__name__)


class ResultsDelegate(QtGui.QStyledItemDelegate):
    def displayText(self, value, locale=None):

        if value is None:
            result = ""
        else:
            value   = value.toPyObject()
            results = value.xml, value.profile, value.best_practices
            invalid = any(getattr(x, 'is_valid', None) is False for x in results)
            result  = "Invalid" if invalid else "Valid"

        return super(ResultsDelegate, self).displayText(result, locale)


class BoolDelegate(QtGui.QStyledItemDelegate):
    def displayText(self, value, locale=None):
        value = utils.str2bool(value.toPyObject())
        return super(BoolDelegate, self).displayText(str(value), locale)


class BoolEditableDelegate(BoolDelegate):
    def setEditorData(self, widget, index):
        value = index.model().data(index, Qt.EditRole)
        bool  = utils.str2bool(value)
        idx   = 0 if bool else 1
        widget.setCurrentIndex(idx)

    def createEditor(self, parent, option, index):
        from .widgets import BoolComboBox  # circular import
        return BoolComboBox(parent)
