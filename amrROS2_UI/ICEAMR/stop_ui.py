# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'stop.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout,
    QLabel, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_mpStopDialog(object):
    def setupUi(self, mpStopDialog):
        if not mpStopDialog.objectName():
            mpStopDialog.setObjectName(u"mpStopDialog")
        mpStopDialog.resize(639, 496)
        self.verticalLayout = QVBoxLayout(mpStopDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(mpStopDialog)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"background-color: rgb(46, 194, 126);")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.mpStopText = QLabel(self.frame)
        self.mpStopText.setObjectName(u"mpStopText")
        font = QFont()
        font.setFamilies([u"Ubuntu Sans"])
        font.setPointSize(50)
        font.setItalic(True)
        self.mpStopText.setFont(font)

        self.gridLayout.addWidget(self.mpStopText, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout.addWidget(self.frame, 0, Qt.AlignmentFlag.AlignTop)

        self.frame_2 = QFrame(mpStopDialog)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setStyleSheet(u"background-color: rgb(143, 240, 164);")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label = QLabel(self.frame_2)
        self.label.setObjectName(u"label")
        font1 = QFont()
        font1.setFamilies([u"Ubuntu Sans"])
        font1.setPointSize(40)
        font1.setItalic(True)
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(mpStopDialog)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.mpRunAgainBtn = QPushButton(self.frame_3)
        self.mpRunAgainBtn.setObjectName(u"mpRunAgainBtn")
        self.mpRunAgainBtn.setMinimumSize(QSize(0, 100))
        font2 = QFont()
        font2.setFamilies([u"Ubuntu Sans"])
        font2.setPointSize(40)
        self.mpRunAgainBtn.setFont(font2)
        self.mpRunAgainBtn.setStyleSheet(u"background-color: rgb(25, 255, 0);")

        self.verticalLayout_2.addWidget(self.mpRunAgainBtn)


        self.verticalLayout.addWidget(self.frame_3, 0, Qt.AlignmentFlag.AlignBottom)


        self.retranslateUi(mpStopDialog)

        QMetaObject.connectSlotsByName(mpStopDialog)
    # setupUi

    def retranslateUi(self, mpStopDialog):
        mpStopDialog.setWindowTitle(QCoreApplication.translate("mpStopDialog", u"Dialog", None))
        self.mpStopText.setText(QCoreApplication.translate("mpStopDialog", u"SAFE  STOP", None))
        self.label.setText(QCoreApplication.translate("mpStopDialog", u"Press run button to \n"
"run robot again.", None))
        self.mpRunAgainBtn.setText(QCoreApplication.translate("mpStopDialog", u"Run", None))
    # retranslateUi

