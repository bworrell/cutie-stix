"""
This module contains model code for cutiestix.
"""

# stdlib
import os
import logging

# external
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

# internal
from . import utils
from . import settings


LOG = logging.getLogger(__name__)


# These foreground and background colors are used to denote validation status.
VALIDATION_COLORS = {
    'exception': {
        'fg':  QtGui.QColor(Qt.white),
        'bg': QtGui.QColor(Qt.red)
    },
    'xml': {
        True: {
            'fg': QtGui.QColor(Qt.darkBlue),
            'bg': QtGui.QColor(Qt.cyan)
        },
        False: {
            'fg': QtGui.QColor(Qt.white),
            'bg': QtGui.QColor(Qt.magenta)
        }
    },
    'best_practices': {
        True: {
            'fg': QtGui.QColor(Qt.darkBlue),
            'bg': QtGui.QColor(Qt.cyan)
        },
        False: {
            'fg': QtGui.QColor(Qt.white),
            'bg': QtGui.QColor(Qt.magenta)
        }
    },
    'profile': {
        True: {
            'fg': QtGui.QColor(Qt.darkBlue),
            'bg': QtGui.QColor(Qt.cyan)
        },
        False: {
            'fg': QtGui.QColor(Qt.white),
            'bg': QtGui.QColor(Qt.magenta)
        }
    },

}


class IndexedModelItem(object):
    """Used for model row data that can be accessed by column number or
    attribute name.

    This is useful in QAbstractTableModel data() and setData() methods which
    are passed QModelIndex objects, and thus refer to columns and rows by
    index values.

    Example:
        >>> class Foo(IndexedModelItem):
        >>>     _attrs = ("foo", "bar")
        >>>
        >>> f = Foo(foo=True, bar=False)
        >>> print f[0]
        True
        >>> print f.foo
        True
        >>> print f[1]
        False
        >>> print f.bar
        False
    """

    _attrs = tuple()  # Index-accessible attributes

    def __init__(self, **kwargs):
        super(IndexedModelItem, self).__init__()

        for attr in self._attrs:
            setattr(self, attr, kwargs.get(attr))

    def __getitem__(self, index):
        """Return the value for the `index`.

        Args:
            index: A integer index.

        Returns:
            The value associated with the index.

        Raises:
            TypeError: If `index` cannot be translated to an int.
            ValueError: If `index` cannot be translated to an int.
        """
        index = int(index)
        attr  = self._attrs[index]
        return getattr(self, attr)

    def __setitem__(self, index, value):
        """Set the `value` for the `index`.

        Args:
            index: An integer index.
            value: A value.

        Returns:
            The value associated with the index.

        Raises:
            TypeError: If `index` cannot be translated to an int.
            ValueError: If `index` cannot be translated to an int.
        """
        index = int(index)
        attr  = self._attrs[index]
        setattr(self, attr, value)


class BestPracticeResultsTableItem(IndexedModelItem):
    """Used for BestPracticeResultsTableModel entries."""
    _attrs = ("title", "line", "tag", "id", "idref", "message")


class ValidateTableItem(IndexedModelItem, QtCore.QObject):
    """Used for ValidationTableModel entries.

    Signals:
        SIGNAL_RESULTS_UPDATED (str): Emitted when results have been updated.
    """
    _attrs = ("filename", "stix_version", "validate_best_practices",
              "validate_stix_profile", "results")

    SIGNAL_RESULTS_UPDATED = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)

        IndexedModelItem.__init__(
            self,
            filename=None,
            stix_version=None,
            validate_stix_profile=settings.VALIDATE_STIX_PROFILE,
            validate_best_practices=settings.VALIDATE_STIX_BEST_PRACTICES,
            results=None
        )

        self.__key = str(id(self))

    def key(self):
        """Return a key for this item. This is the str(id(self)).

        This can be used for lookup within a table model.

        Note:
            Initially this returned ``id(self)`` but was changed due to integer
            overflow issues that can occur between 64bit Python and Qt when
            emitting integer data.

            I could have gotten around this by defining my signals as
            ``pyqtSignal('long long')`` but found that out after using
            ``str`` everywhere.
        """
        return self.__key

    def notify(self):
        """Notify observers that the results have changed.

        Emits:
            SIGNAL_RESULTS_UPDATED (str): The key() of the item that has been
            updated.
        """
        key = self.key()
        LOG.debug("Sending id(self): %s", key)
        self.SIGNAL_RESULTS_UPDATED.emit(key)

    @classmethod
    def from_file(cls, fn):
        """Return a ValidateTableItem instance for the input filename.

        Args:
            fn: A filename.

        Returns:
            A ValidateTableItem object.
        """
        item = cls()
        item.filename = os.path.abspath(fn)
        item.stix_version = utils.stix_version(fn)

        return item


class ValidationResults(object):
    """Holds validation results.

    This is used by ValidationTableItem for storing validation results.
    """
    __slots__ = ("xml", "best_practices", "profile")

    def __init__(self):
        self.xml = None
        self.best_practices = None
        self.profile = None


