from PySide2.QtWidgets import QMainWindow, QPushButton, QFileDialog, QLayout, QHBoxLayout, QAction, QWidget
from PySide2.QtCore import Slot, Qt, QObject,SIGNAL
from ImageCanvas import Canvas
from SideBar import SideBar

class MyMainWindow(QMainWindow):
    def __init__(self, title):
        QMainWindow.__init__(self)
        self.setWindowTitle(title)

        self.canvas = Canvas()
        self.sideBar = SideBar()

        self.canvas.connect(self.sideBar, SIGNAL("getAllColors(list())"), self.canvas.getAllColors)
        self.canvas.connect(self.sideBar, SIGNAL("setHighlightColor(QColor)"), self.canvas.setHighlightColor)

        openFileAct = QAction("Abrir Foto", self)
        openFileAct.triggered.connect(self.canvas.onFileOpen)

        saveFileAct = QAction("Salvar foto", self)
        saveFileAct.triggered.connect(self.canvas.onSaveFile)

        exportBinaryAct = QAction("Salvar máscara", self)
        exportBinaryAct.triggered.connect(self.canvas.exportBinary)

        removeBackgroudAct = QAction("Remover backgroud", self)
        removeBackgroudAct.triggered.connect(self.canvas.onRemoveBackgroud)

        toolbar = self.addToolBar("")
        toolbar.addAction(openFileAct)
        toolbar.addAction(saveFileAct)
        toolbar.addAction(exportBinaryAct)
        toolbar.addSeparator()
        toolbar.addAction(removeBackgroudAct)

        toolbar.setMovable(False)

        self.mainlayout = QHBoxLayout(self)
        self.mainlayout.addWidget(self.canvas)
        self.mainlayout.addWidget(self.sideBar)


        mainWidget = QWidget()
        mainWidget.setLayout(self.mainlayout)

        self.setCentralWidget(mainWidget)


    @Slot()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


