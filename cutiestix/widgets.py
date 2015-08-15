"""
This module contains custom Qt widgets and widget-related helper functions.
"""

# stdlib
import os
import logging

# stix-validator
import sdv

# PyQT
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
    """Center the `widget` on the screen."""
    screen = QtGui.QDesktopWidget().screenGeometry()
    me = widget.geometry()

    # Get the centering coordinates
    xpos = (screen.width() - me.width()) / 2
    ypos = (screen.height() - me.height()) / 2

    widget.move(xpos, ypos)


class XmlDropMixin(QtCore.QObject):
    """A pseudo-mixin class that contains the logic required for handling
    file drop events.

    Note:
        All classes which utilize this mixin MUST define a
        SIGNAL_FILES_ADDED(list) signal.

    I was hoping to have this class own the signal, but PyQt doesn't seem
    to like mixins owning the signal, so sublasses must redefine the same
    signal.
    """

    SIGNAL_FILES_ADDED = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)

    def _emit(self, files):
        """Emit the SIGNAL_FILES_ADDED signal.

        This is a bit of a hack to make multiple-inheritance work in PyQt.

        See also:
            http://trevorius.com/scrapbook/python/pyqt-multiple-inheritance/

        """
        self.SIGNAL_FILES_ADDED.emit(files)

    def dropEvent(self, event):
        """Catch the drop event and let observers know that we've
        got some files for them do deal with.

        Note:
            This does not work on OSX due to a bug in Qt, so we check the
            platform before emitting.
        """
        LOG.debug("Caught dropEvent!")
        mdata = event.mimeData()
        files = [str(url.toLocalFile()) for url in mdata.urls()]
        files = [path for path in files if os.path.exists(path)]

        self._emit(files)

    def dragEnterEvent(self, event):
        """Accept any drag enter event."""
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """Accept any drag move event."""
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """Accept any drag leave event."""
        event.accept()


class XmlFileDropWidget(QtGui.QWidget, XmlDropMixin):
    """A QWidget which accepts file drops from outside the application.

    Signals:
        SIGNAL_FILES_ADDED (list): Emits a list of filenames that the user has
            attempted to drag into this widget.
    """

    SIGNAL_FILES_ADDED = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(XmlFileDropWidget, self).__init__(parent)
        self.setAcceptDrops(True)


class MainTabView(QtGui.QTabWidget):
    """The main window tab view.

    The intent of this was to hide the close "X" button on the first tab,
    but allow it on other validation result tabs.

    I have decided to leave all tabs as unclosable, so disable_remove() is
    no longer called and this class has sorta lost its usefulness (FOR NOW!).
    """

    def __init__(self, parent=None):
        super(MainTabView, self).__init__(parent)

    def disable_remove(self, index):
        bar = self.tabBar()
        bar.tabButton(index, QtGui.QTabBar.RightSide).setVisible(False)


class ResultsTableView(QtGui.QTableView):
    """A TableView class designed to contain and display validation results."""

    def __init__(self, parent=None):
        super(ResultsTableView, self).__init__(parent)
        self._init_headers()
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    @QtCore.pyqtSlot()
    def resize_columns(self):
        """A slot which resizes all the columns to fit their contents and
        stretches the last column.

        Normally, if you resize the columns to contents, the last stretched
        column becomes unstretched.
        """
        self.resizeColumnsToContents()
        h_header = self.horizontalHeader()
        h_header.setStretchLastSection(True)

    def _init_headers(self):
        """Initialize the table view's horizontal headers."""
        h_header = self.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Interactive)
        h_header.setStretchLastSection(True)


class AboutDialog(Ui_AboutDialog, QtGui.QDialog):
    """Displays version/license information about cutiestix and the
    underlying APIs.
    """

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        self._connect_signals()
        self._populate()

    def _connect_signals(self):
        """Connect ui widget signals to handlers."""
        self.btn_close.clicked.connect(self.done)

    def _populate(self):
        """Add the version information to the appropriate QLabels."""
        self.txt_license_value.setText(LICENSE)
        self.label_api_version_value.setText(sdv.__version__)
        self.label_version_value.setText(version.__version__)