class ValidationResultsTableModel(QtCore.QAbstractTableModel):
    """Table model for storing XML and Profile validation errors.

    The underlying data is a list of stix-validator
    XmlValidationError amd ProfileValidationError objects.
    """

    COLUMNS = ("Line Number", "Error")
    COLUMN_INDEXES = dict(enumerate(COLUMNS))

    def __init__(self, parent):
        super(ValidationResultsTableModel, self).__init__(parent)
        self._data = []

    def update(self, results):
        """Set the model data to the errors found on `results`.

        If `results` is None, clear the model data.
        """
        self.beginResetModel()

        if results is None:
            self._data = []
        else:
            self._data = results.errors

        self.endResetModel()

    def clear(self):
        """Reset the model data."""
        self.update(None)

    def headerData(self, column, orientation, role=None):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.COLUMN_INDEXES[column]
        elif orientation == Qt.Vertical:
            return column + 1

        return None

    def _get_text(self, index):
        """Return the text to display for the input QModelIndex `index`."""
        row    = index.row()
        col = index.column()
        error = self._data[row]

        if col == 0:
            return str(error.line)
        elif col == 1:
            return error.message

    def data(self, index, role=None):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return self._get_text(index)

        return None

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        return len(self.COLUMNS)


class BestPracticeResultsTableModel(QtCore.QAbstractTableModel):
    """Table model for storing STIX Best Practice warnings.

    The underlying data is a list of stix-validator BestPracticeWarning objects.
    """

    COLUMNS = ("Title", "Line", "Tag", "@id", "@idref", "Error")
    COLUMN_INDEXES = dict(enumerate(COLUMNS))

    def __init__(self, parent):
        super(BestPracticeResultsTableModel, self).__init__(parent)
        self._data = []

    def _parse_results(self, results):
        """Parse the results and set the internal data.

        Args:
            results: A stix-validator BestPracticeResults object.

        Returns:
            A list of BestPracticeTableItem objects.
        """
        data = []

        for collection in sorted(results, key=lambda x: x.name):
            title = collection.name
            warns = [x for x in collection]

            for warn in warns:
                warndict = {k: warn[k] for k in warn.core_keys}
                item     = BestPracticeResultsTableItem(title=title, **warndict)
                data.append(item)

        return data

    def update(self, results):
        """Parse the `results` and populate the model.

        Args:
            results: A BestPracticeResults object.
        """
        self.beginResetModel()

        if results is None:
            self._data = []
        elif not results.errors:
            self._data = []
        else:
            self._data = self._parse_results(results)

        self.endResetModel()

    def clear(self):
        """Clear the model data."""
        self.update(None)

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        return len(self.COLUMNS)

    def data(self, index, role=None):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            return self._data[row][col]

        return None

    def headerData(self, column, orientation, role=None):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.COLUMN_INDEXES[column]
        elif orientation == Qt.Vertical:
            return column + 1


