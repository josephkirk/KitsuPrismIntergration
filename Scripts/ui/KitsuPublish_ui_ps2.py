# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'KitsuPublish.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_dlg_kitsuPublish(object):
    def setupUi(self, dlg_kitsuPublish):
        if not dlg_kitsuPublish.objectName():
            dlg_kitsuPublish.setObjectName(u"dlg_kitsuPublish")
        dlg_kitsuPublish.resize(292, 320)
        self.verticalLayout = QVBoxLayout(dlg_kitsuPublish)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.widget = QWidget(dlg_kitsuPublish)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.rb_asset = QRadioButton(self.widget)
        self.rb_asset.setObjectName(u"rb_asset")

        self.horizontalLayout.addWidget(self.rb_asset)

        self.rb_shot = QRadioButton(self.widget)
        self.rb_shot.setObjectName(u"rb_shot")

        self.horizontalLayout.addWidget(self.rb_shot)

        self.horizontalSpacer = QSpacerItem(40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.widget)

        self.widget_2 = QWidget(dlg_kitsuPublish)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setLayoutDirection(Qt.LeftToRight)
        self.verticalLayout_2 = QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.cb_shot = QComboBox(self.widget_2)
        self.cb_shot.setObjectName(u"cb_shot")

        self.verticalLayout_2.addWidget(self.cb_shot)

        self.label = QLabel(self.widget_2)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.cb_status = QComboBox(self.widget_2)
        self.cb_status.setObjectName(u"cb_status")

        self.verticalLayout_2.addWidget(self.cb_status)


        self.verticalLayout.addWidget(self.widget_2)

        self.widget_3 = QWidget(dlg_kitsuPublish)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout.addWidget(self.widget_3)

        self.l_description = QLabel(dlg_kitsuPublish)
        self.l_description.setObjectName(u"l_description")

        self.verticalLayout.addWidget(self.l_description)

        self.te_description = QPlainTextEdit(dlg_kitsuPublish)
        self.te_description.setObjectName(u"te_description")

        self.verticalLayout.addWidget(self.te_description)

        self.verticalSpacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.b_sgPublish = QPushButton(dlg_kitsuPublish)
        self.b_sgPublish.setObjectName(u"b_sgPublish")
        self.b_sgPublish.setMinimumSize(QSize(0, 35))

        self.verticalLayout.addWidget(self.b_sgPublish)


        self.retranslateUi(dlg_kitsuPublish)

        QMetaObject.connectSlotsByName(dlg_kitsuPublish)
    # setupUi

    def retranslateUi(self, dlg_kitsuPublish):
        dlg_kitsuPublish.setWindowTitle(QCoreApplication.translate("dlg_kitsuPublish", u"Kitsu Publish", None))
        self.rb_asset.setText(QCoreApplication.translate("dlg_kitsuPublish", u"Asset", None))
        self.rb_shot.setText(QCoreApplication.translate("dlg_kitsuPublish", u"Shot", None))
        self.label.setText(QCoreApplication.translate("dlg_kitsuPublish", u"Status:", None))
        self.l_description.setText(QCoreApplication.translate("dlg_kitsuPublish", u"Comment:", None))
        self.b_sgPublish.setText(QCoreApplication.translate("dlg_kitsuPublish", u"Publish to Kitsu", None))
    # retranslateUi

