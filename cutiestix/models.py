# builtin
import os
import collections
import logging

# external
from PyQt4 import QtCore
from PyQt4.QtCore import Qt

# internal
from . import utils
from . import settings


LOG = logging.getLogger(__name__)


class IndexedModelItem(object):
    __slots__ = tuple()

    def __init__(self, **kwargs):
       for attr, value in kwargs.iteritems():
           setattr(self, attr, value)

    def __getitem__(self, item):
        index = int(item)
        attr  = self.__slots__[index]
        return getattr(self, attr)

    def __setitem__(self, key, value):
        index = int(key)
        attr  = self.__slots__[index]
        setattr(self, attr, value)


BestPracticeTableItem = collections.namedtuple(
    typename="BestPracticeTableItem",
    field_names=("filename", "title", "line", "tag", "id", "idref", "message")
)


class ValidateTableItem(IndexedModelItem):
    __slots__ = ("filename", "stix_version", "validate_xml",
                 "validate_stix_profile", "validate_best_practices")

    def __init__(self):
        super(ValidateTableItem, self).__init__(
            filename=None,
            stix_version=None,
            validate_xml=settings.VALIDATE_XML,
            validate_stix_profile=settings.VALIDATE_STIX_PROFILE,
            validate_best_practices=settings.VALIDATE_STIX_BEST_PRACTICES
        )

    @classmethod
    def from_file(cls, fn):
        item = cls()
        item.filename = os.path.abspath(fn)
        item.stix_version = utils.stix_version(fn)
        return item


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
    COL_NAMES = ("Filename", "STIX Version", "XML Schema", "Best Practices",
                 "STIX Profile")
    COL_INDEXES = dict(enumerate(COL_NAMES))

    def __init__(self, parent):
        super(ValidateTableModel, self).__init__(parent)
        self._data = []
        self.update([])

    def clear(self):
        self.beginResetModel()
        self._data = []
        self.endResetModel()

    def update(self, files):
        if not files:
            item = ValidateTableItem()
            item.filename = "hi"
            item.stix_version = "1.0"
            self._data = [item]
            return

        self.beginResetModel()
        self._data = [ValidateTableItem.from_file(fn) for fn in files]
        self.endResetModel()

    def add(self, item):
        idx = len(self._data)
        self.beginInsertRows(QtCore.QModelIndex(), idx, idx)
        self._data.append(item)
        self.endInsertRows()

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        return len(self.COL_NAMES)

    def data(self, index, role=None):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            return self._data[row][col]
        elif role == Qt.EditRole:
            return self._data[row][col]

        return None

    def flags(self, index):
        flags = super(ValidateTableModel, self).flags(index)
        col = index.column()

        if col in (2,3,4):
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

    def headerData(self, column, orientation, int_role=None):
        if int_role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.COL_INDEXES[column]
        elif orientation == Qt.Vertical:
            return column + 1


class BoolListModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(BoolListModel, self).__init__(parent)
        self._data = ("True", "False")

    def rowCount(self, index):
        return 2

    def data(self, index, role=None):
        if not index.isValid():
            return None

        row = index.row()

        if role == Qt.DisplayRole:
            return self._data[row]

        return None