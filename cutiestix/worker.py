"""
This module contains QObjects that perform specific, long-running tasks that
are intended to be moved to a non-GUI thread.

The QObject implementations below are designed to be leveraged by a QThread
via the `moveToThread()` method:

>>> thread = QThread()
>>> worker = FooWorker()
>>>
>>> thread.started.connect(worker.dowork)    # Connect QThread.started signal
>>> worker.done_signal.connect(thread.quit)  # Quit the thread when finished
>>>
>>> worker.moveToThread(thread)  # Move the worker object to the thread
>>>
>>> thread.start() # Start the thread!
"""

# stdlib
from __future__ import division
import logging

# PyQt
from PyQt4 import QtCore

# stix-validator
import sdv

# internal
from . import settings
from . import models


LOG = logging.getLogger(__name__)


class ValidationWorker(QtCore.QObject):
    """Performs XML, STIX Best Practices, and STIX Profile validation against
    a set of input files.

    Signals:
        SIGNAL_VALIDATING (str): Emits the key() of the item that is currently
            being validated.
        SIGNAL_VALIDATED (str): Emits the key() of an item that is done
            validating.
        SIGNAL_FINISHED: Emitted when validation is completed for all items.
        SIGNAL_EXCEPTION (str): Emits an Exception string if an Exception
            has been raised during validation.

    Slots:
        validate: Runs the validation tasks. Connect QThread.started to this.
    """

    SIGNAL_VALIDATING  = QtCore.pyqtSignal(str)
    SIGNAL_VALIDATED   = QtCore.pyqtSignal(int, float)
    SIGNAL_FINISHED    = QtCore.pyqtSignal()
    SIGNAL_EXCEPTION   = QtCore.pyqtSignal(Exception)

    def __init__(self, parent=None):
        super(ValidationWorker, self).__init__(parent)
        self._tasks = []

    def add_tasks(self, tasks):
        """Add the validation "tasks" to the internal task collection.

        Args:
            tasks: A list of ValidateTableItem objects from the main window table.
        """
        self._tasks.extend(tasks)

    def add_task(self, task):
        """Add a single validation task to the internal task collection.

        Args:
            task: A single ValidateTableItem from the main window table.
        """
        self._tasks.append(task)

    def _validate_item(self, item):
        """Perform validation for the  ValidateTableItem `item`.

        The `item` specifies the input filename and what forms of validation
        are to be run against that file.

        Returns:
            A model ValidationResults object.
        """
        fn      = item.filename
        version = item.stix_version
        schemas = None
        profile = settings.STIX_PROFILE_FILENAME
        result  = models.ValidationResults()

        if settings.VALIDATE_EXTERNAL_SCHEMAS:
            schemas = settings.XML_SCHEMA_DIR

        # Always run XML validation
        LOG.debug("Validating %s using schema dir %s", fn, schemas)
        result.xml = sdv.validate_xml(doc=fn, schemas=schemas, version=version)

        # If the file was XML invalid, don't bother running the other
        # validation scenarios.
        if not result.xml.is_valid:
            return result

        if item.validate_stix_profile:
            LOG.debug("Running profile validation for %s using profile %s", fn, profile)
            result.profile = sdv.validate_profile(doc=fn, profile=profile)

        if item.validate_best_practices:
            LOG.debug("Running best practice validation for %s", fn)
            result.best_practices = sdv.validate_best_practices(doc=fn, version=version)

        return result

    @QtCore.pyqtSlot()
    def validate(self):
        """Run the validation tasks.

        Connect the QThread.started signal to this slot!

        Emits:
            SIGNAL_VALIDATING (str): When a validation task has started.
            SIGNAL_VALIDATED (str, float): When a validation task has completed.
            SIGNAL_EXCEPTION (str): When an error has occurred during validation.
            SIGNAL_FINISHED: When all validation tasks have completed.
        """
        LOG.debug("Validating %d docuemnts", len(self._tasks))
        LOG.debug("Worker executing in thread %d", QtCore.QThread.currentThreadId())
        total = len(self._tasks)

        for idx, item in enumerate(self._tasks, start=1):
            LOG.debug("Running task %s", id(item))
            self.SIGNAL_VALIDATING.emit(item.filename)

            try:
                item.results = self._validate_item(item)
            except Exception as ex:
                LOG.warn("Error during validation: %s", str(ex))
                self.SIGNAL_EXCEPTION.emit(ex)
                item.results = ex
            finally:
                item.notify()
                self.SIGNAL_VALIDATED.emit(item.key(), (idx / total))

        LOG.debug("validate() done!")
        self.SIGNAL_FINISHED.emit()


class TransformWorker(QtCore.QObject):
    """Transforms STIX Profiles to Schematron or XSLT.

    Signals:
        SIGNAL_FINISHED: Emitted when the transformation has completed.
        SIGNAL_EXCEPTION (Exception): Emitted when an exception is raise at
            some point in the transformation.

    Slots:
        to_schematron: Transforms the input STIX document into Schematron.
        to_xslt: Transforms the input STIX documetn into XSLT.

    Args:
        infile: An input STIX filename or etree parsable object.
        outfile: An output filename.
        parent: A QObject parent.
    """

    SIGNAL_FINISHED  = QtCore.pyqtSignal()
    SIGNAL_EXCEPTION = QtCore.pyqtSignal(Exception)

    def __init__(self, infile, outfile, parent=None):
        super(TransformWorker, self).__init__(parent)
        self._profile = infile
        self._outfile = outfile

    def _write_out(self, tree):
        """Write the etree `tree` to the designated output file.

        Args:
            tree: An lxml ElementTree object.
        """
        tree.write(
            self._outfile,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8"
        )

    @QtCore.pyqtSlot()
    def to_schematron(self):
        """Transform the input document to Schematron.

        Emits:
            SIGNAL_EXCEPTION: If an exception is raised during transformation.
            SIGNAL_FINISHED: When the transformation has completed.
        """
        try:
            schematron = sdv.profile_to_schematron(self._profile)
            self._write_out(schematron)
        except Exception as ex:
            self.SIGNAL_EXCEPTION.emit(ex)
        finally:
            self.SIGNAL_FINISHED.emit()

    @QtCore.pyqtSlot()
    def to_xslt(self):
        """Transform the input document to Schematron.

        Emits:
            SIGNAL_EXCEPTION: If an exception is raised during transformation.
            SIGNAL_FINISHED: When the transformation has completed.
        """
        try:
            xslt = sdv.profile_to_xslt(self._profile)
            self._write_out(xslt)
        except Exception as ex:
            self.SIGNAL_EXCEPTION.emit(ex)
        finally:
            self.SIGNAL_FINISHED.emit()