class ValidateTableModel(QtCore.QAbstractTableModel):
    """A table model that holds information about items to be validated."""

    COLUMNS = ("Filename", "STIX Version", "Best Practices Validate",
               "STIX Profile Validate", "Results")
    COLUMN_INDEXES = dict(enumerate(COLUMNS))

    def __init__(self, parent):
        super(ValidateTableModel, self).__init__(parent)
        self._data = []

    def clear(self):
        """Clears the model data."""
        self.update(None)

    def _get_item(self, fn):
        """Build and return a ValidateTableItem for the filename `fn`.

        Wire up the ValidateTableItem signals so that the model is notified
        of result updates.
        """
        item = ValidateTableItem.from_file(fn)
        item.SIGNAL_RESULTS_UPDATED.connect(self._notify_updated)
        return item

    def update(self, files):
        self.beginResetModel()

        if files is None:
            self._data = []
        else:
            self._data = [self._get_item(fn) for fn in files]

        self.endResetModel()

    def add(self, file):
        idx = len(self._data)
        self.beginInsertRows(QtCore.QModelIndex(), idx, idx)
        self._data.append(self._get_item(file))
        self.endInsertRows()

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        return len(self.COLUMNS)

    def _color(self, index, key):
        """Return the background/foreground color for the input `index`
        and `key`.

        If the item at `index` has validation results, return the associated
        color. If no results are set, return None (system defaults will be
        used).

        Args:
            index: A QModelIndex object.
            key: The VALIDATION_COLORS key (either 'bg' or 'fg').

        """
        row  = index.row()
        col  = index.column()
        item = self._data[row]

        if not item.results:
            return None
        elif isinstance(item.results, Exception):
            return VALIDATION_COLORS["exception"][key]

        xml = item.results.xml
        best_practices = item.results.best_practices
        profile = item.results.profile

        # For the "Results" column
        total = xml, profile, best_practices
        valid = all(getattr(x, 'is_valid', True) is True for x in total)

        if col == 2 and best_practices:
            is_valid = best_practices.is_valid
            return VALIDATION_COLORS["best_practices"][is_valid][key]
        elif col == 3 and profile:
            is_valid = profile.is_valid
            return VALIDATION_COLORS["profile"][is_valid][key]
        elif col == 4:
            # Just use the xml validation colors
            return VALIDATION_COLORS['xml'][valid][key]
        else:
            is_valid = xml.is_valid
            return VALIDATION_COLORS["xml"][is_valid][key]

    def _bgcolor(self, index):
        """Return the background color to paint for the item at `index`.

        Args
            index: A QModelIndex object.
        """
        return self._color(index, "bg")

    def _fgcolor(self, index):
        """Return the foreground color to paint for the item at `index`.

        Args
            index: A QModelIndex object.
        """
        return self._color(index, "fg")

    def data(self, index, role=None):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            return self._data[row][col]
        elif role == Qt.EditRole:
            return self._data[row][col]
        elif role == Qt.BackgroundRole:
            return self._bgcolor(index)
        elif role == Qt.ForegroundRole:
            return self._fgcolor(index)
        elif role  == Qt.UserRole:
            return self._data[row]

        return None

    def flags(self, index):
        """Allow the validation type columns to be editable so users can
        enable/disable validation types.

        For example, if a user selects the STIX Profile Validate column, they
        can enable or disable this type of validation.
        """
        flags = super(ValidateTableModel, self).flags(index)

        if not index.isValid():
            return flags

        col = index.column()

        if col == 2:
            flags |= Qt.ItemIsEditable
        elif col == 3 and settings.STIX_PROFILE_FILENAME:
            flags |= Qt.ItemIsEditable

        return flags

    def _handle_edit_role(self, index, value):
        """Handle the user editing a cell value."""
        row   = index.row()
        col   = index.column()
        value = utils.str2bool(value.toPyObject())

        # Set the value
        self._data[row][col] = value

        # Emit the change notification
        self.dataChanged.emit(index, index)

        return True

    def setData(self, index, value, role=None):
        if not index.isValid():
            return False

        if role == Qt.EditRole:
            return self._handle_edit_role(index, value)
        elif role >= Qt.UserRole:
            LOG.debug("Received role >= UserRole")
            return True

        return False

    def remove_item(self, item):
        """Remove the `item` from the model if it is currently held by the
        model.

        Args:
            item: A ValidateTableItem item.
        """
        if hasattr(item, "toPyObject"):
            item = item.toPyObject()

        if item not in self._data:
            LOG.warn("Attempting to remove something I don't have...")
        else:
            row = self._data.index(item)
            self.removeRow(row)

    def remove_items(self, items):
        """Remove the `items` from the model if it they are currently held by
        the model.

        Args:
            items: A list of ValidateTableItem items.
        """
        for item in items:
            self.remove_item(item)

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        """Remove the item found at the `row` from the model."""
        self.beginRemoveRows(parent, row, row)
        del self._data[row]
        self.endRemoveRows()

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        """Remove the items starting at `row` and ending at `row` + count."""
        self.beginRemoveRows(parent, row, row + count)

        for idx in xrange(row, row + count):
            del self._data[idx]

        self.endRemoveRows()

    def headerData(self, column, orientation, role=None):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.COLUMN_INDEXES[column]
        elif orientation == Qt.Vertical:
            return column + 1

        return None

    def items(self):
        """Return the model items."""
        return self._data

    def reset_results(self):
        """Resets the results on all the items in the model."""
        LOG.debug("Resetting model item results.")

        if not self._data:
            return

        for item in self._data:
            item.results = None

        cols  = len(self.COLUMNS)
        rows  = len(self._data)

        start = self.index(0, cols)
        end   = self.index(rows, cols)
        self.dataChanged.emit(start, end)

    @QtCore.pyqtSlot(str)
    def _notify_updated(self, itemid):
        """Notify the view that the row for the given `itemid` needs to be
        redrawn since its results have changed..
        """
        items = self._data
        idx   = next(x for x, item in enumerate(items) if item.key() == itemid)
        start = self.index(idx, 0)
        end   = self.index(idx, len(self.COLUMNS))
        self.dataChanged.emit(start, end)

    def enable_best_practices(self, enabled=True):
        """Enable/Disable best practices validation for all items in the
        model.
        """
        for item in self._data:
            item.validate_best_practices = enabled

        self.reset_results()

    def enable_profile(self, enabled=True):
        """Enable/Disable profile validation for all items in the model."""
        for item in self._data:
            item.validate_stix_profile = enabled

        self.reset_results()

    def lookup(self, itemid):
        """Return the model item for the given `itemid`.

        Args:
            itemid: A ValidateTableItem key() value.

        Raises:
            KeyError: If no model items have a key() which matches `itemid`.
        """
        try:
            return next(item for item in self._data if item.key() == itemid)
        except StopIteration:
            raise KeyError("Unknown itemid: %s" % itemid)
