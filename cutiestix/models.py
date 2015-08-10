# builtin
import os
import collections
import logging

# external
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

# internal
from . import utils
from . import settings


LOG = logging.getLogger(__name__)


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


class IndexedModelItem(QtCore.QObject):
    _attrs = tuple()

    def __init__(self, **kwargs):
        super(IndexedModelItem, self).__init__()

        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def __getitem__(self, item):
        index = int(item)
        attr  = self._attrs[index]
        return getattr(self, attr)

    def __setitem__(self, key, value):
        index = int(key)
        attr  = self._attrs[index]
        setattr(self, attr, value)


BestPracticeTableItem = collections.namedtuple(
    typename="BestPracticeTableItem",
    field_names=("filename", "title", "line", "tag", "id", "idref", "message")
)


class ValidationResults(object):
    __slots__ = ("xml", "best_practices", "profile")

    def __init__(self):
        self.xml = None
        self.best_practices = None
        self.profile = None


class ValidateTableItem(IndexedModelItem):
    _attrs = ("filename", "stix_version", "validate_best_practices",
              "validate_stix_profile", "results")

    SIGNAL_RESULTS_UPDATED = QtCore.pyqtSignal(str)

    def __init__(self):
        super(ValidateTableItem, self).__init__(
            filename=None,
            stix_version=None,
            validate_stix_profile=settings.VALIDATE_STIX_PROFILE,
            validate_best_practices=settings.VALIDATE_STIX_BEST_PRACTICES,
            results=None
        )

        self.__key = str(id(self))

    def key(self):
        return self.__key

    def notify(self):
        key = self.key()
        LOG.debug("Sending id(self): %s", key)
        self.SIGNAL_RESULTS_UPDATED.emit(key)

    @classmethod
    def from_file(cls, fn):
        item = cls()
        item.filename = os.path.abspath(fn)
        item.stix_version = utils.stix_version(fn)
        return item


class ColoredRowProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ColoredRowProxyModel, self).__init__(parent)
        self._fgcolors = {}
        self._bgcolors = {}

    def clear(self):
        self._fgcolors = {}
        self._bgcolors = {}
        self.invalidate()

    def set_color(self, row, bgcolor, fgcolor):
        self._fgcolors[row] = fgcolor
        self._bgcolors[row] = bgcolor
        self.invalidate()

    def data(self, index, role=None):
        if not index.isValid():
            return None

        row = index.row()

        if role == Qt.BackgroundRole:
            return self._bgcolors[row]
        elif role == Qt.ForegroundRole:
            return self._fgcolors[row]

        return super(ColoredRowProxyModel, self).data(index, role)


class BestPracticeResultsTableModel(QtCore.QAbstractTableModel):
    COL_NAMES = (
        "Filename",
        "Title",
        "Line",
        "Tag",
        "ID",
        "IDREF",
        "Message"
    )

    COL_INDEXES = dict(enumerate(COL_NAMES))

    def __init__(self, parent, data=None):
        super(BestPracticeResultsTableModel, self).__init__(parent)
        self._data = self._parse_data(data)

    def _parse_data(self, data):
        retval = []

        if not data:
            return retval

        for filename, collection in data.iteritems():
            title = collection.name

            for warn in collection:
                item = BestPracticeTableItem(
                    filename=filename,
                    title=title,
                    line=warn["line"],
                    message=warn["message"],
                    tag=warn["tag"],
                    id=warn["id"],
                    idref=warn["idref"]
                )

                retval.append(item)

        return retval

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        return len(self.COL_NAMES)

    def data(self, index, int_role=None):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if int_role == Qt.DisplayRole:
            return self._data[row][col]

        return None

    def headerData(self, column, orientation, int_role=None):
        if int_role != Qt.DisplayRole:
            return None

        if orientation != Qt.Horizontal:
            return None

        return self.COL_INDEXES[column]


class ValidateTableModel(QtCore.QAbstractTableModel):
    COLUMNS = ("Filename", "STIX Version", "Best Practices Validate",
               "STIX Profile Validate", "Results")
    COLUMN_INDEXES = dict(enumerate(COLUMNS))

    def __init__(self, parent):
        super(ValidateTableModel, self).__init__(parent)
        self._data = []
        self.update([])

    def clear(self):
        self.beginResetModel()
        self._data = []
        self.endResetModel()

    def _get_item(self, fn):
        item = ValidateTableItem.from_file(fn)
        item.SIGNAL_RESULTS_UPDATED.connect(self.update_results)
        return item

    def update(self, files):
        self.beginResetModel()
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
        return self._color(index, "bg")

    def _fgcolor(self, index):
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
        if hasattr(item, "toPyObject"):
            item = item.toPyObject()

        if item not in self._data:
            LOG.warn("Attempting to remove something I don't have...")
        else:
            row = self._data.index(item)
            self.removeRow(row)

    def remove_items(self, items):
        for item in items:
            self.remove_item(item)

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        del self._data[row]
        self.endRemoveRows()

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
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
    def update_results(self, itemid):
        """Let observers know that the results have changed for the item
        with the id() equal to `itemid`.
        """
        items = self._data
        idx   = next(x for x, item in enumerate(items) if item.key() == itemid)
        start = self.index(idx, 0)
        end   = self.index(idx, len(self.COLUMNS))
        self.dataChanged.emit(start, end)

    def enable_best_practices(self, enabled=True):
        for item in self._data:
            item.validate_best_practices = enabled

        self.reset_results()

    def enable_profile(self, enabled=True):
        for item in self._data:
            item.validate_stix_profile = enabled

        self.reset_results()


class BoolListModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(BoolListModel, self).__init__(parent)
        self._data = ("True", "False")

    def rowCount(self, index=None):
        return 2

    def data(self, index, role=None):
        if not index.isValid():
            return None

        row = index.row()

        if role == Qt.DisplayRole:
            return self._data[row]

        return None