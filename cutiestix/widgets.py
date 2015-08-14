# stdlib
import logging

# external
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

# internal
from . import LICENSE
from . import version
from . import models
from .delegates import BoolDelegate, ResultsDelegate
from .ui.about import Ui_AboutDialog
from .ui.transform import Ui_TransformDialog


LOG = logging.getLogger(__name__)


def center(widget):
    """Centers a widget on the screen."""
    screen = QtGui.QDesktopWidget().screenGeometry()
    me = widget.geometry()

    # Get the centering coordinates
    xpos = (screen.width() - me.width()) / 2
    ypos = (screen.height() - me.height()) / 2

    widget.move(xpos, ypos)


class MainTabView(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(MainTabView, self).__init__(parent)

    def disable_remove(self, index):
        bar = self.tabBar()
        bar.tabButton(index, QtGui.QTabBar.RightSide).setVisible(False)


class ResultsTableView(QtGui.QTableView):
    def __init__(self, parent=None):
        super(ResultsTableView, self).__init__(parent)
        self._init_headers()
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def resize_columns(self):
        self.resizeColumnsToContents()
        h_header = self.horizontalHeader()
        h_header.setStretchLastSection(True)

    def _init_headers(self):
        h_header = self.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Interactive)
        h_header.setStretchLastSection(True)


