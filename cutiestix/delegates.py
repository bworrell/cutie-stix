"""View delegates."""

import logging

from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from . import utils

LOG = logging.getLogger(__name__)


class BoolEditableDelegate(QtGui.QStyledItemDelegate):
    def displayText(self, value, locale=None):
        value = utils.str2bool(value.toPyObject())
        return super(BoolEditableDelegate, self).displayText(str(value), locale)


    def setEditorData(self, widget, index):
        value = index.model().data(index, Qt.EditRole)
        bool  = utils.str2bool(value)
        widget.setCurrentIndex(int(bool))

    def createEditor(self, parent, option, index):
        from .widgets import BoolComboBox  # circular import
        return BoolComboBox(parent)
