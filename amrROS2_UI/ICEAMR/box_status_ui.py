# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'box_status.ui'
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

class Ui_mpBoxStatus(object):
    def setupUi(self, mpBoxStatus):
        if not mpBoxStatus.objectName():
            mpBoxStatus.setObjectName(u"mpBoxStatus")
        mpBoxStatus.resize(500, 396)
        self.verticalLayout = QVBoxLayout(mpBoxStatus)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(mpBoxStatus)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"background-color: rgb(98, 160, 234);")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamilies([u"Ubuntu Sans"])
        font.setPointSize(40)
        font.setBold(False)
        font.setItalic(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(mpBoxStatus)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.mpBoxInuselb = QLabel(self.frame_2)
        self.mpBoxInuselb.setObjectName(u"mpBoxInuselb")
        font1 = QFont()
        font1.setFamilies([u"Ubuntu Sans"])
        font1.setPointSize(30)
        font1.setItalic(True)
        self.mpBoxInuselb.setFont(font1)
        self.mpBoxInuselb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.mpBoxInuselb, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(mpBoxStatus)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.mpCloseBoxStatusbtn = QPushButton(self.frame_3)
        self.mpCloseBoxStatusbtn.setObjectName(u"mpCloseBoxStatusbtn")
        self.mpCloseBoxStatusbtn.setMinimumSize(QSize(0, 50))
        font2 = QFont()
        font2.setFamilies([u"Ubuntu Sans"])
        font2.setPointSize(25)
        font2.setItalic(True)
        self.mpCloseBoxStatusbtn.setFont(font2)
        self.mpCloseBoxStatusbtn.setStyleSheet(u"background-color: rgb(249, 248, 207);")

        self.verticalLayout_3.addWidget(self.mpCloseBoxStatusbtn)


        self.verticalLayout.addWidget(self.frame_3, 0, Qt.AlignmentFlag.AlignBottom)


        self.retranslateUi(mpBoxStatus)
        self.mpCloseBoxStatusbtn.clicked.connect(mpBoxStatus.accept)

        QMetaObject.connectSlotsByName(mpBoxStatus)
    # setupUi

    def retranslateUi(self, mpBoxStatus):
        mpBoxStatus.setWindowTitle(QCoreApplication.translate("mpBoxStatus", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("mpBoxStatus", u"Box Status", None))
        self.mpBoxInuselb.setText(QCoreApplication.translate("mpBoxStatus", u"Box 1 already in use. ", None))
        self.mpCloseBoxStatusbtn.setText(QCoreApplication.translate("mpBoxStatus", u"Close", None))
    # retranslateUi

