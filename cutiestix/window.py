"""
This module contains code for the main window of cutiestix.
"""

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


# Module-level logger
LOG = logging.getLogger(__name__)

# Main window dimensions
WIDTH  = 1280
HEIGHT = 768

# Main window stacked widget indexes
INDEX_ADD_FILES  = 0
INDEX_VIEW_FILES = 1

# Used for Open/Save file dialogs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MainWindow(Ui_MainWindow, QtGui.QMainWindow):
    """The main window for the application.

    Slots:
        update_status (str): Updates the status bar with the received message.
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Dictionary of result types (xml, profile, ...) to QWidgets.
        # We use this for auto-selecting an already-open widget when a
        # user requests validation results.
        self._result_tabs = {}

        # Initialize all the ui components
        self._populate()

        # Connect the ui component signals.
        self._connect_ui()

    def _populate(self):
        """Initializes and populates ui components found in this window."""
        self.setupUi(self)

        # Create the results tabs but don't show them yet.
        self._result_tabs['xml'] = widgets.ResultsWidget(models.ValidationResultsTableModel)
        self._result_tabs['profile'] = widgets.ResultsWidget(models.ValidationResultsTableModel)
        self._result_tabs['best_practices'] = widgets.ResultsWidget(models.BestPracticeResultsTableModel)

        # Remove the unwanted, empty tab
        self.tab_widget.removeTab(1)

        # Add a permanent status bar
        self.status = QtGui.QLabel()
        self.statusBar().addPermanentWidget(self.status)

        # Update the status bar and make sure we're on the right stacked
        # widget.
        self._handle_file_table_model_changed()

        # Set the correct dimensions
        self.resize(WIDTH, HEIGHT)

        # Center the UI on the screen
        widgets.center(self)

    def _connect_ui(self):
        """Connect the ui component signals."""

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
        self.action_quit.triggered.connect(self.close)

        # Validate file table
        model = self.table_files.source_model
        model.modelReset.connect(self._handle_file_table_model_changed)
        model.rowsInserted.connect(self._handle_file_table_model_changed)
        model.rowsRemoved.connect(self._handle_file_table_model_changed)

        table = self.table_files
        table.SIGNAL_XML_RESULTS_REQUESTED.connect(self._handle_xml_results_requested)
        table.SIGNAL_PROFILE_RESULTS_REQUESTED.connect(self._handle_profile_results_requested)
        table.SIGNAL_BEST_PRACTICES_RESULTS_REQUESTED.connect(self._handle_best_practices_results_requested)
        table.SIGNAL_FILES_ADDED.connect(self._add_files)

        # Validation options
        bpstate = self.check_best_practices.stateChanged
        bpstate.connect(self._handle_check_best_practices_state_changed)
        exschema = self.check_external_schemas.stateChanged
        exschema.connect(self._handle_check_external_schemas_state_changed)
        pstate = self.check_profile.stateChanged
        pstate.connect(self._handle_check_profile_state_changed)

        # Add Files landing screen.
        self.page_add_files.SIGNAL_FILES_ADDED.connect(self._add_files)

    def _remove_results_tabs(self):
        """Removes XML, Best Practices, and Profile results tabs from the
        main window.

        Note:
            This will leave the main tab open.
        """
        for tab in self._result_tabs.itervalues():
            idx = self.tab_widget.indexOf(tab)
            self.tab_widget.removeTab(idx)

    @QtCore.pyqtSlot()
    def _show_about(self):
        """Display the About dialog."""
        about = widgets.AboutDialog(self)
        about.exec_()

    @QtCore.pyqtSlot()
    def _handle_file_table_model_changed(self):
        """Respond to the file table model change signals.

        If the table model is empty, send users back to the "Add Files.."
        screen and update the status.

        If the table model is not empty, send users to the table view.
        """
        model = self.table_files.source_model
        size  = model.rowCount()

        if size == 0:
            self.stacked_main.setCurrentIndex(INDEX_ADD_FILES)
            self._remove_results_tabs()
            self.update_status("No Files Added.")
        else:
            self.stacked_main.setCurrentIndex(INDEX_VIEW_FILES)
            self.update_status("Ready.")

    @QtCore.pyqtSlot(list)
    def _add_files(self, files):
        """Add entries to the file table.

        Args:
            files: A single file or list of files to add. If any of the files
                are directories, they will be traversed and all contained
                STIX files will be collected.
        """
        xmlfiles  = utils.list_xml_files(files)
        stixdocs  = [f for f in xmlfiles if utils.is_stix(f)]
        nonstix   = [f for f in xmlfiles if f not in stixdocs]
        model     = self.table_files.source_model

        for file in stixdocs:
            model.add(file)

        LOG.debug("Added STIX files: %s", stixdocs)
        LOG.debug("Skipped non-STIX files: %s", nonstix)

    @QtCore.pyqtSlot()
    def _handle_add_files(self):
        """Handle the "Add Files.." main menu clicks."""
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
        """Handle the "Add Directory..." main menu clicks."""
        LOG.debug("Adding directory")

        xmldir = QtGui.QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select STIX Document Directory",
            directory=BASE_DIR,
        )

        xmldir = str(xmldir)

        if not xmldir:
            LOG.debug("User cancelled out of xml directory selection")
        else:
            self._add_files(xmldir)

    @QtCore.pyqtSlot()
    def _handle_set_schema_dir(self):
        """Handle the "Set Schema Directory..." main menu clicks."""
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
        """Handle the "Set STIX Profile..." main menu clicks."""
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
        """Handle the "Profile Validate" check box check/uncheck events."""
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
        """Handle the "Use External Schemas" check box check/uncheck events."""
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
        """Handle the "Best Practices Validate" check box check/uncheck
        events.
        """
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
        """Update the status bar with the name of the file that is currently
        being validated.
        """
        fn = os.path.split(str(fn))[-1]
        msg = "Validating {file}...".format(file=fn)
        self.update_status(msg)

    @QtCore.pyqtSlot(str, float)
    def _handle_validation_updated(self, itemid, progress):
        """Update the progress bar when a table entry is finished validating."""
        LOG.debug("%s completed. Total progress: %f", itemid, progress)
        self.progress_validation.setValue(int(progress*100))

    @QtCore.pyqtSlot()
    def _handle_validation_started(self):
        """Disable ui components when validation has started."""
        self.group_actions.setEnabled(False)
        self.group_options.setEnabled(False)
        self.progress_validation.setValue(0)

    @QtCore.pyqtSlot()
    def _handle_validation_complete(self):
        """Enable ui components when validation has completed."""
        LOG.debug("Validation completed.")
        self.progress_validation.setValue(100)
        self.update_status("Ready.")
        self.group_actions.setEnabled(True)
        self.group_options.setEnabled(True)

    def _validate_files(self):
        """Create the validation thread and start it."""
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
        """Handle "Validate" button clicks."""

        # First, reset all the results so we don't get into a race with the
        # validation thread.
        model = self.table_files.source_model
        model.reset_results()

        # Start the validation thread
        self._validate_files()

    @QtCore.pyqtSlot()
    def _handle_btn_clear_clicked(self):
        """Handle "Clear" button clicks."""
        LOG.debug("handle_btn_clear_clicked()")
        self.table_files.clear()

    def _populate_xml_results(self, item):
        """Populate the XML Results tab.

        Args:
            item: A ValidationTableItem from the main files table.
        """
        tab = self._result_tabs.get('xml')
        tab.set_results(item.filename, item.results.xml)

        if self.tab_widget.indexOf(tab) == -1:
            self.tab_widget.addTab(tab, "XML Results")

        self.tab_widget.setCurrentWidget(tab)

    @QtCore.pyqtSlot(str)
    def _handle_xml_results_requested(self, itemid):
        """Handle user requests to view XML results for a table item.

        Args:
            itemid: A ValidationTableItem.key() from the main files table.
        """
        LOG.debug("XML results requested...")
        model   = self.table_files.source_model
        item    = model.lookup(str(itemid))

        try:
            self._populate_xml_results(item)
        except AttributeError as ex:
            LOG.error("Error retrieving xml validation results: %s", str(ex))

    def _populate_profile_results(self, item):
        """Populate the STIX Profile Results tab.

        Args:
            item: A ValidationTableItem from the main files table.
        """
        tab = self._result_tabs.get('profile')
        tab.set_results(item.filename, item.results.profile)

        if self.tab_widget.indexOf(tab) == -1:
            self.tab_widget.addTab(tab, "STIX Profile Results")

        self.tab_widget.setCurrentWidget(tab)

    @QtCore.pyqtSlot(str)
    def _handle_profile_results_requested(self, itemid):
        """Handle user requests to view STIX Profile results for a table item.

        Args:
            itemid: A ValidationTableItem.key() from the main files table.
        """
        model = self.table_files.source_model
        item  = model.lookup(str(itemid))

        try:
            self._populate_profile_results(item)
        except AttributeError as ex:
            LOG.error("Error retrieving profile validation results: %s", str(ex))


    def _populate_best_practices_results(self, item):
        """Populate the STIX Best Practices Results tab.

        Args:
            item: A ValidationTableItem from the main files table.
        """
        tab = self._result_tabs.get('best_practices')
        tab.set_results(item.filename, item.results.best_practices)

        if self.tab_widget.indexOf(tab) == -1:
            self.tab_widget.addTab(tab, "Best Practices Results")

        self.tab_widget.setCurrentWidget(tab)

    @QtCore.pyqtSlot(str)
    def _handle_best_practices_results_requested(self, itemid):
        """Handle user requests to view STIX Best Practices results for a
        table item.

        Args:
            itemid: A ValidationTableItem.key() from the main files table.
        """
        model = self.table_files.source_model
        item  = model.lookup(str(itemid))

        try:
            self._populate_best_practices_results(item)
        except AttributeError as ex:
            LOG.error("Error retrieving best pracitces validation results: %s", str(ex))

    def _handle_transform(self, klass, filter):
        """Handle requests to transform a STIX Profile.

        Note:
            This will open a transformer dialog and remain open until the
            transformation has completed.

        Args:
            klass: The transformer dialog class to use (e.g.,
                SchematronTransformDialog or XsltTransformDialog).
            filter: The save filename filter (e.g., "XSLT (*.xslt)")
        """
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
        """Handle requests to transform at STIX Profile to XSLT."""
        filter = "XSLT (*.xslt)"
        self._handle_transform(klass=widgets.XsltTransformDialog, filter=filter)

    @QtCore.pyqtSlot()
    def _handle_to_schematron(self):
        """Handle requests to transform a STIX Profile to Schematron."""
        filter = "Schematron (*.sch)"
        self._handle_transform(klass=widgets.SchematronTransformDialog, filter=filter)

    @QtCore.pyqtSlot()
    def update_status(self, msg):
        """Updates the status bar with the input `msg`.

        Args:
            msg: A status message.
        """
        self.status.setText(msg)