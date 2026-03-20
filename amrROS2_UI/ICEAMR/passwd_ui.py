# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'passwd.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_mpPasswdDialog(object):
    def setupUi(self, mpPasswdDialog):
        if not mpPasswdDialog.objectName():
            mpPasswdDialog.setObjectName(u"mpPasswdDialog")
        mpPasswdDialog.resize(986, 748)
        mpPasswdDialog.setStyleSheet(u"background-color: rgb(220, 230, 235);\n"
"color: rgb(0, 0, 0);")
        self.horizontalLayout_5 = QHBoxLayout(mpPasswdDialog)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.frame_31 = QFrame(mpPasswdDialog)
        self.frame_31.setObjectName(u"frame_31")
        self.frame_31.setFrameShape(QFrame.Shape.StyledPanel)
        self.verticalLayout_7 = QVBoxLayout(self.frame_31)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.frame_45 = QFrame(self.frame_31)
        self.frame_45.setObjectName(u"frame_45")
        self.frame_45.setMaximumSize(QSize(16777215, 180))
        font = QFont()
        font.setPointSize(15)
        self.frame_45.setFont(font)
        self.frame_45.setFrameShape(QFrame.Shape.StyledPanel)
        self.verticalLayout_5 = QVBoxLayout(self.frame_45)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.mpMsgLb = QLabel(self.frame_45)
        self.mpMsgLb.setObjectName(u"mpMsgLb")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mpMsgLb.sizePolicy().hasHeightForWidth())
        self.mpMsgLb.setSizePolicy(sizePolicy)
        self.mpMsgLb.setMaximumSize(QSize(16777215, 180))
        font1 = QFont()
        font1.setFamilies([u"Ubuntu Sans"])
        font1.setPointSize(60)
        font1.setBold(True)
        font1.setItalic(True)
        self.mpMsgLb.setFont(font1)
        self.mpMsgLb.setStyleSheet(u"background-color: rgb(98, 160, 234);\n"
"")
        self.mpMsgLb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_5.addWidget(self.mpMsgLb)


        self.verticalLayout_7.addWidget(self.frame_45, 0, Qt.AlignmentFlag.AlignTop)

        self.frame_4 = QFrame(self.frame_31)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_4)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.frame_47 = QFrame(self.frame_4)
        self.frame_47.setObjectName(u"frame_47")
        self.frame_47.setMaximumSize(QSize(16777215, 500))
        font2 = QFont()
        font2.setFamilies([u"Ubuntu Sans"])
        font2.setPointSize(25)
        font2.setBold(True)
        font2.setItalic(True)
        self.frame_47.setFont(font2)
        self.frame_47.setStyleSheet(u"\n"
"background-color: rgb(249, 248, 207);")
        self.frame_47.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_29 = QHBoxLayout(self.frame_47)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.mpBoxNumberlb = QLabel(self.frame_47)
        self.mpBoxNumberlb.setObjectName(u"mpBoxNumberlb")
        sizePolicy.setHeightForWidth(self.mpBoxNumberlb.sizePolicy().hasHeightForWidth())
        self.mpBoxNumberlb.setSizePolicy(sizePolicy)
        self.mpBoxNumberlb.setMaximumSize(QSize(16777215, 300))
        font3 = QFont()
        font3.setFamilies([u"Ubuntu Sans"])
        font3.setPointSize(200)
        font3.setBold(True)
        font3.setItalic(True)
        self.mpBoxNumberlb.setFont(font3)
        self.mpBoxNumberlb.setStyleSheet(u"color: rgb(26, 95, 180);")
        self.mpBoxNumberlb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_29.addWidget(self.mpBoxNumberlb)


        self.verticalLayout_6.addWidget(self.frame_47)


        self.verticalLayout_7.addWidget(self.frame_4)

        self.frame_33 = QFrame(self.frame_31)
        self.frame_33.setObjectName(u"frame_33")
        self.frame_33.setMinimumSize(QSize(0, 50))
        self.frame_33.setFrameShape(QFrame.Shape.StyledPanel)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_33)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.mpReceiveConfirmBtn = QPushButton(self.frame_33)
        self.mpReceiveConfirmBtn.setObjectName(u"mpReceiveConfirmBtn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.mpReceiveConfirmBtn.sizePolicy().hasHeightForWidth())
        self.mpReceiveConfirmBtn.setSizePolicy(sizePolicy1)
        self.mpReceiveConfirmBtn.setMinimumSize(QSize(150, 80))
        font4 = QFont()
        font4.setFamilies([u"Ubuntu Sans"])
        font4.setPointSize(50)
        font4.setBold(True)
        font4.setItalic(True)
        self.mpReceiveConfirmBtn.setFont(font4)
        self.mpReceiveConfirmBtn.setStyleSheet(u"\n"
"background-color: rgb(25, 255, 0);")

        self.horizontalLayout_6.addWidget(self.mpReceiveConfirmBtn)

        self.mpReceiveSkipBtn = QPushButton(self.frame_33)
        self.mpReceiveSkipBtn.setObjectName(u"mpReceiveSkipBtn")
        sizePolicy1.setHeightForWidth(self.mpReceiveSkipBtn.sizePolicy().hasHeightForWidth())
        self.mpReceiveSkipBtn.setSizePolicy(sizePolicy1)
        self.mpReceiveSkipBtn.setMinimumSize(QSize(150, 80))
        self.mpReceiveSkipBtn.setFont(font4)
        self.mpReceiveSkipBtn.setStyleSheet(u"\n"
"background-color: rgb(224, 27, 36);")

        self.horizontalLayout_6.addWidget(self.mpReceiveSkipBtn)


        self.verticalLayout_7.addWidget(self.frame_33)


        self.horizontalLayout_5.addWidget(self.frame_31)

        self.frame_3 = QFrame(mpPasswdDialog)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(self.frame_3)
        self.frame.setObjectName(u"frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy2)
        self.frame.setMinimumSize(QSize(0, 100))
        self.frame.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.mpPasswdLE = QLineEdit(self.frame)
        self.mpPasswdLE.setObjectName(u"mpPasswdLE")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.mpPasswdLE.sizePolicy().hasHeightForWidth())
        self.mpPasswdLE.setSizePolicy(sizePolicy3)
        font5 = QFont()
        font5.setPointSize(40)
        self.mpPasswdLE.setFont(font5)
        self.mpPasswdLE.setMaxLength(4)
        self.mpPasswdLE.setFrame(False)
        self.mpPasswdLE.setEchoMode(QLineEdit.EchoMode.Password)
        self.mpPasswdLE.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.mpPasswdLE, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(self.frame_3)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QFrame.Shape.Box)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.mp1btn = QPushButton(self.frame_2)
        self.mp1btn.setObjectName(u"mp1btn")
        self.mp1btn.setMinimumSize(QSize(0, 120))
        font6 = QFont()
        font6.setPointSize(40)
        font6.setBold(True)
        self.mp1btn.setFont(font6)

        self.horizontalLayout.addWidget(self.mp1btn)

        self.mp2btn = QPushButton(self.frame_2)
        self.mp2btn.setObjectName(u"mp2btn")
        self.mp2btn.setMinimumSize(QSize(0, 120))
        self.mp2btn.setFont(font6)

        self.horizontalLayout.addWidget(self.mp2btn)

        self.mp3btn = QPushButton(self.frame_2)
        self.mp3btn.setObjectName(u"mp3btn")
        self.mp3btn.setMinimumSize(QSize(0, 120))
        self.mp3btn.setFont(font6)

        self.horizontalLayout.addWidget(self.mp3btn)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.mp4btn = QPushButton(self.frame_2)
        self.mp4btn.setObjectName(u"mp4btn")
        self.mp4btn.setMinimumSize(QSize(0, 120))
        self.mp4btn.setFont(font6)

        self.horizontalLayout_2.addWidget(self.mp4btn)

        self.mp5btn = QPushButton(self.frame_2)
        self.mp5btn.setObjectName(u"mp5btn")
        self.mp5btn.setMinimumSize(QSize(0, 120))
        self.mp5btn.setFont(font6)

        self.horizontalLayout_2.addWidget(self.mp5btn)

        self.mp6btn = QPushButton(self.frame_2)
        self.mp6btn.setObjectName(u"mp6btn")
        self.mp6btn.setMinimumSize(QSize(0, 120))
        self.mp6btn.setFont(font6)

        self.horizontalLayout_2.addWidget(self.mp6btn)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.mp7btn = QPushButton(self.frame_2)
        self.mp7btn.setObjectName(u"mp7btn")
        self.mp7btn.setMinimumSize(QSize(0, 120))
        self.mp7btn.setFont(font6)

        self.horizontalLayout_3.addWidget(self.mp7btn)

        self.mp8btn = QPushButton(self.frame_2)
        self.mp8btn.setObjectName(u"mp8btn")
        self.mp8btn.setMinimumSize(QSize(0, 120))
        self.mp8btn.setFont(font6)

        self.horizontalLayout_3.addWidget(self.mp8btn)

        self.mp9btn = QPushButton(self.frame_2)
        self.mp9btn.setObjectName(u"mp9btn")
        self.mp9btn.setMinimumSize(QSize(0, 120))
        self.mp9btn.setFont(font6)

        self.horizontalLayout_3.addWidget(self.mp9btn)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.mpDelbtn = QPushButton(self.frame_2)
        self.mpDelbtn.setObjectName(u"mpDelbtn")
        self.mpDelbtn.setMinimumSize(QSize(0, 120))
        self.mpDelbtn.setFont(font6)

        self.horizontalLayout_4.addWidget(self.mpDelbtn)

        self.mp0btn = QPushButton(self.frame_2)
        self.mp0btn.setObjectName(u"mp0btn")
        self.mp0btn.setMinimumSize(QSize(0, 120))
        self.mp0btn.setFont(font6)

        self.horizontalLayout_4.addWidget(self.mp0btn)

        self.mpCanclebtn = QPushButton(self.frame_2)
        self.mpCanclebtn.setObjectName(u"mpCanclebtn")
        self.mpCanclebtn.setMinimumSize(QSize(0, 120))
        self.mpCanclebtn.setFont(font6)

        self.horizontalLayout_4.addWidget(self.mpCanclebtn)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.verticalLayout_4.addLayout(self.verticalLayout_3)


        self.verticalLayout.addWidget(self.frame_2)


        self.horizontalLayout_5.addWidget(self.frame_3)


        self.retranslateUi(mpPasswdDialog)

        QMetaObject.connectSlotsByName(mpPasswdDialog)
    # setupUi

    def retranslateUi(self, mpPasswdDialog):
        mpPasswdDialog.setWindowTitle(QCoreApplication.translate("mpPasswdDialog", u"Password Dialog", None))
        self.mpMsgLb.setText(QCoreApplication.translate("mpPasswdDialog", u"\u0e42\u0e1b\u0e23\u0e14\u0e23\u0e31\u0e1a\u0e02\u0e2d\u0e07\u0e17\u0e35\u0e48\u0e0a\u0e48\u0e2d\u0e07 ", None))
        self.mpBoxNumberlb.setText(QCoreApplication.translate("mpPasswdDialog", u"1", None))
        self.mpReceiveConfirmBtn.setText(QCoreApplication.translate("mpPasswdDialog", u"\u0e22\u0e37\u0e19\u0e22\u0e31\u0e19", None))
        self.mpReceiveSkipBtn.setText(QCoreApplication.translate("mpPasswdDialog", u"\u0e02\u0e49\u0e32\u0e21\u0e01\u0e32\u0e23\u0e23\u0e31\u0e1a", None))
        self.mpPasswdLE.setPlaceholderText(QCoreApplication.translate("mpPasswdDialog", u"**** ", None))
        self.mp1btn.setText(QCoreApplication.translate("mpPasswdDialog", u"1", None))
        self.mp2btn.setText(QCoreApplication.translate("mpPasswdDialog", u"2", None))
        self.mp3btn.setText(QCoreApplication.translate("mpPasswdDialog", u"3", None))
        self.mp4btn.setText(QCoreApplication.translate("mpPasswdDialog", u"4", None))
        self.mp5btn.setText(QCoreApplication.translate("mpPasswdDialog", u"5", None))
        self.mp6btn.setText(QCoreApplication.translate("mpPasswdDialog", u"6", None))
        self.mp7btn.setText(QCoreApplication.translate("mpPasswdDialog", u"7", None))
        self.mp8btn.setText(QCoreApplication.translate("mpPasswdDialog", u"8", None))
        self.mp9btn.setText(QCoreApplication.translate("mpPasswdDialog", u"9", None))
        self.mpDelbtn.setText(QCoreApplication.translate("mpPasswdDialog", u"DEL", None))
        self.mp0btn.setText(QCoreApplication.translate("mpPasswdDialog", u"0", None))
        self.mpCanclebtn.setText(QCoreApplication.translate("mpPasswdDialog", u"C", None))
    # retranslateUi

