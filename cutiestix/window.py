# builtin
import logging

# external
from PyQt4 import QtGui, QtCore

# internal
from . import widgets
from . import models
from .ui.window import Ui_MainWindow


LOG = logging.getLogger(__name__)


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self._populate()
        self._connect_ui()

        # Center the UI on the screen
        widgets.center(self)

    def _populate(self):
        self.tab_widget.removeTab(1)

    def _connect_ui(self):
        # Buttons in the main window
        self.btn_validate.clicked.connect(self._handle_btn_validate_clicked)
        self.btn_clear.clicked.connect(self._handle_btn_clear_clicked)

        # Main menu
        self.action_add_file.triggered.connect(self._handle_add_files)

    @QtCore.pyqtSlot()
    def _handle_add_files(self):
        LOG.debug("Adding files")
        dialog = QtGui.QFileDialog(self)


    @QtCore.pyqtSlot()
    def _handle_btn_validate_clicked(self):
        LOG.debug("handle_btn_validate_clicked()")

    @QtCore.pyqtSlot()
    def _handle_btn_clear_clicked(self):
        LOG.debug("handle_btn_clear_clicked()")
        self.table_files.clear()