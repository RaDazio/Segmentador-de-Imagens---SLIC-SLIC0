from PySide2.QtWidgets import QVBoxLayout, QWidget, QColorDialog, QPushButton, QRadioButton,QHBoxLayout, QLineEdit, QLabel, QCheckBox
from PySide2.QtCore import Slot, SIGNAL
from PySide2.QtGui import QPixmap, QColor, QIcon


class SideBar(QWidget):
    def __init__(self):
        QWidget .__init__(self)
        self.setFixedWidth(240)

        self.mainlayout = QVBoxLayout(self)
        self.prinlayout = QVBoxLayout(self)
        self.seclayout = QVBoxLayout(self)
        self.headerlayout = QVBoxLayout(self)

        self.classCheck = QCheckBox("Segmentar diversas classes")
        self.classCheck.clicked.connect(lambda: self.enableClasses(self.classCheck.isChecked()))
        self.classCheck.setChecked(False)

        btnAdd = QPushButton("+")
        btnAdd.clicked.connect(self.addColor)

        self.colorList = list()
        self.currColor = 0

        self.headerlayout.addWidget(self.classCheck)
        self.prinlayout.addWidget(QLabel("Classes:"))
        self.seclayout.addWidget(btnAdd)
        self.seclayout.addStretch(1)

        self.__wid1 = QWidget()
        self.__wid1.setLayout(self.prinlayout)

        self.__wid2 = QWidget()
        self.__wid2.setLayout(self.seclayout)
        self.enableClasses(False)

        self.mainlayout.addLayout(self.headerlayout)
        self.mainlayout.addWidget(self.__wid1)
        self.mainlayout.addWidget(self.__wid2)

        self.setLayout(self.mainlayout)

    @Slot()
    def addColor(self):
        colorWidget = ColorWidget("Class Name")
        self.prinlayout.addWidget(colorWidget)
        self.colorList.append(colorWidget)
        colorWidget.QRadioButton.toggled.connect(lambda: self.checkColor(colorWidget))
        colors = list()
        for color in self.colorList:
            colors.append(color.QColor.toTuple()[:3])

        if len(self.colorList) >= 14:
            self.__wid2.setEnabled(False)
        self.emit(SIGNAL("getAllColors(list)"), colors)

    @Slot()
    def checkColor(self, colorWidget):
        new_idx = 0
        for idx, color in enumerate(self.colorList):
            if colorWidget == color:
                new_idx = idx
                break
        if new_idx != self.currColor:
            if len(self.colorList) > 1:
                self.colorList[self.currColor].QRadioButton.setChecked(False)
            self.currColor = new_idx

        self.emit(SIGNAL("setHighlightColor(QColor)"), colorWidget.QColor)

    @Slot()
    def getAllColors(self):
        c = list()
        for color in self.colorList:
            c.append(color)
        return c

    @Slot()
    def enableClasses(self, cond):
        self.__wid1.setEnabled(cond)
        if len(self.colorList) < 14:
            self.__wid2.setEnabled(cond)


class ColorWidget(QWidget):
    def __init__(self, colorName):
        QWidget.__init__(self)

        comboLayout = QHBoxLayout(self)
        self.QRadioButton = QRadioButton(self)
        self.Qlabel = QLineEdit(colorName)
        self.QColor = QColor(255, 255, 255)
        self.ColorWidget = QPushButton()
        self.ColorWidget.resize(30, 30)
        pixMap = QPixmap(30, 30)
        pixMap.fill(self.QColor)
        self.ColorWidget.setIcon(QIcon(pixMap))

        comboLayout.addWidget(self.QRadioButton)
        comboLayout.addWidget(self.Qlabel)
        comboLayout.addWidget(self.ColorWidget)

        self.ColorWidget.clicked.connect(self.changeColor)

    @Slot()
    def changeColor(self):
        self.QColor = QColorDialog().getColor()
        pixmap = QPixmap(30, 30)
        pixmap.fill(self.QColor)
        self.ColorWidget.setIcon(QIcon(pixmap))