class FilesTableView(QtGui.QTableView, XmlDropMixin):
    """Main table which shows file information and validation options.

    Files can be dropped into this view from external sources and they
    will be added to the underlying model.

    Signals:
        SIGNAL_XML_RESULTS_REQUESTED (str): Emits the key of the table model
            item which a user has selected to review its XML validation
            results.
        SIGNAL_BEST_PRACTICES_RESULTS_REQUESTD (str): Emits the key of the
            table model item which a user has selected to review its best
            practices validation results.
        SIGNAL_PROFILE_RESULTS_REQUESTED (str): Emits the key of the table model
            item which a user has selected to review its STIX Profile validation
            results.
        SIGNAL_FILES_ADDED (list): Emits a list of filenames that the user has
            attempted to drag into the table.
    """
    SIGNAL_XML_RESULTS_REQUESTED = QtCore.pyqtSignal(str)
    SIGNAL_BEST_PRACTICES_RESULTS_REQUESTED = QtCore.pyqtSignal(str)
    SIGNAL_PROFILE_RESULTS_REQUESTED = QtCore.pyqtSignal(str)
    SIGNAL_FILES_ADDED = QtCore.pyqtSignal(list)

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

    @QtCore.pyqtSlot()
    def _resize_columns(self):
        self.resizeColumnsToContents()
        h_header = self.horizontalHeader()
        h_header.setStretchLastSection(True)

    def _connect_signals(self):
        model = self.source_model
        model.modelReset.connect(self._resize_columns)
        model.rowsInserted.connect(self._resize_columns)

    def _get_selected_items(self):
        """Return the table model items for the currently selected rows.

        Returns:
            A list of ValidateTableItem objects or an empty list if no rows
            are selected.
        """
        model    = self.selectionModel()
        selected = model.selectedRows()

        if not selected:
            return []

        tblmodel = self.source_model
        items    = [tblmodel.data(idx, role=Qt.UserRole) for idx in selected]

        return items

    def _show_menu(self, pos):
        """Show the right click menu for a table row.

        If a user has only one row selected, allow them to open the
        corresponding file and view results if there are any.

        If a user has one or more rows selected, allow them to remove the
        rows.
        """
        items = self._get_selected_items()
        count = len(items)

        self.action_open.setEnabled(count == 1)
        self.action_remove.setEnabled(count)

        first = items[0]
        results = getattr(first, 'results', None)
        
        if count != 1 or results is None or isinstance(results, Exception):
            show_xml = show_bp = show_profile = False
        else:
            show_xml     = results.xml is not None
            show_bp      = results.best_practices is not None
            show_profile = results.profile is not None

        self.action_go_to_xml.setVisible(show_xml)
        self.action_go_to_best_practices.setVisible(show_bp)
        self.action_go_to_profile.setVisible(show_profile)

        # Show the menu!
        pos = self.viewport().mapToGlobal(pos)
        self.menu.popup(pos)

    @QtCore.pyqtSlot()
    def _remove_selected(self):
        """Remove the selected rows from the table."""
        model = self.source_model
        items = self._get_selected_items()
        model.remove_items(items)

    @QtCore.pyqtSlot()
    def _go_to_xml(self):
        """Signal to observers that the user has requested to view the XML
        validation results for the selected item.
        """
        items = self._get_selected_items()
        key = items[0].key()
        self.SIGNAL_XML_RESULTS_REQUESTED.emit(key)

    @QtCore.pyqtSlot()
    def _go_to_best_practices(self):
        """Signal to observers that the user has requested to view the best
        practice validation results for the selected item.
        """
        items = self._get_selected_items()
        key = items[0].key()
        self.SIGNAL_BEST_PRACTICES_RESULTS_REQUESTED.emit(key)

    @QtCore.pyqtSlot()
    def _go_to_profile(self):
        """Signal to observers that the user has requested to view the STIX
        Profile validation results for the selected item.
        """
        items = self._get_selected_items()
        key = items[0].key()
        self.SIGNAL_PROFILE_RESULTS_REQUESTED.emit(key)

    @QtCore.pyqtSlot()
    def _open_file(self):
        """Launch the selected row's associated XML file in an external
        viewer.
        """
        item = next(self._get_selected_items())
        file = item.filename

        LOG.debug("Launching %s...", file)
        url = QtCore.QUrl.fromLocalFile(file)
        QtGui.QDesktopServices.openUrl(url)

    def _init_menus(self):
        """Create and connect the right-click menus for the table."""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        self.menu = QtGui.QMenu(self)
        self.action_open = self.menu.addAction("Open File...")
        self.action_remove = self.menu.addAction("Remove File")
        self.menu.addSeparator()
        self.action_go_to_xml = self.menu.addAction("View XML Results...")
        self.action_go_to_best_practices = self.menu.addAction("View Best Practices Results...")
        self.action_go_to_profile = self.menu.addAction("View Profile Results...")

        # Wire up signals
        self.action_remove.triggered.connect(self._remove_selected)
        self.action_open.triggered.connect(self._open_file)
        self.action_go_to_xml.triggered.connect(self._go_to_xml)
        self.action_go_to_profile.triggered.connect(self._go_to_profile)
        self.action_go_to_best_practices.triggered.connect(self._go_to_best_practices)

    def _init_delegates(self):
        """Assign delegates for our validation options rows."""
        self.setItemDelegateForColumn(2, BoolDelegate(self))
        self.setItemDelegateForColumn(3, BoolDelegate(self))
        self.setItemDelegateForColumn(4, ResultsDelegate(self))

    def clear(self):
        """Remove all entries from the table."""
        self.source_model.clear()


