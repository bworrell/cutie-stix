# builtin
import logging

# external
from PyQt4 import QtGui, QtCore

# internal
from . import version
from . import widgets
from . import worker
from . import utils
from .ui.window import Ui_MainWindow


LOG = logging.getLogger(__name__)

WIDTH  = 1280
HEIGHT = 768

INDEX_ADD_FILES  = 0
INDEX_VIEW_FILES = 1


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self._populate()
        self._connect_ui()

        # Set the size of the window
        self.resize(WIDTH, HEIGHT)

        # Center the UI on the screen
        widgets.center(self)

    def _populate(self):
        self.tab_widget.removeTab(1)
        self.stacked_main.setCurrentIndex(INDEX_ADD_FILES)

        title = "STIX Document Validator v%s" % (version.__version__)
        self.setWindowTitle(title)

    def _connect_ui(self):
        # Buttons in the main window
        self.btn_validate.clicked.connect(self._handle_btn_validate_clicked)
        self.btn_clear.clicked.connect(self._handle_btn_clear_clicked)

        # Main menu
        self.action_add_file.triggered.connect(self._handle_add_files)

        # Validate file table
        model = self.table_files.source_model
        model.modelReset.connect(self._handle_file_table_model_changed)
        model.rowsInserted.connect(self._handle_file_table_model_changed)
        model.rowsRemoved.connect(self._handle_file_table_model_changed)

    @QtCore.pyqtSlot()
    def _handle_file_table_model_changed(self):
        model = self.table_files.source_model
        size  = model.rowCount()

        if size == 0:
            self.stacked_main.setCurrentIndex(INDEX_ADD_FILES)
        else:
            self.stacked_main.setCurrentIndex(INDEX_VIEW_FILES)

    def _add_files(self, filenames):
        stixdocs  = [f for f in filenames if utils.is_stix(f)]
        nonstix   = [f for f in filenames if f not in stixdocs]

        LOG.debug("Adding: %s", stixdocs)
        model = self.table_files.source_model

        for file in stixdocs:
            model.add(file)

        LOG.warn("Not STIX files. Skipping: %s", nonstix)

    @QtCore.pyqtSlot()
    def _handle_add_files(self):
        LOG.debug("Adding files")

        files = QtGui.QFileDialog.getOpenFileNames(
            parent=self,
            caption="Add STIX Files",
            directory=__file__,
        )

        LOG.debug(files)
        filenames = [str(f) for f in files]
        self._add_files(filenames)

    @QtCore.pyqtSlot(int, float)
    def _handle_validation_updated(self, itemid, progress):
        LOG.debug("%d completed. Total progress: %f", itemid, progress)
        self.progress_validation.setValue(int(progress*100))

    @QtCore.pyqtSlot()
    def _handle_validation_started(self):
        self.group_actions.setEnabled(False)
        self.group_options.setEnabled(False)
        self.progress_validation.setValue(0)

    @QtCore.pyqtSlot()
    def _handle_validation_complete(self):
        LOG.debug("Validation completed.")
        self.progress_validation.setValue(100)
        self.group_actions.setEnabled(True)
        self.group_options.setEnabled(True)

    @QtCore.pyqtSlot()
    def _handle_btn_validate_clicked(self):
        self.thread = QtCore.QThread()
        self.worker = worker.ValidationWorker()

        # thread      = QtCore.QThread()
        # validator   = worker.ValidationWorker()
        model       = self.table_files.source_model

        # Add validation tasks to our worker
        self.worker.add_tasks(model.items())

        # Connect the QThread signals
        self.thread.started.connect(self._handle_validation_started)
        self.thread.started.connect(self.worker.validate)
        self.thread.finished.connect(self._handle_validation_complete)

        # Connect the ValidationWorker signals
        self.worker.SIGNAL_VALIDATED.connect(self._handle_validation_updated)
        self.worker.SIGNAL_FINISHED.connect(self.thread.quit)

        # Start the thread
        self.worker.moveToThread(self.thread)
        LOG.info("Main executing in thread %d", QtCore.QThread.currentThreadId())
        self.thread.start()

    @QtCore.pyqtSlot()
    def _handle_btn_clear_clicked(self):
        LOG.debug("handle_btn_clear_clicked()")
        self.table_files.clear()