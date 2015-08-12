# stdlib
import os
import logging

# external
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

# internal
from . import widgets
from . import models
from . import worker
from . import settings
from . import utils
from .ui.window import Ui_MainWindow


LOG = logging.getLogger(__name__)

WIDTH  = 1280
HEIGHT = 768

INDEX_ADD_FILES  = 0
INDEX_VIEW_FILES = 1

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MainWindow(Ui_MainWindow, QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self._result_tabs = {}

        self.setupUi(self)
        self._populate()
        self._connect_ui()

        # Set the size of the window
        self.resize(WIDTH, HEIGHT)

        # Center the UI on the screen
        widgets.center(self)

    def _populate(self):
        # Remove the unwanted, empty tab
        self.tab_widget.removeTab(1)

        # Prevent closing the first tab
        # self.tab_widget.disable_remove(0)

        # Add a permanent status bar
        self.status = QtGui.QLabel()
        self.statusBar().addPermanentWidget(self.status)

        # Update the status bar and make sure we're on the right stacked
        # widget.
        self._handle_file_table_model_changed()

    def _connect_ui(self):
        # Buttons in the main window
        self.btn_validate.clicked.connect(self._handle_btn_validate_clicked)
        self.btn_clear.clicked.connect(self._handle_btn_clear_clicked)

        # Main menu
        self.action_add_file.triggered.connect(self._handle_add_files)
        self.action_add_directory.triggered.connect(self._handle_add_directory)
        self.action_set_schema_dir.triggered.connect(self._handle_set_schema_dir)
        self.action_set_stix_profile.triggered.connect(self._handle_set_profile)
        self.action_about.triggered.connect(self._show_about)
        self.action_profile_to_schematron.triggered.connect(self._handle_to_schematron)
        self.action_profile_to_xslt.triggered.connect(self._handle_to_xslt)

        # Validate file table
        model = self.table_files.source_model
        model.modelReset.connect(self._handle_file_table_model_changed)
        model.rowsInserted.connect(self._handle_file_table_model_changed)
        model.rowsRemoved.connect(self._handle_file_table_model_changed)

        table = self.table_files
        table.SIGNAL_XML_RESULTS_REQUESTED.connect(self._handle_xml_results_requested)
        table.SIGNAL_PROFILE_RESULTS_REQUESTED.connect(self._handle_profile_results_requested)
        table.SIGNAL_BEST_PRACTICES_RESULTS_REQUESTED.connect(self._handle_best_practices_results_requested)

        # Main Options
        bpstate = self.check_best_practices.stateChanged
        bpstate.connect(self._handle_check_best_practices_state_changed)
        exschema = self.check_external_schemas.stateChanged
        exschema.connect(self._handle_check_external_schemas_state_changed)
        pstate = self.check_profile.stateChanged
        pstate.connect(self._handle_check_profile_state_changed)

    def _reset_result_tabs(self):
        for tab in self._result_tabs.itervalues():
            idx = self.tab_widget.indexOf(tab)
            self.tab_widget.removeTab(idx)

        # Used for displaying results
        self._result_tabs['xml'] = widgets.ResultsWidget(models.ValidationResultsTableModel)
        self._result_tabs['profile'] = widgets.ResultsWidget(models.ValidationResultsTableModel)
        self._result_tabs['best_practices'] = widgets.ResultsWidget(models.BestPracticeResultsTableModel)

    @QtCore.pyqtSlot()
    def _show_about(self):
        about = widgets.AboutDialog(self)
        about.exec_()

    @QtCore.pyqtSlot()
    def _handle_file_table_model_changed(self):
        model = self.table_files.source_model
        size  = model.rowCount()

        if size == 0:
            self.stacked_main.setCurrentIndex(INDEX_ADD_FILES)
            self._reset_result_tabs()
            self.update_status("No Files Added.")
        else:
            self.stacked_main.setCurrentIndex(INDEX_VIEW_FILES)
            self.update_status("Ready.")

    def _add_files(self, filenames):
        stixdocs  = [f for f in filenames if utils.is_stix(f)]
        nonstix   = [f for f in filenames if f not in stixdocs]

        LOG.debug("Adding: %s", stixdocs)
        model = self.table_files.source_model

        for file in stixdocs:
            model.add(file)

        if nonstix:
            LOG.warn("Skipping non-STIX files: %s", nonstix)

    @QtCore.pyqtSlot()
    def _handle_add_files(self):
        LOG.debug("Adding files")

        files = QtGui.QFileDialog.getOpenFileNames(
            parent=self,
            caption="Add STIX Files",
            filter="XML (*.xml)",
            directory=BASE_DIR,
        )

        filenames = [str(f) for f in files]
        self._add_files(filenames)

    @QtCore.pyqtSlot()
    def _handle_add_directory(self):
        LOG.debug("Adding directory")

        xmldir = QtGui.QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select STIX Document Directory",
            directory=BASE_DIR,
        )

        if not xmldir:
            LOG.debug("User cancelled out of xml directory selection")
        else:
            xml_files = utils.list_xml_files(str(xmldir))
            self._add_files(xml_files)

    @QtCore.pyqtSlot()
    def _handle_set_schema_dir(self):
        LOG.debug("Setting schema dir")

        schemadir = QtGui.QFileDialog.getExistingDirectory(
            parent=self,
            caption="Set Schema Directory",
            directory=BASE_DIR,
        )

        if not schemadir:
            LOG.debug("User cancelled out of schema dir selection.")
        else:
            LOG.debug("User selected schema dir %s", schemadir)
            settings.XML_SCHEMA_DIR = str(schemadir)
            self.check_external_schemas.setEnabled(True)
            self.check_external_schemas.setChecked(True)

    @QtCore.pyqtSlot()
    def _handle_set_profile(self):
        LOG.debug("Setting STIX Profile")

        profile = QtGui.QFileDialog.getOpenFileName(
            parent=self,
            caption="Select STIX Profile",
            filter="Excel (*.xlsx)",
            directory=BASE_DIR,
        )

        if not profile:
            LOG.debug("User cancelled out of STIX Profile selection.")
        else:
            LOG.debug("User selected profile %s", profile)
            settings.STIX_PROFILE_FILENAME = str(profile)
            self.check_profile.setEnabled(True)
            self.check_profile.setChecked(True)

    @QtCore.pyqtSlot(int)
    def _handle_check_profile_state_changed(self, state):
        if state == Qt.Checked:
            enabled = True
        elif state == Qt.Unchecked:
            enabled = False
        else:
           return

        model = self.table_files.source_model
        model.enable_profile(enabled)
        settings.VALIDATE_STIX_PROFILE = enabled

    @QtCore.pyqtSlot(int)
    def _handle_check_external_schemas_state_changed(self, state):
        if state == Qt.Checked:
            enabled = True
        elif state == Qt.Unchecked:
            enabled = False
        else:
           return

        model = self.table_files.source_model
        model.reset_results()
        settings.VALIDATE_EXTERNAL_SCHEMAS = enabled

    @QtCore.pyqtSlot(int)
    def _handle_check_best_practices_state_changed(self, state):
        if state == Qt.Checked:
            enabled = True
        elif state == Qt.Unchecked:
            enabled = False
        else:
           return

        model = self.table_files.source_model
        model.enable_best_practices(enabled)
        settings.VALIDATE_STIX_BEST_PRACTICES = enabled

    @QtCore.pyqtSlot(str)
    def _handle_validating(self, fn):
        fn = os.path.split(str(fn))[-1]
        msg = "Validating {file}...".format(file=fn)
        self.update_status(msg)

    @QtCore.pyqtSlot(str, float)
    def _handle_validation_updated(self, itemid, progress):
        LOG.debug("%s completed. Total progress: %f", itemid, progress)
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
        self.update_status("Ready.")
        self.group_actions.setEnabled(True)
        self.group_options.setEnabled(True)

    def _validate_files(self):
        self.thread = QtCore.QThread()
        self.worker = worker.ValidationWorker()

        # Add validation tasks to our worker
        model = self.table_files.source_model
        self.worker.add_tasks(model.items())

        # Connect the QThread signals
        self.thread.started.connect(self._handle_validation_started)
        self.thread.started.connect(self.worker.validate)
        self.thread.finished.connect(self._handle_validation_complete)

        # Connect the ValidationWorker signals
        self.worker.SIGNAL_VALIDATING.connect(self._handle_validating)
        self.worker.SIGNAL_VALIDATED.connect(self._handle_validation_updated)
        self.worker.SIGNAL_FINISHED.connect(self.thread.quit)

        # Start the thread
        LOG.debug("Main executing in thread %d", QtCore.QThread.currentThreadId())
        self.worker.moveToThread(self.thread)
        self.thread.start()

    @QtCore.pyqtSlot()
    def _handle_btn_validate_clicked(self):
        # First, reset all the results so we don't get into a race with the
        # validation thread.
        model = self.table_files.source_model
        model.reset_results()

        # Start the validation thread
        self._validate_files()

    @QtCore.pyqtSlot()
    def _handle_btn_clear_clicked(self):
        LOG.debug("handle_btn_clear_clicked()")
        self.table_files.clear()

    def _populate_xml_results(self, item):
        tab = self._result_tabs.get('xml')
        tab.set_results(item.filename, item.results.xml)

        if self.tab_widget.indexOf(tab) == -1:
            self.tab_widget.addTab(tab, "XML Results")

        self.tab_widget.setCurrentWidget(tab)

    @QtCore.pyqtSlot(str)
    def _handle_xml_results_requested(self, itemid):
        LOG.debug("XML results requested...")
        model   = self.table_files.source_model
        item    = model.lookup(str(itemid))

        try:
            self._populate_xml_results(item)
        except AttributeError as ex:
            LOG.error("Error retrieving xml validation results: %s", str(ex))

    def _populate_profile_results(self, item):
        tab = self._result_tabs.get('profile')
        tab.set_results(item.filename, item.results.profile)

        if self.tab_widget.indexOf(tab) == -1:
            self.tab_widget.addTab(tab, "STIX Profile Results")

        self.tab_widget.setCurrentWidget(tab)

    @QtCore.pyqtSlot(str)
    def _handle_profile_results_requested(self, itemid):
        model = self.table_files.source_model
        item  = model.lookup(str(itemid))

        try:
            self._populate_profile_results(item)
        except AttributeError as ex:
            LOG.error("Error retrieving profile validation results: %s", str(ex))


    def _populate_best_practices_results(self, item):
        tab = self._result_tabs.get('best_practices')
        tab.set_results(item.filename, item.results.best_practices)

        if self.tab_widget.indexOf(tab) == -1:
            self.tab_widget.addTab(tab, "Best Practices Results")

        self.tab_widget.setCurrentWidget(tab)

    @QtCore.pyqtSlot(str)
    def _handle_best_practices_results_requested(self, itemid):
        model = self.table_files.source_model
        item  = model.lookup(str(itemid))

        try:
            self._populate_best_practices_results(item)
        except AttributeError as ex:
            LOG.error("Error retrieving best pracitces validation results: %s", str(ex))

    def _handle_transform(self, klass, filter):
        infile = QtGui.QFileDialog.getOpenFileName(
            parent=self,
            caption="Select Profile...",
            filter="Excel (*.xlsx)",
            directory=BASE_DIR,
        )

        if not infile:
            LOG.debug("User cancelled out of profile selection.")
            return

        outfile = QtGui.QFileDialog.getSaveFileName(
            parent=self,
            caption="Save Transform As...",
            filter=filter,
            directory=BASE_DIR,
        )

        if not outfile:
            LOG.debug("User cancelled out of save file.")
            return

        outfile = str(outfile)
        infile  = str(infile)

        transformer = worker.TransformWorker(infile=infile, outfile=outfile)
        dialog = klass(worker=transformer, parent=self)

        self.update_status("Transforming Profile...")

        dialog.show()
        dialog.start_transform()
        dialog.exec_()

        self.update_status("Profile Transform Complete.")

    @QtCore.pyqtSlot()
    def _handle_to_xslt(self):
        filter = "XSLT (*.xslt)"
        self._handle_transform(klass=widgets.XsltTransformDialog, filter=filter)

    @QtCore.pyqtSlot()
    def _handle_to_schematron(self):
        filter = "Schematron (*.sch)"
        self._handle_transform(klass=widgets.SchematronTransformDialog, filter=filter)

    def update_status(self, msg):
        self.status.setText(msg)