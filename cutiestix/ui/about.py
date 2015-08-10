# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qtui\about.ui'
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

class Ui_DialogAbout(object):
    def setupUi(self, DialogAbout):
        DialogAbout.setObjectName(_fromUtf8("DialogAbout"))
        DialogAbout.resize(575, 345)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DialogAbout.sizePolicy().hasHeightForWidth())
        DialogAbout.setSizePolicy(sizePolicy)
        DialogAbout.setMinimumSize(QtCore.QSize(575, 345))
        DialogAbout.setMaximumSize(QtCore.QSize(575, 345))
        DialogAbout.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(DialogAbout)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setRowWrapPolicy(QtGui.QFormLayout.DontWrapRows)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(DialogAbout)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(DialogAbout)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_api_version = QtGui.QLabel(DialogAbout)
        self.label_api_version.setObjectName(_fromUtf8("label_api_version"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_api_version)
        self.label_4 = QtGui.QLabel(DialogAbout)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.label_4)
        self.label_description = QtGui.QLabel(DialogAbout)
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_description)
        self.label_license = QtGui.QLabel(DialogAbout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_license.sizePolicy().hasHeightForWidth())
        self.label_license.setSizePolicy(sizePolicy)
        self.label_license.setObjectName(_fromUtf8("label_license"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_license)
        self.txt_license_value = QtGui.QTextEdit(DialogAbout)
        self.txt_license_value.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.txt_license_value.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.txt_license_value.setReadOnly(True)
        self.txt_license_value.setObjectName(_fromUtf8("txt_license_value"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.txt_license_value)
        self.label_version_value = QtGui.QLabel(DialogAbout)
        self.label_version_value.setObjectName(_fromUtf8("label_version_value"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.label_version_value)
        self.label_description_value = QtGui.QLabel(DialogAbout)
        self.label_description_value.setObjectName(_fromUtf8("label_description_value"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.label_description_value)
        self.label_api_version_value = QtGui.QLabel(DialogAbout)
        self.label_api_version_value.setObjectName(_fromUtf8("label_api_version_value"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.label_api_version_value)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, -1, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_close = QtGui.QPushButton(DialogAbout)
        self.btn_close.setObjectName(_fromUtf8("btn_close"))
        self.horizontalLayout.addWidget(self.btn_close)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(DialogAbout)
        QtCore.QMetaObject.connectSlotsByName(DialogAbout)

    def retranslateUi(self, DialogAbout):
        DialogAbout.setWindowTitle(_translate("DialogAbout", "About", None))
        self.label.setText(_translate("DialogAbout", "Application: ", None))
        self.label_2.setText(_translate("DialogAbout", "Version", None))
        self.label_api_version.setText(_translate("DialogAbout", "API Version:", None))
        self.label_4.setText(_translate("DialogAbout", "cutiestix (Qt STIX)", None))
        self.label_description.setText(_translate("DialogAbout", "Description:", None))
        self.label_license.setText(_translate("DialogAbout", "License:", None))
        self.label_version_value.setText(_translate("DialogAbout", "0.1", None))
        self.label_description_value.setText(_translate("DialogAbout", "A PyQt wrapper around the stix-validator API.", None))
        self.label_api_version_value.setText(_translate("DialogAbout", "2.4.0", None))
        self.btn_close.setText(_translate("DialogAbout", "Close", None))

