# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interface.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

from Custom_Widgets.QCustomQStackedWidget import QCustomQStackedWidget
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1923, 1100)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(30)
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"background-color: rgba(69, 140, 234, 222);\n"
"\n"
"\n"
"color: rgb(255, 255, 255);\n"
"\n"
"\n"
"border-radius: 10px;")
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy1)
        self.frame_3.setMinimumSize(QSize(0, 90))
        font1 = QFont()
        font1.setBold(False)
        font1.setItalic(True)
        self.frame_3.setFont(font1)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.mpStatuslb = QLabel(self.frame_3)
        self.mpStatuslb.setObjectName(u"mpStatuslb")
        font2 = QFont()
        font2.setFamilies([u"Ubuntu Sans"])
        font2.setPointSize(40)
        font2.setBold(False)
        font2.setItalic(True)
        self.mpStatuslb.setFont(font2)

        self.horizontalLayout_2.addWidget(self.mpStatuslb, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout.addWidget(self.frame_3)

        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        self.horizontalLayout_3 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_3.setSpacing(20)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(20, 0, 20, 0)
        self.pushButton = QPushButton(self.frame_4)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(0, 50))
        font3 = QFont()
        font3.setPointSize(30)
        font3.setBold(True)
        self.pushButton.setFont(font3)
        icon = QIcon()
        icon.addFile(u":/white/icons_white/material_design/battery_6_bar.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QSize(40, 40))

        self.horizontalLayout_3.addWidget(self.pushButton)

        self.pushButton_3 = QPushButton(self.frame_4)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setMinimumSize(QSize(0, 40))
        self.pushButton_3.setFont(font3)

        self.horizontalLayout_3.addWidget(self.pushButton_3)


        self.horizontalLayout.addWidget(self.frame_4)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy2)
        self.gridLayout_3 = QGridLayout(self.frame_2)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(-1, 0, 0, 0)
        self.myStackedWidget = QCustomQStackedWidget(self.frame_2)
        self.myStackedWidget.setObjectName(u"myStackedWidget")
        self.myStackedWidget.setMaximumSize(QSize(16777215, 1000))
        self.myStackedWidget.setStyleSheet(u"\n"
"/*background-color: rgba(73, 175, 245, 202);*/\n"
"background-color: rgb(255, 255, 255);")
        self.myStackedWidget.setFrameShape(QFrame.Shape.NoFrame)
        self.home_page = QWidget()
        self.home_page.setObjectName(u"home_page")
        self.gridLayout = QGridLayout(self.home_page)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame_5 = QFrame(self.home_page)
        self.frame_5.setObjectName(u"frame_5")
        self.horizontalLayout_4 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_6 = QFrame(self.frame_5)
        self.frame_6.setObjectName(u"frame_6")
        self.horizontalLayout_9 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.frame_17 = QFrame(self.frame_6)
        self.frame_17.setObjectName(u"frame_17")
        self.frame_17.setMaximumSize(QSize(16777215, 900))
        self.verticalLayout_3 = QVBoxLayout(self.frame_17)
        self.verticalLayout_3.setSpacing(10)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(40, 40, 40, 60)
        self.mpTargetBtn = QPushButton(self.frame_17)
        self.mpTargetBtn.setObjectName(u"mpTargetBtn")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.mpTargetBtn.sizePolicy().hasHeightForWidth())
        self.mpTargetBtn.setSizePolicy(sizePolicy3)
        self.mpTargetBtn.setStyleSheet(u"background-color: rgb(31, 149, 239);")
        icon1 = QIcon()
        icon1.addFile(u":/white/icons_white/font_awesome/solid/location-dot.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.mpTargetBtn.setIcon(icon1)
        self.mpTargetBtn.setIconSize(QSize(300, 300))
        self.mpTargetBtn.setAutoDefault(False)
        self.mpTargetBtn.setFlat(False)

        self.verticalLayout_3.addWidget(self.mpTargetBtn)

        self.label_3 = QLabel(self.frame_17)
        self.label_3.setObjectName(u"label_3")
        font4 = QFont()
        font4.setFamilies([u"Ubuntu Sans"])
        font4.setPointSize(60)
        font4.setItalic(True)
        self.label_3.setFont(font4)

        self.verticalLayout_3.addWidget(self.label_3, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout_9.addWidget(self.frame_17)


        self.horizontalLayout_4.addWidget(self.frame_6)

        self.frame_9 = QFrame(self.frame_5)
        self.frame_9.setObjectName(u"frame_9")
        self.horizontalLayout_13 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.frame_18 = QFrame(self.frame_9)
        self.frame_18.setObjectName(u"frame_18")
        self.frame_18.setMaximumSize(QSize(16777215, 900))
        self.verticalLayout_4 = QVBoxLayout(self.frame_18)
        self.verticalLayout_4.setSpacing(10)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(40, 40, 40, 60)
        self.mpSendBtn = QPushButton(self.frame_18)
        self.mpSendBtn.setObjectName(u"mpSendBtn")
        sizePolicy3.setHeightForWidth(self.mpSendBtn.sizePolicy().hasHeightForWidth())
        self.mpSendBtn.setSizePolicy(sizePolicy3)
        self.mpSendBtn.setMaximumSize(QSize(16777215, 166666))
        self.mpSendBtn.setStyleSheet(u"background-color: rgb(31, 149, 239);")
        icon2 = QIcon()
        icon2.addFile(u":/white/icons_white/font_awesome/solid/box-archive.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.mpSendBtn.setIcon(icon2)
        self.mpSendBtn.setIconSize(QSize(300, 300))
        self.mpSendBtn.setAutoDefault(False)
        self.mpSendBtn.setFlat(False)

        self.verticalLayout_4.addWidget(self.mpSendBtn)

        self.label_6 = QLabel(self.frame_18)
        self.label_6.setObjectName(u"label_6")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy4)
        self.label_6.setFont(font4)

        self.verticalLayout_4.addWidget(self.label_6, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout_13.addWidget(self.frame_18)


        self.horizontalLayout_4.addWidget(self.frame_9)

        self.frame_16 = QFrame(self.frame_5)
        self.frame_16.setObjectName(u"frame_16")
        self.horizontalLayout_14 = QHBoxLayout(self.frame_16)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.frame_19 = QFrame(self.frame_16)
        self.frame_19.setObjectName(u"frame_19")
        self.frame_19.setMaximumSize(QSize(16777215, 900))
        self.verticalLayout_5 = QVBoxLayout(self.frame_19)
        self.verticalLayout_5.setSpacing(10)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(40, 40, 40, 60)
        self.mpReceiveBtn = QPushButton(self.frame_19)
        self.mpReceiveBtn.setObjectName(u"mpReceiveBtn")
        sizePolicy3.setHeightForWidth(self.mpReceiveBtn.sizePolicy().hasHeightForWidth())
        self.mpReceiveBtn.setSizePolicy(sizePolicy3)
        self.mpReceiveBtn.setStyleSheet(u"background-color: rgb(31, 149, 239);")
        icon3 = QIcon()
        icon3.addFile(u":/white/icons_white/font_awesome/solid/box-open.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.mpReceiveBtn.setIcon(icon3)
        self.mpReceiveBtn.setIconSize(QSize(300, 300))
        self.mpReceiveBtn.setAutoDefault(False)
        self.mpReceiveBtn.setFlat(False)

        self.verticalLayout_5.addWidget(self.mpReceiveBtn)

        self.label_7 = QLabel(self.frame_19)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font4)

        self.verticalLayout_5.addWidget(self.label_7, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout_14.addWidget(self.frame_19)


        self.horizontalLayout_4.addWidget(self.frame_16)


        self.gridLayout.addWidget(self.frame_5, 0, 0, 1, 1)

        self.myStackedWidget.addWidget(self.home_page)
        self.location_page = QWidget()
        self.location_page.setObjectName(u"location_page")
        self.gridLayout_4 = QGridLayout(self.location_page)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.frame_8 = QFrame(self.location_page)
        self.frame_8.setObjectName(u"frame_8")
        self.verticalLayout_2 = QVBoxLayout(self.frame_8)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_10 = QFrame(self.frame_8)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(98, 160, 234);\n"
"")
        self.frame_10.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_10)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, 0, -1, 0)
        self.mpBacktoHomePageBtn = QPushButton(self.frame_10)
        self.mpBacktoHomePageBtn.setObjectName(u"mpBacktoHomePageBtn")
        self.mpBacktoHomePageBtn.setMinimumSize(QSize(50, 50))
        self.mpBacktoHomePageBtn.setMaximumSize(QSize(50, 50))
        icon4 = QIcon()
        icon4.addFile(u":/white/icons_white/font_awesome/solid/angle-left.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.mpBacktoHomePageBtn.setIcon(icon4)
        self.mpBacktoHomePageBtn.setIconSize(QSize(40, 40))

        self.horizontalLayout_5.addWidget(self.mpBacktoHomePageBtn)

        self.label_2 = QLabel(self.frame_10)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        font5 = QFont()
        font5.setFamilies([u"Ubuntu Sans"])
        font5.setPointSize(40)
        font5.setBold(True)
        font5.setItalic(True)
        self.label_2.setFont(font5)

        self.horizontalLayout_5.addWidget(self.label_2)


        self.verticalLayout_2.addWidget(self.frame_10)

        self.frame_11 = QFrame(self.frame_8)
        self.frame_11.setObjectName(u"frame_11")
        sizePolicy2.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(sizePolicy2)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_10.setSpacing(6)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(-1, -1, -1, 80)
        self.frame_12 = QFrame(self.frame_11)
        self.frame_12.setObjectName(u"frame_12")
        sizePolicy1.setHeightForWidth(self.frame_12.sizePolicy().hasHeightForWidth())
        self.frame_12.setSizePolicy(sizePolicy1)
        self.gridLayout_2 = QGridLayout(self.frame_12)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QGroupBox(self.frame_12)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setStyleSheet(u"QGroupBox{\n"
"	border-radius:20px;\n"
"	background-color: rgb(153, 193, 241);\n"
"}")
        self.mpMaplb = QLabel(self.groupBox)
        self.mpMaplb.setObjectName(u"mpMaplb")
        self.mpMaplb.setGeometry(QRect(9, 9, 1401, 762))
        sizePolicy.setHeightForWidth(self.mpMaplb.sizePolicy().hasHeightForWidth())
        self.mpMaplb.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)


        self.horizontalLayout_10.addWidget(self.frame_12)

        self.frame_13 = QFrame(self.frame_11)
        self.frame_13.setObjectName(u"frame_13")
        self.verticalLayout_6 = QVBoxLayout(self.frame_13)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(10, 0, 0, 0)
        self.frame_14 = QFrame(self.frame_13)
        self.frame_14.setObjectName(u"frame_14")
        self.horizontalLayout_11 = QHBoxLayout(self.frame_14)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, -1, 0, -1)
        self.mpTargetCmb = QComboBox(self.frame_14)
        self.mpTargetCmb.setObjectName(u"mpTargetCmb")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.mpTargetCmb.sizePolicy().hasHeightForWidth())
        self.mpTargetCmb.setSizePolicy(sizePolicy5)
        self.mpTargetCmb.setMinimumSize(QSize(0, 80))
        font6 = QFont()
        font6.setPointSize(20)
        self.mpTargetCmb.setFont(font6)
        self.mpTargetCmb.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.mpTargetCmb.setStyleSheet(u"background-color: rgba(73, 175, 245, 202);")
        self.mpTargetCmb.setMinimumContentsLength(0)
        self.mpTargetCmb.setIconSize(QSize(40, 40))
        self.mpTargetCmb.setPlaceholderText(u"")
        self.mpTargetCmb.setFrame(True)

        self.horizontalLayout_11.addWidget(self.mpTargetCmb)


        self.verticalLayout_6.addWidget(self.frame_14)

        self.label_5 = QLabel(self.frame_13)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(400, 0))
        font7 = QFont()
        font7.setFamilies([u"Ubuntu Sans"])
        font7.setPointSize(35)
        font7.setBold(True)
        font7.setItalic(True)
        self.label_5.setFont(font7)

        self.verticalLayout_6.addWidget(self.label_5)

        self.mpTargetLb = QLabel(self.frame_13)
        self.mpTargetLb.setObjectName(u"mpTargetLb")
        sizePolicy2.setHeightForWidth(self.mpTargetLb.sizePolicy().hasHeightForWidth())
        self.mpTargetLb.setSizePolicy(sizePolicy2)
        font8 = QFont()
        font8.setPointSize(60)
        self.mpTargetLb.setFont(font8)
        self.mpTargetLb.setStyleSheet(u"border-color: rgb(252, 250, 79);\n"
"color: rgb(99, 69, 44);\n"
"background-color: rgb(146, 212, 244);\n"
"\n"
"border-radius:20px;")
        self.mpTargetLb.setFrameShape(QFrame.Shape.NoFrame)
        self.mpTargetLb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_6.addWidget(self.mpTargetLb)

        self.frame_15 = QFrame(self.frame_13)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setMinimumSize(QSize(0, 50))
        self.horizontalLayout_12 = QHBoxLayout(self.frame_15)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.mpCancelBtn = QPushButton(self.frame_15)
        self.mpCancelBtn.setObjectName(u"mpCancelBtn")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.mpCancelBtn.sizePolicy().hasHeightForWidth())
        self.mpCancelBtn.setSizePolicy(sizePolicy6)
        self.mpCancelBtn.setMinimumSize(QSize(150, 80))
        self.mpCancelBtn.setFont(font7)
        self.mpCancelBtn.setStyleSheet(u"\n"
"background-color: rgb(224, 27, 36);")

        self.horizontalLayout_12.addWidget(self.mpCancelBtn)

        self.mpOkBtn = QPushButton(self.frame_15)
        self.mpOkBtn.setObjectName(u"mpOkBtn")
        self.mpOkBtn.setMinimumSize(QSize(150, 80))
        self.mpOkBtn.setFont(font7)
        self.mpOkBtn.setStyleSheet(u"\n"
"background-color: rgb(51, 209, 122);\n"
"")

        self.horizontalLayout_12.addWidget(self.mpOkBtn)


        self.verticalLayout_6.addWidget(self.frame_15)


        self.horizontalLayout_10.addWidget(self.frame_13)


        self.verticalLayout_2.addWidget(self.frame_11)


        self.gridLayout_4.addWidget(self.frame_8, 0, 0, 1, 1)

        self.myStackedWidget.addWidget(self.location_page)
        self.send_page = QWidget()
        self.send_page.setObjectName(u"send_page")
        self.verticalLayout_9 = QVBoxLayout(self.send_page)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.frame_20 = QFrame(self.send_page)
        self.frame_20.setObjectName(u"frame_20")
        self.verticalLayout_7 = QVBoxLayout(self.frame_20)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.frame_21 = QFrame(self.frame_20)
        self.frame_21.setObjectName(u"frame_21")
        font9 = QFont()
        font9.setPointSize(50)
        self.frame_21.setFont(font9)
        self.frame_21.setStyleSheet(u"\n"
"background-color: rgb(98, 160, 234);")
        self.horizontalLayout_7 = QHBoxLayout(self.frame_21)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(-1, 0, -1, 0)
        self.mpBacktoHomePageBtn_2 = QPushButton(self.frame_21)
        self.mpBacktoHomePageBtn_2.setObjectName(u"mpBacktoHomePageBtn_2")
        self.mpBacktoHomePageBtn_2.setMinimumSize(QSize(50, 50))
        self.mpBacktoHomePageBtn_2.setMaximumSize(QSize(50, 50))
        self.mpBacktoHomePageBtn_2.setIcon(icon4)
        self.mpBacktoHomePageBtn_2.setIconSize(QSize(40, 40))

        self.horizontalLayout_7.addWidget(self.mpBacktoHomePageBtn_2)

        self.label_4 = QLabel(self.frame_21)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setFont(font5)
        self.label_4.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_7.addWidget(self.label_4)


        self.verticalLayout_7.addWidget(self.frame_21)

        self.frame_22 = QFrame(self.frame_20)
        self.frame_22.setObjectName(u"frame_22")
        sizePolicy2.setHeightForWidth(self.frame_22.sizePolicy().hasHeightForWidth())
        self.frame_22.setSizePolicy(sizePolicy2)
        self.frame_22.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_36 = QFrame(self.frame_22)
        self.frame_36.setObjectName(u"frame_36")
        self.frame_36.setGeometry(QRect(210, 9, 561, 791))
        self.frame_36.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_34 = QFrame(self.frame_36)
        self.frame_34.setObjectName(u"frame_34")
        self.frame_34.setGeometry(QRect(20, 20, 521, 741))
        sizePolicy4.setHeightForWidth(self.frame_34.sizePolicy().hasHeightForWidth())
        self.frame_34.setSizePolicy(sizePolicy4)
        self.frame_34.setFrameShape(QFrame.Shape.NoFrame)
        self.mpDoorA = QPushButton(self.frame_34)
        self.mpDoorA.setObjectName(u"mpDoorA")
        self.mpDoorA.setGeometry(QRect(10, 10, 250, 180))
        font10 = QFont()
        font10.setPointSize(40)
        self.mpDoorA.setFont(font10)
        self.mpDoorA.setStyleSheet(u"")
        self.mpDoorB = QPushButton(self.frame_34)
        self.mpDoorB.setObjectName(u"mpDoorB")
        self.mpDoorB.setGeometry(QRect(260, 10, 250, 180))
        self.mpDoorB.setFont(font10)
        self.mpDoorC = QPushButton(self.frame_34)
        self.mpDoorC.setObjectName(u"mpDoorC")
        self.mpDoorC.setGeometry(QRect(10, 190, 250, 180))
        self.mpDoorC.setFont(font10)
        self.mpDoorD = QPushButton(self.frame_34)
        self.mpDoorD.setObjectName(u"mpDoorD")
        self.mpDoorD.setGeometry(QRect(260, 190, 250, 180))
        self.mpDoorD.setFont(font10)
        self.mpDoorE = QPushButton(self.frame_34)
        self.mpDoorE.setObjectName(u"mpDoorE")
        self.mpDoorE.setGeometry(QRect(10, 370, 250, 180))
        self.mpDoorE.setFont(font10)
        self.mpDoorF = QPushButton(self.frame_34)
        self.mpDoorF.setObjectName(u"mpDoorF")
        self.mpDoorF.setGeometry(QRect(260, 370, 250, 180))
        self.mpDoorF.setFont(font10)
        self.mpDoorG = QPushButton(self.frame_34)
        self.mpDoorG.setObjectName(u"mpDoorG")
        self.mpDoorG.setGeometry(QRect(10, 550, 250, 180))
        self.mpDoorG.setFont(font10)
        self.mpDoorH = QPushButton(self.frame_34)
        self.mpDoorH.setObjectName(u"mpDoorH")
        self.mpDoorH.setGeometry(QRect(260, 550, 250, 180))
        self.mpDoorH.setFont(font10)
        self.frame_38 = QFrame(self.frame_22)
        self.frame_38.setObjectName(u"frame_38")
        self.frame_38.setGeometry(QRect(980, 9, 791, 781))
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.frame_38.sizePolicy().hasHeightForWidth())
        self.frame_38.setSizePolicy(sizePolicy7)
        self.frame_38.setMaximumSize(QSize(800, 16777215))
        self.frame_38.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_8 = QVBoxLayout(self.frame_38)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.mpQueueTable = QTableWidget(self.frame_38)
        if (self.mpQueueTable.columnCount() < 2):
            self.mpQueueTable.setColumnCount(2)
        font11 = QFont()
        font11.setFamilies([u"Suravaram"])
        font11.setPointSize(30)
        font11.setBold(False)
        font11.setItalic(True)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font11);
        __qtablewidgetitem.setBackground(QColor(31, 149, 239));
        self.mpQueueTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font11);
        __qtablewidgetitem1.setBackground(QColor(31, 149, 239));
        self.mpQueueTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.mpQueueTable.setObjectName(u"mpQueueTable")
        sizePolicy2.setHeightForWidth(self.mpQueueTable.sizePolicy().hasHeightForWidth())
        self.mpQueueTable.setSizePolicy(sizePolicy2)
        self.mpQueueTable.setBaseSize(QSize(0, 0))
        font12 = QFont()
        font12.setFamilies([u"Ubuntu Sans"])
        font12.setPointSize(30)
        font12.setItalic(True)
        self.mpQueueTable.setFont(font12)
        self.mpQueueTable.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.mpQueueTable.setShowGrid(True)
        self.mpQueueTable.setGridStyle(Qt.PenStyle.SolidLine)
        self.mpQueueTable.setRowCount(0)
        self.mpQueueTable.setColumnCount(2)
        self.mpQueueTable.horizontalHeader().setVisible(True)
        self.mpQueueTable.horizontalHeader().setDefaultSectionSize(200)
        self.mpQueueTable.horizontalHeader().setHighlightSections(False)
        self.mpQueueTable.verticalHeader().setVisible(True)
        self.mpQueueTable.verticalHeader().setCascadingSectionResizes(False)
        self.mpQueueTable.verticalHeader().setDefaultSectionSize(40)
        self.mpQueueTable.verticalHeader().setHighlightSections(True)

        self.verticalLayout_8.addWidget(self.mpQueueTable)

        self.frame_26 = QFrame(self.frame_38)
        self.frame_26.setObjectName(u"frame_26")
        self.frame_26.setEnabled(True)
        sizePolicy4.setHeightForWidth(self.frame_26.sizePolicy().hasHeightForWidth())
        self.frame_26.setSizePolicy(sizePolicy4)
        self.frame_26.setMinimumSize(QSize(0, 60))
        self.frame_26.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_26)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.mpSendConfirmBtn = QPushButton(self.frame_26)
        self.mpSendConfirmBtn.setObjectName(u"mpSendConfirmBtn")
        sizePolicy6.setHeightForWidth(self.mpSendConfirmBtn.sizePolicy().hasHeightForWidth())
        self.mpSendConfirmBtn.setSizePolicy(sizePolicy6)
        self.mpSendConfirmBtn.setMinimumSize(QSize(150, 50))
        self.mpSendConfirmBtn.setFont(font)
        self.mpSendConfirmBtn.setStyleSheet(u"\n"
"background-color: rgb(51, 209, 122);")

        self.horizontalLayout_8.addWidget(self.mpSendConfirmBtn)

        self.mpSendCancelBtn = QPushButton(self.frame_26)
        self.mpSendCancelBtn.setObjectName(u"mpSendCancelBtn")
        sizePolicy6.setHeightForWidth(self.mpSendCancelBtn.sizePolicy().hasHeightForWidth())
        self.mpSendCancelBtn.setSizePolicy(sizePolicy6)
        self.mpSendCancelBtn.setMinimumSize(QSize(150, 50))
        self.mpSendCancelBtn.setFont(font)
        self.mpSendCancelBtn.setStyleSheet(u"\n"
"background-color: rgb(224, 27, 36);")

        self.horizontalLayout_8.addWidget(self.mpSendCancelBtn)


        self.verticalLayout_8.addWidget(self.frame_26, 0, Qt.AlignmentFlag.AlignBottom)


        self.verticalLayout_7.addWidget(self.frame_22)


        self.verticalLayout_9.addWidget(self.frame_20)

        self.myStackedWidget.addWidget(self.send_page)
        self.receive_page = QWidget()
        self.receive_page.setObjectName(u"receive_page")
        self.verticalLayout_12 = QVBoxLayout(self.receive_page)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.frame_27 = QFrame(self.receive_page)
        self.frame_27.setObjectName(u"frame_27")
        self.verticalLayout_10 = QVBoxLayout(self.frame_27)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.frame_28 = QFrame(self.frame_27)
        self.frame_28.setObjectName(u"frame_28")
        self.frame_28.setStyleSheet(u"\n"
"background-color: rgb(98, 160, 234);")
        self.frame_28.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_28)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(-1, 0, -1, 0)
        self.mpBacktoHomePageBtn_3 = QPushButton(self.frame_28)
        self.mpBacktoHomePageBtn_3.setObjectName(u"mpBacktoHomePageBtn_3")
        self.mpBacktoHomePageBtn_3.setMinimumSize(QSize(50, 50))
        self.mpBacktoHomePageBtn_3.setMaximumSize(QSize(50, 50))
        self.mpBacktoHomePageBtn_3.setIcon(icon4)
        self.mpBacktoHomePageBtn_3.setIconSize(QSize(40, 40))

        self.horizontalLayout_6.addWidget(self.mpBacktoHomePageBtn_3)

        self.label_8 = QLabel(self.frame_28)
        self.label_8.setObjectName(u"label_8")
        sizePolicy1.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy1)
        self.label_8.setMaximumSize(QSize(16777215, 100))
        font13 = QFont()
        font13.setFamilies([u"Ubuntu Sans"])
        font13.setPointSize(60)
        font13.setBold(True)
        font13.setItalic(True)
        self.label_8.setFont(font13)
        self.label_8.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_6.addWidget(self.label_8, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_10.addWidget(self.frame_28)

        self.frame_29 = QFrame(self.frame_27)
        self.frame_29.setObjectName(u"frame_29")
        sizePolicy2.setHeightForWidth(self.frame_29.sizePolicy().hasHeightForWidth())
        self.frame_29.setSizePolicy(sizePolicy2)
        self.frame_29.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_16 = QHBoxLayout(self.frame_29)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.frame_30 = QFrame(self.frame_29)
        self.frame_30.setObjectName(u"frame_30")
        sizePolicy4.setHeightForWidth(self.frame_30.sizePolicy().hasHeightForWidth())
        self.frame_30.setSizePolicy(sizePolicy4)
        self.frame_30.setFrameShape(QFrame.Shape.NoFrame)
        self.gridLayout_6 = QGridLayout(self.frame_30)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.mpReceiveKeyBtn = QPushButton(self.frame_30)
        self.mpReceiveKeyBtn.setObjectName(u"mpReceiveKeyBtn")
        self.mpReceiveKeyBtn.setMinimumSize(QSize(500, 500))
        self.mpReceiveKeyBtn.setMaximumSize(QSize(500, 500))
        self.mpReceiveKeyBtn.setStyleSheet(u"border:none;")
        icon5 = QIcon()
        icon5.addFile(u":/black/Icons/font_awesome/solid/lock.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.mpReceiveKeyBtn.setIcon(icon5)
        self.mpReceiveKeyBtn.setIconSize(QSize(500, 500))

        self.gridLayout_6.addWidget(self.mpReceiveKeyBtn, 0, 1, 1, 1)


        self.horizontalLayout_16.addWidget(self.frame_30)

        self.frame_31 = QFrame(self.frame_29)
        self.frame_31.setObjectName(u"frame_31")
        self.frame_31.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_11 = QVBoxLayout(self.frame_31)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(-1, -1, -1, 60)
        self.frame_32 = QFrame(self.frame_31)
        self.frame_32.setObjectName(u"frame_32")
        self.frame_32.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_15 = QVBoxLayout(self.frame_32)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.frame_45 = QFrame(self.frame_32)
        self.frame_45.setObjectName(u"frame_45")
        font14 = QFont()
        font14.setPointSize(15)
        self.frame_45.setFont(font14)
        self.frame_45.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_17 = QVBoxLayout(self.frame_45)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.frame_44 = QFrame(self.frame_45)
        self.frame_44.setObjectName(u"frame_44")
        self.frame_44.setMaximumSize(QSize(16777215, 150))
        font15 = QFont()
        font15.setFamilies([u"Ubuntu Sans"])
        font15.setPointSize(30)
        self.frame_44.setFont(font15)
        self.frame_44.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_16 = QVBoxLayout(self.frame_44)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.label_10 = QLabel(self.frame_44)
        self.label_10.setObjectName(u"label_10")
        sizePolicy2.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy2)
        self.label_10.setMaximumSize(QSize(16777215, 150))
        font16 = QFont()
        font16.setFamilies([u"Ubuntu Sans"])
        font16.setPointSize(80)
        font16.setBold(True)
        font16.setItalic(True)
        self.label_10.setFont(font16)

        self.verticalLayout_16.addWidget(self.label_10, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_17.addWidget(self.frame_44)

        self.frame_46 = QFrame(self.frame_45)
        self.frame_46.setObjectName(u"frame_46")
        self.frame_46.setMaximumSize(QSize(16777215, 150))
        self.frame_46.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_28 = QHBoxLayout(self.frame_46)
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.label_16 = QLabel(self.frame_46)
        self.label_16.setObjectName(u"label_16")
        sizePolicy2.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy2)
        self.label_16.setMaximumSize(QSize(16777215, 150))
        self.label_16.setFont(font13)

        self.horizontalLayout_28.addWidget(self.label_16, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_17.addWidget(self.frame_46)

        self.frame_47 = QFrame(self.frame_45)
        self.frame_47.setObjectName(u"frame_47")
        self.frame_47.setMaximumSize(QSize(16777215, 150))
        font17 = QFont()
        font17.setFamilies([u"Ubuntu Sans"])
        font17.setPointSize(25)
        font17.setBold(True)
        font17.setItalic(True)
        self.frame_47.setFont(font17)
        self.frame_47.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_29 = QHBoxLayout(self.frame_47)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.mpBoxNumberlb = QLabel(self.frame_47)
        self.mpBoxNumberlb.setObjectName(u"mpBoxNumberlb")
        sizePolicy2.setHeightForWidth(self.mpBoxNumberlb.sizePolicy().hasHeightForWidth())
        self.mpBoxNumberlb.setSizePolicy(sizePolicy2)
        self.mpBoxNumberlb.setMaximumSize(QSize(16777215, 150))
        font18 = QFont()
        font18.setFamilies([u"Ubuntu Sans"])
        font18.setPointSize(100)
        font18.setBold(True)
        font18.setItalic(True)
        self.mpBoxNumberlb.setFont(font18)
        self.mpBoxNumberlb.setStyleSheet(u"color: rgb(26, 95, 180);")

        self.horizontalLayout_29.addWidget(self.mpBoxNumberlb, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_17.addWidget(self.frame_47)


        self.verticalLayout_15.addWidget(self.frame_45)


        self.verticalLayout_11.addWidget(self.frame_32)

        self.frame_33 = QFrame(self.frame_31)
        self.frame_33.setObjectName(u"frame_33")
        self.frame_33.setMinimumSize(QSize(0, 50))
        self.frame_33.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_18 = QHBoxLayout(self.frame_33)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.mpReceiveOkBtn = QPushButton(self.frame_33)
        self.mpReceiveOkBtn.setObjectName(u"mpReceiveOkBtn")
        self.mpReceiveOkBtn.setMinimumSize(QSize(150, 80))
        font19 = QFont()
        font19.setFamilies([u"Ubuntu Sans"])
        font19.setPointSize(50)
        font19.setBold(True)
        font19.setItalic(True)
        self.mpReceiveOkBtn.setFont(font19)
        self.mpReceiveOkBtn.setStyleSheet(u"\n"
"background-color: rgb(51, 209, 122);")

        self.horizontalLayout_18.addWidget(self.mpReceiveOkBtn)

        self.mpReceiveCancelBtn = QPushButton(self.frame_33)
        self.mpReceiveCancelBtn.setObjectName(u"mpReceiveCancelBtn")
        sizePolicy6.setHeightForWidth(self.mpReceiveCancelBtn.sizePolicy().hasHeightForWidth())
        self.mpReceiveCancelBtn.setSizePolicy(sizePolicy6)
        self.mpReceiveCancelBtn.setMinimumSize(QSize(150, 80))
        self.mpReceiveCancelBtn.setFont(font19)
        self.mpReceiveCancelBtn.setStyleSheet(u"\n"
"background-color: rgb(224, 27, 36);")

        self.horizontalLayout_18.addWidget(self.mpReceiveCancelBtn)


        self.verticalLayout_11.addWidget(self.frame_33)


        self.horizontalLayout_16.addWidget(self.frame_31)


        self.verticalLayout_10.addWidget(self.frame_29)


        self.verticalLayout_12.addWidget(self.frame_27)

        self.myStackedWidget.addWidget(self.receive_page)
        self.Moving_page = QWidget()
        self.Moving_page.setObjectName(u"Moving_page")
        self.horizontalLayout_33 = QHBoxLayout(self.Moving_page)
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.frame_48 = QFrame(self.Moving_page)
        self.frame_48.setObjectName(u"frame_48")
        self.verticalLayout_18 = QVBoxLayout(self.frame_48)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.frame_49 = QFrame(self.frame_48)
        self.frame_49.setObjectName(u"frame_49")
        self.frame_49.setMaximumSize(QSize(16777215, 100))
        self.frame_49.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(98, 160, 234);")
        self.frame_49.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_17 = QHBoxLayout(self.frame_49)
        self.horizontalLayout_17.setSpacing(6)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(-1, 0, -1, 0)
        self.label_18 = QLabel(self.frame_49)
        self.label_18.setObjectName(u"label_18")
        sizePolicy1.setHeightForWidth(self.label_18.sizePolicy().hasHeightForWidth())
        self.label_18.setSizePolicy(sizePolicy1)
        self.label_18.setMaximumSize(QSize(16777215, 100))
        self.label_18.setFont(font13)

        self.horizontalLayout_17.addWidget(self.label_18, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_18.addWidget(self.frame_49)

        self.frame_50 = QFrame(self.frame_48)
        self.frame_50.setObjectName(u"frame_50")
        sizePolicy2.setHeightForWidth(self.frame_50.sizePolicy().hasHeightForWidth())
        self.frame_50.setSizePolicy(sizePolicy2)
        self.frame_50.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_27 = QHBoxLayout(self.frame_50)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.frame_53 = QFrame(self.frame_50)
        self.frame_53.setObjectName(u"frame_53")
        sizePolicy1.setHeightForWidth(self.frame_53.sizePolicy().hasHeightForWidth())
        self.frame_53.setSizePolicy(sizePolicy1)
        self.frame_53.setStyleSheet(u"\n"
"background-color: rgb(246, 245, 244);\n"
"")
        self.frame_53.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_19 = QVBoxLayout(self.frame_53)
        self.verticalLayout_19.setSpacing(5)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(-1, -1, -1, 60)
        self.pushButton_5 = QPushButton(self.frame_53)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setMinimumSize(QSize(400, 400))
        self.pushButton_5.setMaximumSize(QSize(500, 500))
        self.pushButton_5.setStyleSheet(u"border:none;")
        icon6 = QIcon()
        icon6.addFile(u":/black/Icons/font_awesome/solid/location-dot.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_5.setIcon(icon6)
        self.pushButton_5.setIconSize(QSize(350, 350))

        self.verticalLayout_19.addWidget(self.pushButton_5, 0, Qt.AlignmentFlag.AlignHCenter)

        self.mpStationTargetLb = QLabel(self.frame_53)
        self.mpStationTargetLb.setObjectName(u"mpStationTargetLb")
        sizePolicy4.setHeightForWidth(self.mpStationTargetLb.sizePolicy().hasHeightForWidth())
        self.mpStationTargetLb.setSizePolicy(sizePolicy4)
        self.mpStationTargetLb.setMaximumSize(QSize(16777215, 100))
        font20 = QFont()
        font20.setFamilies([u"Ubuntu Sans"])
        font20.setPointSize(70)
        font20.setBold(True)
        font20.setItalic(True)
        self.mpStationTargetLb.setFont(font20)

        self.verticalLayout_19.addWidget(self.mpStationTargetLb, 0, Qt.AlignmentFlag.AlignHCenter)

        self.label_20 = QLabel(self.frame_53)
        self.label_20.setObjectName(u"label_20")
        sizePolicy4.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy4)
        self.label_20.setMaximumSize(QSize(16777215, 150))
        self.label_20.setFont(font20)
        self.label_20.setStyleSheet(u"color: rgb(38, 162, 105);\n"
"")

        self.verticalLayout_19.addWidget(self.label_20, 0, Qt.AlignmentFlag.AlignHCenter)

        self.pushButton_6 = QPushButton(self.frame_53)
        self.pushButton_6.setObjectName(u"pushButton_6")
        sizePolicy5.setHeightForWidth(self.pushButton_6.sizePolicy().hasHeightForWidth())
        self.pushButton_6.setSizePolicy(sizePolicy5)
        self.pushButton_6.setMinimumSize(QSize(800, 10))
        self.pushButton_6.setMaximumSize(QSize(16777215, 10))
        self.pushButton_6.setStyleSheet(u"background-color: rgb(94, 92, 100);")

        self.verticalLayout_19.addWidget(self.pushButton_6)

        self.mpSendCancelBtn2 = QPushButton(self.frame_53)
        self.mpSendCancelBtn2.setObjectName(u"mpSendCancelBtn2")
        sizePolicy5.setHeightForWidth(self.mpSendCancelBtn2.sizePolicy().hasHeightForWidth())
        self.mpSendCancelBtn2.setSizePolicy(sizePolicy5)
        self.mpSendCancelBtn2.setMinimumSize(QSize(0, 80))
        self.mpSendCancelBtn2.setFont(font5)
        self.mpSendCancelBtn2.setStyleSheet(u"background-color: rgb(224, 27, 36);")

        self.verticalLayout_19.addWidget(self.mpSendCancelBtn2)


        self.horizontalLayout_27.addWidget(self.frame_53)


        self.verticalLayout_18.addWidget(self.frame_50)


        self.horizontalLayout_33.addWidget(self.frame_48)

        self.myStackedWidget.addWidget(self.Moving_page)
        self.Move2Target_page = QWidget()
        self.Move2Target_page.setObjectName(u"Move2Target_page")
        self.horizontalLayout_32 = QHBoxLayout(self.Move2Target_page)
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.frame_54 = QFrame(self.Move2Target_page)
        self.frame_54.setObjectName(u"frame_54")
        self.verticalLayout_20 = QVBoxLayout(self.frame_54)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.frame_55 = QFrame(self.frame_54)
        self.frame_55.setObjectName(u"frame_55")
        self.frame_55.setMaximumSize(QSize(16777215, 100))
        self.frame_55.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(98, 160, 234);")
        self.frame_55.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_30 = QHBoxLayout(self.frame_55)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalLayout_30.setContentsMargins(-1, 0, -1, 0)
        self.label_19 = QLabel(self.frame_55)
        self.label_19.setObjectName(u"label_19")
        sizePolicy1.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy1)
        self.label_19.setMaximumSize(QSize(16777215, 150))
        self.label_19.setFont(font13)

        self.horizontalLayout_30.addWidget(self.label_19, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_20.addWidget(self.frame_55)

        self.frame_56 = QFrame(self.frame_54)
        self.frame_56.setObjectName(u"frame_56")
        sizePolicy2.setHeightForWidth(self.frame_56.sizePolicy().hasHeightForWidth())
        self.frame_56.setSizePolicy(sizePolicy2)
        self.frame_56.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_31 = QHBoxLayout(self.frame_56)
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.frame_57 = QFrame(self.frame_56)
        self.frame_57.setObjectName(u"frame_57")
        sizePolicy1.setHeightForWidth(self.frame_57.sizePolicy().hasHeightForWidth())
        self.frame_57.setSizePolicy(sizePolicy1)
        self.frame_57.setStyleSheet(u"\n"
"background-color: rgb(246, 245, 244);\n"
"")
        self.frame_57.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_21 = QVBoxLayout(self.frame_57)
        self.verticalLayout_21.setSpacing(9)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(-1, -1, -1, 60)
        self.pushButton_7 = QPushButton(self.frame_57)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setMinimumSize(QSize(150, 150))
        self.pushButton_7.setMaximumSize(QSize(500, 500))
        self.pushButton_7.setStyleSheet(u"border:none;")
        self.pushButton_7.setIcon(icon6)
        self.pushButton_7.setIconSize(QSize(350, 350))

        self.verticalLayout_21.addWidget(self.pushButton_7, 0, Qt.AlignmentFlag.AlignHCenter)

        self.mpStationTargetLb_2 = QLabel(self.frame_57)
        self.mpStationTargetLb_2.setObjectName(u"mpStationTargetLb_2")
        sizePolicy4.setHeightForWidth(self.mpStationTargetLb_2.sizePolicy().hasHeightForWidth())
        self.mpStationTargetLb_2.setSizePolicy(sizePolicy4)
        self.mpStationTargetLb_2.setMaximumSize(QSize(16777215, 100))
        self.mpStationTargetLb_2.setFont(font20)

        self.verticalLayout_21.addWidget(self.mpStationTargetLb_2, 0, Qt.AlignmentFlag.AlignHCenter)

        self.label_21 = QLabel(self.frame_57)
        self.label_21.setObjectName(u"label_21")
        sizePolicy4.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy4)
        self.label_21.setMaximumSize(QSize(16777215, 150))
        self.label_21.setFont(font20)
        self.label_21.setStyleSheet(u"color: rgb(38, 162, 105);\n"
"")

        self.verticalLayout_21.addWidget(self.label_21, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout_31.addWidget(self.frame_57)


        self.verticalLayout_20.addWidget(self.frame_56)


        self.horizontalLayout_32.addWidget(self.frame_54)

        self.myStackedWidget.addWidget(self.Move2Target_page)

        self.gridLayout_3.addWidget(self.myStackedWidget, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.frame_2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.mpTargetCmb.currentTextChanged.connect(self.mpTargetLb.setText)

        self.myStackedWidget.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("")
        self.mpStatuslb.setText(QCoreApplication.translate("MainWindow", u"Status: STANDBY", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"98%", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"9:30", None))
        self.mpTargetBtn.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u0e15\u0e33\u0e41\u0e2b\u0e19\u0e48\u0e07\u0e40\u0e1b\u0e49\u0e32\u0e2b\u0e21\u0e32\u0e22", None))
        self.mpSendBtn.setText("")
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u0e2a\u0e48\u0e07\u0e02\u0e2d\u0e07", None))
        self.mpReceiveBtn.setText("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u0e23\u0e31\u0e1a\u0e02\u0e2d\u0e07", None))
        self.mpBacktoHomePageBtn.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u0e42\u0e1b\u0e23\u0e14\u0e40\u0e25\u0e37\u0e2d\u0e01\u0e15\u0e33\u0e41\u0e2b\u0e19\u0e48\u0e07\u0e1b\u0e25\u0e32\u0e22\u0e17\u0e32\u0e07\u0e02\u0e2d\u0e07\u0e2b\u0e38\u0e48\u0e19\u0e22\u0e19\u0e15\u0e4c", None))
        self.groupBox.setTitle("")
        self.mpMaplb.setText("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"   \u0e15\u0e33\u0e41\u0e2b\u0e19\u0e48\u0e07\u0e1b\u0e25\u0e32\u0e22\u0e17\u0e32\u0e07\u0e17\u0e35\u0e48\u0e40\u0e25\u0e37\u0e2d\u0e01 \u0e04\u0e37\u0e2d", None))
        self.mpTargetLb.setText("")
        self.mpCancelBtn.setText(QCoreApplication.translate("MainWindow", u"\u0e22\u0e01\u0e40\u0e25\u0e34\u0e01", None))
        self.mpOkBtn.setText(QCoreApplication.translate("MainWindow", u"\u0e22\u0e37\u0e19\u0e22\u0e31\u0e19", None))
        self.mpBacktoHomePageBtn_2.setText("")
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u0e01\u0e23\u0e38\u0e13\u0e32\u0e40\u0e25\u0e37\u0e2d\u0e01\u0e0a\u0e48\u0e2d\u0e07\u0e27\u0e32\u0e07\u0e02\u0e2d\u0e07\u0e41\u0e25\u0e30\u0e43\u0e2a\u0e48\u0e02\u0e2d\u0e07\u0e43\u0e2b\u0e49\u0e40\u0e23\u0e35\u0e22\u0e1a\u0e23\u0e49\u0e2d\u0e22", None))
        self.mpDoorA.setText(QCoreApplication.translate("MainWindow", u"A", None))
        self.mpDoorB.setText(QCoreApplication.translate("MainWindow", u"B", None))
        self.mpDoorC.setText(QCoreApplication.translate("MainWindow", u"C", None))
        self.mpDoorD.setText(QCoreApplication.translate("MainWindow", u"D", None))
        self.mpDoorE.setText(QCoreApplication.translate("MainWindow", u"E", None))
        self.mpDoorF.setText(QCoreApplication.translate("MainWindow", u"F", None))
        self.mpDoorG.setText(QCoreApplication.translate("MainWindow", u"G", None))
        self.mpDoorH.setText(QCoreApplication.translate("MainWindow", u"H", None))
        ___qtablewidgetitem = self.mpQueueTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Box ", None));
        ___qtablewidgetitem1 = self.mpQueueTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Station", None));
        self.mpSendConfirmBtn.setText(QCoreApplication.translate("MainWindow", u"\u0e22\u0e37\u0e19\u0e22\u0e31\u0e19\u0e17\u0e31\u0e49\u0e07\u0e2b\u0e21\u0e14", None))
        self.mpSendCancelBtn.setText(QCoreApplication.translate("MainWindow", u"\u0e22\u0e01\u0e40\u0e25\u0e34\u0e01 \u0e23\u0e32\u0e22\u0e01\u0e32\u0e23\u0e17\u0e35\u0e48\u0e40\u0e25\u0e37\u0e2d\u0e01", None))
        self.mpBacktoHomePageBtn_3.setText("")
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"\u0e1b\u0e25\u0e32\u0e22\u0e17\u0e32\u0e07", None))
        self.mpReceiveKeyBtn.setText("")
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"\u0e23\u0e2d\u0e1c\u0e39\u0e49\u0e23\u0e31\u0e1a\u0e02\u0e2d\u0e07", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"\u0e42\u0e1b\u0e23\u0e14\u0e23\u0e31\u0e1a\u0e02\u0e2d\u0e07\u0e17\u0e35\u0e48\u0e0a\u0e48\u0e2d\u0e07 ", None))
        self.mpBoxNumberlb.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.mpReceiveOkBtn.setText(QCoreApplication.translate("MainWindow", u"\u0e23\u0e31\u0e1a\u0e02\u0e2d\u0e07", None))
        self.mpReceiveCancelBtn.setText(QCoreApplication.translate("MainWindow", u"\u0e02\u0e49\u0e32\u0e21\u0e01\u0e32\u0e23\u0e2a\u0e48\u0e07", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"\u0e2a\u0e16\u0e32\u0e19\u0e35", None))
        self.pushButton_5.setText("")
        self.mpStationTargetLb.setText(QCoreApplication.translate("MainWindow", u"Station B", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"\u0e01\u0e33\u0e25\u0e31\u0e07\u0e2d\u0e22\u0e39\u0e48\u0e23\u0e30\u0e2b\u0e27\u0e48\u0e32\u0e07\u0e01\u0e32\u0e23\u0e2a\u0e48\u0e07\u0e02\u0e2d\u0e07", None))
        self.pushButton_6.setText("")
        self.mpSendCancelBtn2.setText(QCoreApplication.translate("MainWindow", u"\u0e22\u0e01\u0e40\u0e25\u0e34\u0e01\u0e01\u0e32\u0e23\u0e08\u0e31\u0e14\u0e2a\u0e48\u0e07", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"\u0e2a\u0e16\u0e32\u0e19\u0e35", None))
        self.pushButton_7.setText("")
        self.mpStationTargetLb_2.setText(QCoreApplication.translate("MainWindow", u"Station B", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"\u0e01\u0e33\u0e25\u0e31\u0e07\u0e2d\u0e22\u0e39\u0e48\u0e23\u0e30\u0e2b\u0e27\u0e48\u0e32\u0e07\u0e01\u0e32\u0e23\u0e40\u0e14\u0e34\u0e19\u0e17\u0e32\u0e07", None))
    # retranslateUi

