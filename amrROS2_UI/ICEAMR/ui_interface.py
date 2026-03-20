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
        MainWindow.resize(1923, 1132)
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
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy1)
        self.frame_3.setMinimumSize(QSize(0, 90))
        self.frame_3.setMaximumSize(QSize(200, 16777215))
        font1 = QFont()
        font1.setBold(False)
        font1.setItalic(True)
        self.frame_3.setFont(font1)
        self.gridLayout_5 = QGridLayout(self.frame_3)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.pushButton_3 = QPushButton(self.frame_3)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setMinimumSize(QSize(0, 40))
        font2 = QFont()
        font2.setPointSize(30)
        font2.setBold(True)
        font2.setItalic(False)
        self.pushButton_3.setFont(font2)

        self.gridLayout_5.addWidget(self.pushButton_3, 0, 0, 1, 1)


        self.horizontalLayout_2.addWidget(self.frame_3)

        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        sizePolicy1.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy1)
        self.horizontalLayout = QHBoxLayout(self.frame_4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.mpStatuslb = QLabel(self.frame_4)
        self.mpStatuslb.setObjectName(u"mpStatuslb")
        font3 = QFont()
        font3.setFamilies([u"Ubuntu Sans"])
        font3.setPointSize(40)
        font3.setBold(False)
        font3.setItalic(True)
        self.mpStatuslb.setFont(font3)

        self.horizontalLayout.addWidget(self.mpStatuslb, 0, Qt.AlignmentFlag.AlignHCenter)

        self.pushButton = QPushButton(self.frame_4)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(0, 50))
        font4 = QFont()
        font4.setPointSize(30)
        font4.setBold(True)
        self.pushButton.setFont(font4)
        icon = QIcon()
        icon.addFile(u":/white/icons_white/material_design/battery_6_bar.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QSize(40, 40))

        self.horizontalLayout.addWidget(self.pushButton, 0, Qt.AlignmentFlag.AlignRight)


        self.horizontalLayout_2.addWidget(self.frame_4)

        self.frame_25 = QFrame(self.frame)
        self.frame_25.setObjectName(u"frame_25")
        self.frame_25.setStyleSheet(u"background-color: rgb(246, 97, 81);")
        self.frame_25.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_25.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.frame_25)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.mpCloseApp = QPushButton(self.frame_25)
        self.mpCloseApp.setObjectName(u"mpCloseApp")
        self.mpCloseApp.setFont(font)
        self.mpCloseApp.setIconSize(QSize(16, 15))

        self.verticalLayout_15.addWidget(self.mpCloseApp)


        self.horizontalLayout_2.addWidget(self.frame_25, 0, Qt.AlignmentFlag.AlignRight)


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
        font5 = QFont()
        font5.setFamilies([u"Ubuntu Sans"])
        font5.setPointSize(60)
        font5.setItalic(True)
        self.label_3.setFont(font5)

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
        self.label_6.setFont(font5)

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
        self.label_7.setFont(font5)

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
        font6 = QFont()
        font6.setFamilies([u"Ubuntu Sans"])
        font6.setPointSize(40)
        font6.setBold(True)
        font6.setItalic(True)
        self.label_2.setFont(font6)

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
        self.gridLayout_7 = QGridLayout(self.groupBox)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.pushButton_2 = QPushButton(self.groupBox)
        self.pushButton_2.setObjectName(u"pushButton_2")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy5)
        font7 = QFont()
        font7.setPointSize(100)
        self.pushButton_2.setFont(font7)
        self.pushButton_2.setStyleSheet(u"background-color: rgb(249, 248, 207);")
        icon5 = QIcon()
        icon5.addFile(u":/dock/Icons_dock/navigate1000_500.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_2.setIcon(icon5)
        self.pushButton_2.setIconSize(QSize(1000, 1000))

        self.gridLayout_7.addWidget(self.pushButton_2, 0, 0, 1, 1)


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
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.mpTargetCmb.sizePolicy().hasHeightForWidth())
        self.mpTargetCmb.setSizePolicy(sizePolicy6)
        self.mpTargetCmb.setMinimumSize(QSize(0, 80))
        font8 = QFont()
        font8.setPointSize(20)
        self.mpTargetCmb.setFont(font8)
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
        font9 = QFont()
        font9.setFamilies([u"Ubuntu Sans"])
        font9.setPointSize(35)
        font9.setBold(True)
        font9.setItalic(True)
        self.label_5.setFont(font9)

        self.verticalLayout_6.addWidget(self.label_5)

        self.mpTargetLb = QLabel(self.frame_13)
        self.mpTargetLb.setObjectName(u"mpTargetLb")
        sizePolicy2.setHeightForWidth(self.mpTargetLb.sizePolicy().hasHeightForWidth())
        self.mpTargetLb.setSizePolicy(sizePolicy2)
        font10 = QFont()
        font10.setPointSize(60)
        self.mpTargetLb.setFont(font10)
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
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.mpCancelBtn.sizePolicy().hasHeightForWidth())
        self.mpCancelBtn.setSizePolicy(sizePolicy7)
        self.mpCancelBtn.setMinimumSize(QSize(150, 80))
        self.mpCancelBtn.setFont(font9)
        self.mpCancelBtn.setStyleSheet(u"\n"
"background-color: rgb(224, 27, 36);")

        self.horizontalLayout_12.addWidget(self.mpCancelBtn)

        self.mpOkBtn = QPushButton(self.frame_15)
        self.mpOkBtn.setObjectName(u"mpOkBtn")
        self.mpOkBtn.setMinimumSize(QSize(150, 80))
        self.mpOkBtn.setFont(font9)
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
        font11 = QFont()
        font11.setPointSize(50)
        self.frame_21.setFont(font11)
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
        self.label_4.setFont(font6)
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
        font12 = QFont()
        font12.setPointSize(40)
        self.mpDoorA.setFont(font12)
        self.mpDoorA.setStyleSheet(u"")
        self.mpDoorB = QPushButton(self.frame_34)
        self.mpDoorB.setObjectName(u"mpDoorB")
        self.mpDoorB.setGeometry(QRect(260, 10, 250, 180))
        self.mpDoorB.setFont(font12)
        self.mpDoorC = QPushButton(self.frame_34)
        self.mpDoorC.setObjectName(u"mpDoorC")
        self.mpDoorC.setGeometry(QRect(10, 190, 250, 180))
        self.mpDoorC.setFont(font12)
        self.mpDoorD = QPushButton(self.frame_34)
        self.mpDoorD.setObjectName(u"mpDoorD")
        self.mpDoorD.setGeometry(QRect(260, 190, 250, 180))
        self.mpDoorD.setFont(font12)
        self.mpDoorE = QPushButton(self.frame_34)
        self.mpDoorE.setObjectName(u"mpDoorE")
        self.mpDoorE.setGeometry(QRect(10, 370, 250, 180))
        self.mpDoorE.setFont(font12)
        self.mpDoorF = QPushButton(self.frame_34)
        self.mpDoorF.setObjectName(u"mpDoorF")
        self.mpDoorF.setGeometry(QRect(260, 370, 250, 180))
        self.mpDoorF.setFont(font12)
        self.mpDoorG = QPushButton(self.frame_34)
        self.mpDoorG.setObjectName(u"mpDoorG")
        self.mpDoorG.setGeometry(QRect(10, 550, 250, 180))
        self.mpDoorG.setFont(font12)
        self.mpDoorH = QPushButton(self.frame_34)
        self.mpDoorH.setObjectName(u"mpDoorH")
        self.mpDoorH.setGeometry(QRect(260, 550, 250, 180))
        self.mpDoorH.setFont(font12)
        self.frame_38 = QFrame(self.frame_22)
        self.frame_38.setObjectName(u"frame_38")
        self.frame_38.setGeometry(QRect(980, 9, 791, 781))
        sizePolicy5.setHeightForWidth(self.frame_38.sizePolicy().hasHeightForWidth())
        self.frame_38.setSizePolicy(sizePolicy5)
        self.frame_38.setMaximumSize(QSize(800, 16777215))
        self.frame_38.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_8 = QVBoxLayout(self.frame_38)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.mpQueueTable = QTableWidget(self.frame_38)
        if (self.mpQueueTable.columnCount() < 2):
            self.mpQueueTable.setColumnCount(2)
        font13 = QFont()
        font13.setFamilies([u"Suravaram"])
        font13.setPointSize(30)
        font13.setBold(False)
        font13.setItalic(True)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font13);
        __qtablewidgetitem.setBackground(QColor(31, 149, 239));
        self.mpQueueTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font13);
        __qtablewidgetitem1.setBackground(QColor(31, 149, 239));
        self.mpQueueTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.mpQueueTable.setObjectName(u"mpQueueTable")
        sizePolicy2.setHeightForWidth(self.mpQueueTable.sizePolicy().hasHeightForWidth())
        self.mpQueueTable.setSizePolicy(sizePolicy2)
        self.mpQueueTable.setBaseSize(QSize(0, 0))
        font14 = QFont()
        font14.setFamilies([u"Ubuntu Sans"])
        font14.setPointSize(30)
        font14.setItalic(True)
        self.mpQueueTable.setFont(font14)
        self.mpQueueTable.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.mpQueueTable.setStyleSheet(u"")
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
        sizePolicy7.setHeightForWidth(self.mpSendConfirmBtn.sizePolicy().hasHeightForWidth())
        self.mpSendConfirmBtn.setSizePolicy(sizePolicy7)
        self.mpSendConfirmBtn.setMinimumSize(QSize(150, 50))
        font15 = QFont()
        font15.setPointSize(30)
        font15.setItalic(True)
        self.mpSendConfirmBtn.setFont(font15)
        self.mpSendConfirmBtn.setStyleSheet(u"\n"
"background-color: rgb(51, 209, 122);")

        self.horizontalLayout_8.addWidget(self.mpSendConfirmBtn)

        self.mpSendCancelBtn = QPushButton(self.frame_26)
        self.mpSendCancelBtn.setObjectName(u"mpSendCancelBtn")
        sizePolicy7.setHeightForWidth(self.mpSendCancelBtn.sizePolicy().hasHeightForWidth())
        self.mpSendCancelBtn.setSizePolicy(sizePolicy7)
        self.mpSendCancelBtn.setMinimumSize(QSize(150, 50))
        self.mpSendCancelBtn.setFont(font15)
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
        self.frame_28.setMaximumSize(QSize(16777215, 100))
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
        self.label_8.setFont(font6)
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
        sizePolicy6.setHeightForWidth(self.frame_30.sizePolicy().hasHeightForWidth())
        self.frame_30.setSizePolicy(sizePolicy6)
        self.frame_30.setMinimumSize(QSize(0, 800))
        self.frame_30.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_14 = QVBoxLayout(self.frame_30)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.frame_24 = QFrame(self.frame_30)
        self.frame_24.setObjectName(u"frame_24")
        self.frame_24.setStyleSheet(u"background-color: rgb(249, 248, 207);")
        self.frame_24.setFrameShape(QFrame.Shape.Box)
        self.frame_24.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_20 = QHBoxLayout(self.frame_24)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.label_12 = QLabel(self.frame_24)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setFont(font5)
        self.label_12.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_20.addWidget(self.label_12)

        self.label_13 = QLabel(self.frame_24)
        self.label_13.setObjectName(u"label_13")
        font16 = QFont()
        font16.setFamilies([u"Ubuntu Sans"])
        font16.setPointSize(50)
        font16.setItalic(True)
        self.label_13.setFont(font16)
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_20.addWidget(self.label_13)


        self.verticalLayout_14.addWidget(self.frame_24)

        self.frame_7 = QFrame(self.frame_30)
        self.frame_7.setObjectName(u"frame_7")
        sizePolicy4.setHeightForWidth(self.frame_7.sizePolicy().hasHeightForWidth())
        self.frame_7.setSizePolicy(sizePolicy4)
        self.frame_7.setStyleSheet(u"background-color: rgb(249, 248, 207);")
        self.frame_7.setFrameShape(QFrame.Shape.Box)
        self.frame_7.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label = QLabel(self.frame_7)
        self.label.setObjectName(u"label")
        self.label.setFont(font5)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_15.addWidget(self.label)

        self.mpTargetTextLb = QLabel(self.frame_7)
        self.mpTargetTextLb.setObjectName(u"mpTargetTextLb")
        self.mpTargetTextLb.setFont(font5)
        self.mpTargetTextLb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_15.addWidget(self.mpTargetTextLb)


        self.verticalLayout_14.addWidget(self.frame_7)

        self.frame_23 = QFrame(self.frame_30)
        self.frame_23.setObjectName(u"frame_23")
        sizePolicy4.setHeightForWidth(self.frame_23.sizePolicy().hasHeightForWidth())
        self.frame_23.setSizePolicy(sizePolicy4)
        self.frame_23.setStyleSheet(u"background-color: rgb(249, 248, 207);")
        self.frame_23.setFrameShape(QFrame.Shape.Box)
        self.frame_23.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_19 = QHBoxLayout(self.frame_23)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.label_9 = QLabel(self.frame_23)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font5)
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_19.addWidget(self.label_9)

        self.mpBoxTextLb = QLabel(self.frame_23)
        self.mpBoxTextLb.setObjectName(u"mpBoxTextLb")
        font17 = QFont()
        font17.setPointSize(60)
        font17.setItalic(True)
        self.mpBoxTextLb.setFont(font17)
        self.mpBoxTextLb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_19.addWidget(self.mpBoxTextLb)


        self.verticalLayout_14.addWidget(self.frame_23)


        self.horizontalLayout_16.addWidget(self.frame_30, 0, Qt.AlignmentFlag.AlignTop)

        self.frame_31 = QFrame(self.frame_29)
        self.frame_31.setObjectName(u"frame_31")
        sizePolicy6.setHeightForWidth(self.frame_31.sizePolicy().hasHeightForWidth())
        self.frame_31.setSizePolicy(sizePolicy6)
        self.frame_31.setMinimumSize(QSize(0, 800))
        self.frame_31.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_11 = QVBoxLayout(self.frame_31)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(-1, -1, -1, 60)
        self.frame_45 = QFrame(self.frame_31)
        self.frame_45.setObjectName(u"frame_45")
        self.frame_45.setMinimumSize(QSize(0, 780))
        font18 = QFont()
        font18.setPointSize(15)
        self.frame_45.setFont(font18)
        self.frame_45.setStyleSheet(u"background-color: rgb(246, 245, 244);")
        self.frame_45.setFrameShape(QFrame.Shape.Box)
        self.frame_45.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.frame_45)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.frame_44 = QFrame(self.frame_45)
        self.frame_44.setObjectName(u"frame_44")
        self.frame_44.setMaximumSize(QSize(16777215, 150))
        font19 = QFont()
        font19.setFamilies([u"Ubuntu Sans"])
        font19.setPointSize(30)
        self.frame_44.setFont(font19)
        self.frame_44.setStyleSheet(u"background-color: rgb(153, 193, 241);")
        self.frame_44.setFrameShape(QFrame.Shape.Box)
        self.verticalLayout_16 = QVBoxLayout(self.frame_44)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.label_10 = QLabel(self.frame_44)
        self.label_10.setObjectName(u"label_10")
        sizePolicy2.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy2)
        self.label_10.setMaximumSize(QSize(16777215, 150))
        font20 = QFont()
        font20.setFamilies([u"Ubuntu Sans"])
        font20.setPointSize(80)
        font20.setBold(True)
        font20.setItalic(True)
        self.label_10.setFont(font20)

        self.verticalLayout_16.addWidget(self.label_10, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_13.addWidget(self.frame_44)

        self.frame_46 = QFrame(self.frame_45)
        self.frame_46.setObjectName(u"frame_46")
        self.frame_46.setMaximumSize(QSize(16777215, 16777215))
        self.frame_46.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_46)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.mpBoxNumberCb = QComboBox(self.frame_46)
        self.mpBoxNumberCb.setObjectName(u"mpBoxNumberCb")
        self.mpBoxNumberCb.setMinimumSize(QSize(400, 150))
        self.mpBoxNumberCb.setMaximumSize(QSize(600, 16777215))
        font21 = QFont()
        font21.setFamilies([u"TH Sarabun New"])
        font21.setPointSize(60)
        font21.setBold(True)
        font21.setItalic(True)
        self.mpBoxNumberCb.setFont(font21)
        self.mpBoxNumberCb.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.mpBoxNumberCb.setStyleSheet(u"background-color: rgb(249, 248, 207);")
        self.mpBoxNumberCb.setMaxCount(10)
        self.mpBoxNumberCb.setFrame(True)

        self.horizontalLayout_3.addWidget(self.mpBoxNumberCb)


        self.verticalLayout_13.addWidget(self.frame_46, 0, Qt.AlignmentFlag.AlignBottom)

        self.frame_33 = QFrame(self.frame_45)
        self.frame_33.setObjectName(u"frame_33")
        self.frame_33.setMinimumSize(QSize(0, 50))
        self.frame_33.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_18 = QHBoxLayout(self.frame_33)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.mpReceiveOkBtn = QPushButton(self.frame_33)
        self.mpReceiveOkBtn.setObjectName(u"mpReceiveOkBtn")
        self.mpReceiveOkBtn.setMinimumSize(QSize(150, 80))
        font22 = QFont()
        font22.setFamilies([u"Ubuntu Sans"])
        font22.setPointSize(50)
        font22.setBold(True)
        font22.setItalic(True)
        self.mpReceiveOkBtn.setFont(font22)
        self.mpReceiveOkBtn.setStyleSheet(u"\n"
"background-color: rgb(51, 209, 122);")

        self.horizontalLayout_18.addWidget(self.mpReceiveOkBtn)


        self.verticalLayout_13.addWidget(self.frame_33, 0, Qt.AlignmentFlag.AlignBottom)


        self.verticalLayout_11.addWidget(self.frame_45)


        self.horizontalLayout_16.addWidget(self.frame_31, 0, Qt.AlignmentFlag.AlignTop)


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
        font23 = QFont()
        font23.setFamilies([u"Ubuntu Sans"])
        font23.setPointSize(60)
        font23.setBold(True)
        font23.setItalic(True)
        self.label_18.setFont(font23)

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
        font24 = QFont()
        font24.setFamilies([u"Ubuntu Sans"])
        font24.setPointSize(70)
        font24.setBold(True)
        font24.setItalic(True)
        self.mpStationTargetLb.setFont(font24)

        self.verticalLayout_19.addWidget(self.mpStationTargetLb, 0, Qt.AlignmentFlag.AlignHCenter)

        self.label_20 = QLabel(self.frame_53)
        self.label_20.setObjectName(u"label_20")
        sizePolicy4.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy4)
        self.label_20.setMaximumSize(QSize(16777215, 150))
        self.label_20.setFont(font24)
        self.label_20.setStyleSheet(u"color: rgb(38, 162, 105);\n"
"")

        self.verticalLayout_19.addWidget(self.label_20, 0, Qt.AlignmentFlag.AlignHCenter)

        self.pushButton_6 = QPushButton(self.frame_53)
        self.pushButton_6.setObjectName(u"pushButton_6")
        sizePolicy6.setHeightForWidth(self.pushButton_6.sizePolicy().hasHeightForWidth())
        self.pushButton_6.setSizePolicy(sizePolicy6)
        self.pushButton_6.setMinimumSize(QSize(800, 10))
        self.pushButton_6.setMaximumSize(QSize(16777215, 10))
        self.pushButton_6.setStyleSheet(u"background-color: rgb(94, 92, 100);")

        self.verticalLayout_19.addWidget(self.pushButton_6)

        self.mpSendCancelBtn2 = QPushButton(self.frame_53)
        self.mpSendCancelBtn2.setObjectName(u"mpSendCancelBtn2")
        sizePolicy6.setHeightForWidth(self.mpSendCancelBtn2.sizePolicy().hasHeightForWidth())
        self.mpSendCancelBtn2.setSizePolicy(sizePolicy6)
        self.mpSendCancelBtn2.setMinimumSize(QSize(0, 80))
        self.mpSendCancelBtn2.setFont(font6)
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
        self.label_19.setFont(font23)

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
        self.mpStationTargetLb_2.setFont(font24)

        self.verticalLayout_21.addWidget(self.mpStationTargetLb_2, 0, Qt.AlignmentFlag.AlignHCenter)

        self.label_21 = QLabel(self.frame_57)
        self.label_21.setObjectName(u"label_21")
        sizePolicy4.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy4)
        self.label_21.setMaximumSize(QSize(16777215, 150))
        self.label_21.setFont(font24)
        self.label_21.setStyleSheet(u"color: rgb(38, 162, 105);\n"
"")

        self.verticalLayout_21.addWidget(self.label_21, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout_31.addWidget(self.frame_57)


        self.verticalLayout_20.addWidget(self.frame_56)


        self.horizontalLayout_32.addWidget(self.frame_54)

        self.myStackedWidget.addWidget(self.Move2Target_page)
        self.dock_page = QWidget()
        self.dock_page.setObjectName(u"dock_page")
        self.gridLayout_6 = QGridLayout(self.dock_page)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.frame_58 = QFrame(self.dock_page)
        self.frame_58.setObjectName(u"frame_58")
        self.verticalLayout_22 = QVBoxLayout(self.frame_58)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.frame_59 = QFrame(self.frame_58)
        self.frame_59.setObjectName(u"frame_59")
        self.frame_59.setMaximumSize(QSize(16777215, 100))
        self.frame_59.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(98, 160, 234);")
        self.frame_59.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_34 = QHBoxLayout(self.frame_59)
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.horizontalLayout_34.setContentsMargins(-1, 0, -1, 0)
        self.label_22 = QLabel(self.frame_59)
        self.label_22.setObjectName(u"label_22")
        sizePolicy1.setHeightForWidth(self.label_22.sizePolicy().hasHeightForWidth())
        self.label_22.setSizePolicy(sizePolicy1)
        self.label_22.setMaximumSize(QSize(16777215, 150))
        self.label_22.setFont(font23)

        self.horizontalLayout_34.addWidget(self.label_22, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_22.addWidget(self.frame_59)

        self.frame_60 = QFrame(self.frame_58)
        self.frame_60.setObjectName(u"frame_60")
        sizePolicy2.setHeightForWidth(self.frame_60.sizePolicy().hasHeightForWidth())
        self.frame_60.setSizePolicy(sizePolicy2)
        self.frame_60.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_21 = QHBoxLayout(self.frame_60)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.frame_61 = QFrame(self.frame_60)
        self.frame_61.setObjectName(u"frame_61")
        sizePolicy1.setHeightForWidth(self.frame_61.sizePolicy().hasHeightForWidth())
        self.frame_61.setSizePolicy(sizePolicy1)
        self.frame_61.setStyleSheet(u"\n"
"background-color: rgb(153, 193, 241);\n"
"")
        self.frame_61.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_23 = QVBoxLayout(self.frame_61)
        self.verticalLayout_23.setSpacing(9)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(-1, -1, -1, 60)
        self.mpDockImageBtn = QPushButton(self.frame_61)
        self.mpDockImageBtn.setObjectName(u"mpDockImageBtn")
        self.mpDockImageBtn.setMinimumSize(QSize(150, 150))
        self.mpDockImageBtn.setMaximumSize(QSize(500, 650))
        self.mpDockImageBtn.setStyleSheet(u"border:none;")
        icon7 = QIcon()
        icon7.addFile(u":/dock/Icons_dock/Dock.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.mpDockImageBtn.setIcon(icon7)
        self.mpDockImageBtn.setIconSize(QSize(500, 650))

        self.verticalLayout_23.addWidget(self.mpDockImageBtn, 0, Qt.AlignmentFlag.AlignHCenter)

        self.mpDockStatuslb = QLabel(self.frame_61)
        self.mpDockStatuslb.setObjectName(u"mpDockStatuslb")
        sizePolicy4.setHeightForWidth(self.mpDockStatuslb.sizePolicy().hasHeightForWidth())
        self.mpDockStatuslb.setSizePolicy(sizePolicy4)
        self.mpDockStatuslb.setMaximumSize(QSize(16777215, 130))
        font25 = QFont()
        font25.setFamilies([u"TH Sarabun New"])
        font25.setPointSize(120)
        font25.setBold(True)
        font25.setItalic(True)
        font25.setUnderline(False)
        self.mpDockStatuslb.setFont(font25)
        self.mpDockStatuslb.setStyleSheet(u"color: rgb(0, 0, 0);")

        self.verticalLayout_23.addWidget(self.mpDockStatuslb, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout_21.addWidget(self.frame_61)

        self.frame_62 = QFrame(self.frame_60)
        self.frame_62.setObjectName(u"frame_62")
        sizePolicy1.setHeightForWidth(self.frame_62.sizePolicy().hasHeightForWidth())
        self.frame_62.setSizePolicy(sizePolicy1)
        self.frame_62.setStyleSheet(u"\n"
"background-color: rgb(246, 245, 244);\n"
"")
        self.frame_62.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_24 = QVBoxLayout(self.frame_62)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.frame_32 = QFrame(self.frame_62)
        self.frame_32.setObjectName(u"frame_32")
        self.frame_32.setStyleSheet(u"background-color: rgb(153, 193, 241);")
        self.frame_32.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_32.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_22 = QHBoxLayout(self.frame_32)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.mpChargeStatus = QLabel(self.frame_32)
        self.mpChargeStatus.setObjectName(u"mpChargeStatus")
        sizePolicy4.setHeightForWidth(self.mpChargeStatus.sizePolicy().hasHeightForWidth())
        self.mpChargeStatus.setSizePolicy(sizePolicy4)
        self.mpChargeStatus.setMaximumSize(QSize(16777215, 100))
        font26 = QFont()
        font26.setFamilies([u"TH Sarabun New"])
        font26.setPointSize(50)
        font26.setBold(False)
        font26.setItalic(True)
        self.mpChargeStatus.setFont(font26)
        self.mpChargeStatus.setStyleSheet(u"")
        self.mpChargeStatus.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_22.addWidget(self.mpChargeStatus)

        self.mpChargeStatuslb = QLabel(self.frame_32)
        self.mpChargeStatuslb.setObjectName(u"mpChargeStatuslb")
        sizePolicy4.setHeightForWidth(self.mpChargeStatuslb.sizePolicy().hasHeightForWidth())
        self.mpChargeStatuslb.setSizePolicy(sizePolicy4)
        self.mpChargeStatuslb.setMaximumSize(QSize(16777215, 100))
        font27 = QFont()
        font27.setFamilies([u"TH Sarabun New"])
        font27.setPointSize(50)
        font27.setBold(True)
        font27.setItalic(True)
        self.mpChargeStatuslb.setFont(font27)
        self.mpChargeStatuslb.setStyleSheet(u"color: rgb(38, 162, 105);\n"
"")
        self.mpChargeStatuslb.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_22.addWidget(self.mpChargeStatuslb)


        self.verticalLayout_24.addWidget(self.frame_32, 0, Qt.AlignmentFlag.AlignTop)

        self.frame_35 = QFrame(self.frame_62)
        self.frame_35.setObjectName(u"frame_35")
        sizePolicy2.setHeightForWidth(self.frame_35.sizePolicy().hasHeightForWidth())
        self.frame_35.setSizePolicy(sizePolicy2)
        self.frame_35.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_35.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_17 = QVBoxLayout(self.frame_35)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.mpStationTargetLb_5 = QLabel(self.frame_35)
        self.mpStationTargetLb_5.setObjectName(u"mpStationTargetLb_5")
        sizePolicy4.setHeightForWidth(self.mpStationTargetLb_5.sizePolicy().hasHeightForWidth())
        self.mpStationTargetLb_5.setSizePolicy(sizePolicy4)
        self.mpStationTargetLb_5.setMaximumSize(QSize(16777215, 100))
        self.mpStationTargetLb_5.setFont(font26)
        self.mpStationTargetLb_5.setStyleSheet(u"background-color: rgb(153, 193, 241);")
        self.mpStationTargetLb_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_17.addWidget(self.mpStationTargetLb_5, 0, Qt.AlignmentFlag.AlignVCenter)

        self.mpCurrentBattBtn = QPushButton(self.frame_35)
        self.mpCurrentBattBtn.setObjectName(u"mpCurrentBattBtn")
        sizePolicy3.setHeightForWidth(self.mpCurrentBattBtn.sizePolicy().hasHeightForWidth())
        self.mpCurrentBattBtn.setSizePolicy(sizePolicy3)
        self.mpCurrentBattBtn.setMinimumSize(QSize(0, 200))
        font28 = QFont()
        font28.setFamilies([u"TH Sarabun New"])
        font28.setPointSize(150)
        self.mpCurrentBattBtn.setFont(font28)
        self.mpCurrentBattBtn.setStyleSheet(u"background-color: rgb(153, 193, 241);\n"
"color: rgb(53, 132, 228);")
        icon8 = QIcon()
        icon8.addFile(u":/black/Icons/font_awesome/solid/battery-three-quarters.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.mpCurrentBattBtn.setIcon(icon8)
        self.mpCurrentBattBtn.setIconSize(QSize(400, 400))
        self.mpCurrentBattBtn.setAutoRepeatInterval(100)

        self.verticalLayout_17.addWidget(self.mpCurrentBattBtn)


        self.verticalLayout_24.addWidget(self.frame_35)


        self.horizontalLayout_21.addWidget(self.frame_62)


        self.verticalLayout_22.addWidget(self.frame_60)


        self.gridLayout_6.addWidget(self.frame_58, 0, 0, 1, 1)

        self.myStackedWidget.addWidget(self.dock_page)

        self.gridLayout_3.addWidget(self.myStackedWidget, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.frame_2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.mpTargetCmb.currentTextChanged.connect(self.mpTargetLb.setText)
        self.mpCloseApp.clicked.connect(MainWindow.close)

        self.myStackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("")
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"PAUSE", None))
        self.mpStatuslb.setText(QCoreApplication.translate("MainWindow", u"Status: STANDBY", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"98%", None))
        self.mpCloseApp.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.mpTargetBtn.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u0e15\u0e33\u0e41\u0e2b\u0e19\u0e48\u0e07\u0e40\u0e1b\u0e49\u0e32\u0e2b\u0e21\u0e32\u0e22", None))
        self.mpSendBtn.setText("")
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u0e2a\u0e48\u0e07\u0e02\u0e2d\u0e07", None))
        self.mpReceiveBtn.setText("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u0e23\u0e31\u0e1a\u0e02\u0e2d\u0e07", None))
        self.mpBacktoHomePageBtn.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u0e42\u0e1b\u0e23\u0e14\u0e40\u0e25\u0e37\u0e2d\u0e01\u0e15\u0e33\u0e41\u0e2b\u0e19\u0e48\u0e07\u0e1b\u0e25\u0e32\u0e22\u0e17\u0e32\u0e07\u0e02\u0e2d\u0e07\u0e2b\u0e38\u0e48\u0e19\u0e22\u0e19\u0e15\u0e4c", None))
        self.groupBox.setTitle("")
        self.pushButton_2.setText("")
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
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Action :", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Delivery", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Target :", None))
        self.mpTargetTextLb.setText("")
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Box No. :", None))
        self.mpBoxTextLb.setText("")
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"\u0e01\u0e23\u0e38\u0e13\u0e32\u0e40\u0e25\u0e37\u0e2d\u0e01\u0e0a\u0e48\u0e2d\u0e07\u0e40\u0e01\u0e47\u0e1a\u0e02\u0e2d\u0e07", None))
        self.mpBoxNumberCb.setCurrentText("")
        self.mpReceiveOkBtn.setText(QCoreApplication.translate("MainWindow", u"\u0e23\u0e31\u0e1a\u0e02\u0e2d\u0e07", None))
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
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"\u0e2a\u0e16\u0e32\u0e19\u0e35\u0e0a\u0e32\u0e23\u0e4c\u0e08\u0e41\u0e1a\u0e15\u0e40\u0e15\u0e2d\u0e23\u0e35\u0e48", None))
        self.mpDockImageBtn.setText("")
        self.mpDockStatuslb.setText(QCoreApplication.translate("MainWindow", u"Docking", None))
        self.mpChargeStatus.setText(QCoreApplication.translate("MainWindow", u"\u0e2a\u0e16\u0e32\u0e19\u0e30\u0e01\u0e32\u0e23\u0e0a\u0e32\u0e23\u0e4c\u0e08 :  ", None))
        self.mpChargeStatuslb.setText(QCoreApplication.translate("MainWindow", u"Charging..", None))
        self.mpStationTargetLb_5.setText(QCoreApplication.translate("MainWindow", u"\u0e23\u0e30\u0e14\u0e31\u0e1a\u0e41\u0e1a\u0e15\u0e40\u0e15\u0e2d\u0e23\u0e35\u0e48\u0e1b\u0e31\u0e08\u0e08\u0e38\u0e1a\u0e31\u0e19(%)", None))
        self.mpCurrentBattBtn.setText(QCoreApplication.translate("MainWindow", u" 98%", None))
    # retranslateUi