# Avoid circular imports: ui.results imports ResultsTableView.
from .ui.results import Ui_ResultsWidget


class ResultsWidget(Ui_ResultsWidget, QtGui.QWidget):
    """A general-purpose Widget for displaying validation results.

    Args:
        model: An instance of models.ValidationResultsTableModel or
            models.BestPracticeResultsTableModel.
        parent: A QObject parent for this widget.
    """

    def __init__(self, model, parent=None):
        super(ResultsWidget, self).__init__(parent)
        self.setupUi(self)
        self._init_model(model)
        self._connect_signals()

    def _connect_signals(self):
        """Connect ui component signals.

        Every time the underlying table model is reset, we resize the columns
        to fit their contents.
        """
        table  = self.table_results
        model = table.source_model
        model.modelReset.connect(table.resize_columns)

    def _init_model(self, model):
        """Sets the source model for this table view.

        Args:
            model: An instance of models.ValidationResultsTableModel or
                models.BestPracticeResultsTableModel.
        """
        table = self.table_results
        table.source_model = model(self)
        table.setModel(table.source_model)

    def set_results(self, fn, results):
        """Sets the result data for the table and updates the displayed
        file information.

        Note:
            The results must be "understood" by the underlying model. So, if
            the model is a ValidationResultsTableModel you cannot pass in a
            BestPracticeValidationResults object.

        Args:
            fn: The filename associated with the results.
            results: An instance of sdv.validators.xml_schema.XmlValidationResults,
                sdv.validators.stix.best_practice.BestPracticeValidationResults,
                or sdv.validators.stix.profile.ProfileValidationResults.
        """
        self.label_filename_value.setText(fn)
        self.label_result_value.setText(str(results.is_valid))

        table = self.table_results
        table.source_model.update(results)


class _TransformDialog(Ui_TransformDialog, QtGui.QDialog):
    """Abstract base class for a dialog that displays Schematron/XSLT
    transformation progress.
    """
    def __init__(self, worker, parent=None):
        super(_TransformDialog, self).__init__(parent)
        self.setupUi(self)

        self._worker = worker
        self._thread = None
        self._connect_worker()

        # Make sure the user can't click outside of this dialog while it's
        # running.
        self.setModal(True)

    def _worker_thread_slot(self, worker):
        """Return a slot to connect the QThread.started signal to."""
        raise NotImplementedError()

    def _connect_worker(self):
        """Create a QThread and move the worker object to that thread."""
        worker = self._worker
        thread = QtCore.QThread()  # no parent!

        # Connect the cancel button to our thread
        self.btn_cancel.clicked.connect(thread.quit)

        # Connect the QThread to the concrete impl defined slot.
        work_slot = self._worker_thread_slot(worker)
        thread.started.connect(work_slot)

        # Quit the thread and close this window when the work is done.
        worker.SIGNAL_FINISHED.connect(thread.quit)
        worker.SIGNAL_FINISHED.connect(self.close)

        # New-style QThread management. Move the worker to the thread.
        worker.moveToThread(thread)

        # Do this so the worker and thread don't get garbage collected
        self._thread = thread
        self._worker = worker

    def start_transform(self):
        """Start the QThread and perform the transform."""
        thread = self._thread
        worker = self._worker

        if not thread and worker:
            raise RuntimeError("Cannot start(). Worker thread not initialized.")

        self._thread.start()


class SchematronTransformDialog(_TransformDialog):
    """Concrete implementation of _TransformDialog.

    This is displayed when a user transforms a STIX Profile to Schematron.
    """
    def _worker_thread_slot(self, worker):
        return worker.to_schematron


class XsltTransformDialog(_TransformDialog):
    """Concrete implementation of _TransformDialog.

    This is displayed when a user transforms a STIX Profile to XSLT.
    """
    def _worker_thread_slot(self, worker):
        return worker.to_xslt


