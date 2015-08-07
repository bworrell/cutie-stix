import logging

from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from . import models
from .delegates import BoolEditableDelegate


LOG = logging.getLogger(__name__)


def center(widget):
    """Centers the widget on the screen."""
    screen = QtGui.QDesktopWidget().screenGeometry()
    me = widget.geometry()

    # Get the centering coordinates
    xpos = (screen.width() - me.width()) / 2
    ypos = (screen.height() - me.height()) / 2

    widget.move(xpos, ypos)


class BestPracticeTableView(QtGui.QTableView):
    pass


class BoolComboBox(QtGui.QComboBox):
    def __init__(self, parent=None):
        super(BoolComboBox, self).__init__(parent)
        self.setModel(models.BoolListModel(self))
        self.setEditable(False)


class FilesTableView(QtGui.QTableView):
    def __init__(self, parent):
        LOG.debug("FilesTableView.__init__()")
        super(FilesTableView, self).__init__(parent)
        self._init_menus()
        self._init_headers()
        self._init_delegates()
        self.resizeColumnsToContents()

    def _init_headers(self):
        v_header = self.verticalHeader()
        h_header = self.horizontalHeader()
        h_header.setStretchLastSection(True)

    def show_menu(self, pos):
        pos = self.viewport().mapToGlobal(pos)
        self.menu.popup(pos)


    def _init_menus(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

        self.menu = QtGui.QMenu(self)
        self.action_foo = self.menu.addAction("Foo")
        self.action_bar = self.menu.addAction("Bar")

    def _init_delegates(self):
        self.setItemDelegateForColumn(2, BoolEditableDelegate(self))
        self.setItemDelegateForColumn(3, BoolEditableDelegate(self))
        self.setItemDelegateForColumn(4, BoolEditableDelegate(self))

    # Dragging files into the view doesn't work because of:
    # https://bugreports.qt.io/browse/QTBUG-40449
    # def dropEvent(self, event):
    #     LOG.debug("Caught dropEvent!")
    #     mdata = event.mimeData()
    #
    #     # filenames = [str(url.toLocalFile()) for url in mdata.urls()]
    #     #
    #     # for fn in filenames:
    #     #     printfile(fn)
    #     #
    #     #
    #     # LOG.debug(mdata.text())
    #     # LOG.debug(", ".join(str(x.path()) for x in mdata.urls()))
    #
    #
    # def dragEnterEvent(self, event):
    #     LOG.debug("FilesTableView.dragEnterEvent()")
    #     event.acceptProposedAction()
    #
    # def dragMoveEvent(self, event):
    #     LOG.debug("FilesTableView.dragMoveEvent()")
    #     event.acceptProposedAction()
    #
    # def dragLeaveEvent(self, event):
    #     LOG.debug("FilesTableView.dragLeaveEvent()")
    #     event.accept()