class AboutDialog(Ui_AboutDialog, QtGui.QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        self._connect_signals()
        self._populate()

    def _connect_signals(self):
        self.btn_close.clicked.connect(self.done)

    def _populate(self):
        import sdv

        # Set the license
        self.txt_license_value.setText(LICENSE)

        # Set version info
        self.label_api_version_value.setText(sdv.__version__)
        self.label_version_value.setText(version.__version__)


class BoolComboBox(QtGui.QComboBox):
    def __init__(self, parent=None):
        super(BoolComboBox, self).__init__(parent)
        self.setModel(models.BoolListModel(self))
        self.setEditable(False)


class FilesTableView(QtGui.QTableView):
    SIGNAL_XML_RESULTS_REQUESTED = QtCore.pyqtSignal(str)
    SIGNAL_BEST_PRACTICES_RESULTS_REQUESTED = QtCore.pyqtSignal(str)
    SIGNAL_PROFILE_RESULTS_REQUESTED = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        LOG.debug("FilesTableView.__init__()")
        super(FilesTableView, self).__init__(parent)
        self._init_models()
        self._init_menus()
        self._init_delegates()
        self._init_headers()
        self._connect_signals()
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def _init_headers(self):
        h_header = self.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Interactive)
        h_header.setStretchLastSection(True)

    def _init_models(self):
        self.source_model = models.ValidateTableModel(self)
        self.setModel(self.source_model)

    def _resize_columns(self):
        self.resizeColumnsToContents()
        h_header = self.horizontalHeader()
        h_header.setStretchLastSection(True)

    def _connect_signals(self):
        model = self.source_model
        model.modelReset.connect(self._resize_columns)
        model.rowsInserted.connect(self._resize_columns)

    def _get_selected_items(self):
        model = self.selectionModel()
        selected = model.selectedRows()

        if not selected:
            return []

        tblmodel = self.source_model
        items = [tblmodel.data(idx, role=Qt.UserRole) for idx in selected]
        return items

    def _show_menu(self, pos):
        # First determine what we can do with the current table selection
        model = self.selectionModel()
        selected = model.hasSelection()
        items = self._get_selected_items()
        count = len(items)

        self.action_open.setEnabled(count == 1)
        self.action_remove.setEnabled(selected)

        first = items[0]
        results = getattr(first, 'results', None)
        
        if count == 1 and results is not None:
            show_xml     = results.xml is not None
            show_bp      = results.best_practices is not None
            show_profile = results.profile is not None
        else:
            show_xml = show_bp = show_profile = False

        self.action_go_to_xml.setVisible(show_xml)
        self.action_go_to_best_practices.setVisible(show_bp)
        self.action_go_to_profile.setVisible(show_profile)

        # Show the menu!
        pos = self.viewport().mapToGlobal(pos)
        self.menu.popup(pos)

    @QtCore.pyqtSlot()
    def _remove_files(self):
        model = self.source_model
        items = self._get_selected_items()
        model.remove_items(items)

    @QtCore.pyqtSlot()
    def _go_to_xml(self):
        items = self._get_selected_items()
        key = items[0].key()
        self.SIGNAL_XML_RESULTS_REQUESTED.emit(key)

    @QtCore.pyqtSlot()
    def _go_to_best_practices(self):
        items = self._get_selected_items()
        key = items[0].key()
        self.SIGNAL_BEST_PRACTICES_RESULTS_REQUESTED.emit(key)

    @QtCore.pyqtSlot()
    def _go_to_profile(self):
        items = self._get_selected_items()
        key = items[0].key()
        self.SIGNAL_PROFILE_RESULTS_REQUESTED.emit(key)

    @QtCore.pyqtSlot()
    def _open_file(self):
        item = next(self._get_selected_items())
        file = item.filename

        LOG.debug("Launching %s...", file)
        url = QtCore.QUrl(file)
        QtGui.QDesktopServices.openUrl(url)

    def _init_menus(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        self.menu = QtGui.QMenu(self)
        self.action_open = self.menu.addAction("Open File...")
        self.action_remove = self.menu.addAction("Remove File")
        self.menu.addSeparator()
        self.action_go_to_xml = self.menu.addAction("XML Results...")
        self.action_go_to_best_practices = self.menu.addAction("Best Practices Results...")
        self.action_go_to_profile = self.menu.addAction("Profile Results...")

        # Wire up signals
        self.action_remove.triggered.connect(self._remove_files)
        self.action_open.triggered.connect(self._open_file)
        self.action_go_to_xml.triggered.connect(self._go_to_xml)
        self.action_go_to_profile.triggered.connect(self._go_to_profile)
        self.action_go_to_best_practices.triggered.connect(self._go_to_best_practices)

    def _init_delegates(self):
        self.setItemDelegateForColumn(2, BoolDelegate(self))
        self.setItemDelegateForColumn(3, BoolDelegate(self))
        self.setItemDelegateForColumn(4, ResultsDelegate(self))

    def clear(self):
        self.source_model.clear()


# Avoid circular imports
from .ui.results import Ui_ResultsWidget


class ResultsWidget(Ui_ResultsWidget, QtGui.QWidget):
    def __init__(self, model, parent=None):
        super(ResultsWidget, self).__init__(parent)
        self.setupUi(self)
        self._init_model(model)
        self._connect_signals()


    def _connect_signals(self):
        table  = self.table_results
        model = table.source_model
        model.modelReset.connect(table.resize_columns)

    def _init_model(self, model):
        table = self.table_results
        table.source_model = model(self)
        table.setModel(table.source_model)

    def set_results(self, fn, results):
        self.label_filename_value.setText(fn)
        self.label_result_value.setText(str(results.is_valid))

        table = self.table_results
        table.source_model.update(results)


class _TransformDialog(Ui_TransformDialog, QtGui.QDialog):
    _transformer = None

    TRANSFORM_SCHEMATRON = 0x01
    TRANSFORM_XSLT       = 0x02

    def __init__(self, worker, parent=None):
        super(_TransformDialog, self).__init__(parent)
        self.setupUi(self)

        self._worker = worker
        self._thread = None
        self._connect_worker()

        # Make sure the user can't click outside of this dialog while it's
        # running.
        self.setModal(True)

    def _connect_worker(self):
        type_  = self._transformer
        worker = self._worker
        thread = QtCore.QThread()

        # Connect the cancel button to our thread
        self.btn_cancel.clicked.connect(thread.quit)

        if type_ == self.TRANSFORM_SCHEMATRON:
            thread.started.connect(worker.to_schematron)
        elif type_ == self.TRANSFORM_XSLT:
            thread.started.connect(worker.to_xslt)
        else:
            raise ValueError("Unknown transformer type: %s" % self._transformer)

        worker.SIGNAL_FINISHED.connect(thread.quit)
        worker.SIGNAL_FINISHED.connect(self.close)
        worker.moveToThread(thread)

        # Do this so the worker and thread don't get garbage collected
        self._thread = thread
        self._worker = worker

    def start_transform(self):
        thread = self._thread
        worker = self._worker

        if not thread and worker:
            raise RuntimeError("Cannot start(). Worker thread not initialized.")

        self._thread.start()


class SchematronTransformDialog(_TransformDialog):
    _transformer = _TransformDialog.TRANSFORM_SCHEMATRON

class XsltTransformDialog(_TransformDialog):
    _transformer = _TransformDialog.TRANSFORM_XSLT


