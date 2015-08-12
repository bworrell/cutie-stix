# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qtui\transform.ui'
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

class Ui_TransformDialog(object):
    def setupUi(self, TransformDialog):
        TransformDialog.setObjectName(_fromUtf8("TransformDialog"))
        TransformDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        TransformDialog.resize(385, 65)
        TransformDialog.setMinimumSize(QtCore.QSize(385, 65))
        TransformDialog.setMaximumSize(QtCore.QSize(385, 65))
        self.verticalLayout = QtGui.QVBoxLayout(TransformDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.progressBar = QtGui.QProgressBar(TransformDialog)
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", -1)
        self.progressBar.setFormat(_fromUtf8(""))
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.horizontalLayout.addWidget(self.progressBar)
        self.btn_cancel = QtGui.QPushButton(TransformDialog)
        self.btn_cancel.setMaximumSize(QtCore.QSize(16777215, 23))
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.horizontalLayout.addWidget(self.btn_cancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(TransformDialog)
        QtCore.QMetaObject.connectSlotsByName(TransformDialog)

    def retranslateUi(self, TransformDialog):
        TransformDialog.setWindowTitle(_translate("TransformDialog", "Transforming...", None))
        self.btn_cancel.setText(_translate("TransformDialog", "Cancel", None))

