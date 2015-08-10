# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qtui\tableresults.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ResultsWidget(object):
    def setupUi(self, ResultsWidget):
        ResultsWidget.setObjectName(_fromUtf8("ResultsWidget"))
        ResultsWidget.resize(1369, 809)
        self.verticalLayout = QtGui.QVBoxLayout(ResultsWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setContentsMargins(-1, 10, -1, -1)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_result = QtGui.QLabel(ResultsWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_result.sizePolicy().hasHeightForWidth())
        self.label_result.setSizePolicy(sizePolicy)
        self.label_result.setMaximumSize(QtCore.QSize(16777215, 15))
        self.label_result.setObjectName(_fromUtf8("label_result"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_result)
        self.label_filename = QtGui.QLabel(ResultsWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_filename.sizePolicy().hasHeightForWidth())
        self.label_filename.setSizePolicy(sizePolicy)
        self.label_filename.setMaximumSize(QtCore.QSize(16777215, 15))
        self.label_filename.setObjectName(_fromUtf8("label_filename"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_filename)
        self.label_filename_value = QtGui.QLabel(ResultsWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_filename_value.sizePolicy().hasHeightForWidth())
        self.label_filename_value.setSizePolicy(sizePolicy)
        self.label_filename_value.setMaximumSize(QtCore.QSize(16777215, 15))
        self.label_filename_value.setObjectName(_fromUtf8("label_filename_value"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.label_filename_value)
        self.label_result_value = QtGui.QLabel(ResultsWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_result_value.sizePolicy().hasHeightForWidth())
        self.label_result_value.setSizePolicy(sizePolicy)
        self.label_result_value.setMaximumSize(QtCore.QSize(16777215, 15))
        self.label_result_value.setObjectName(_fromUtf8("label_result_value"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.label_result_value)
        self.verticalLayout.addLayout(self.formLayout)
        self.table_results = ResultsTableView(ResultsWidget)
        self.table_results.setObjectName(_fromUtf8("table_results"))
        self.verticalLayout.addWidget(self.table_results)

        self.retranslateUi(ResultsWidget)
        QtCore.QMetaObject.connectSlotsByName(ResultsWidget)

    def retranslateUi(self, ResultsWidget):
        ResultsWidget.setWindowTitle(_translate("ResultsWidget", "Form", None))
        self.label_result.setText(_translate("ResultsWidget", "Validation Result:", None))
        self.label_filename.setText(_translate("ResultsWidget", "Filename:", None))
        self.label_filename_value.setText(_translate("ResultsWidget", "(some file)", None))
        self.label_result_value.setText(_translate("ResultsWidget", "(some result)", None))

from cutiestix.widgets import ResultsTableView
