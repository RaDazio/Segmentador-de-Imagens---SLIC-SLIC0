import sys
from mainWindow import MyMainWindow
from PySide2.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = MyMainWindow("SuperPixels - SLIC v1.0")
    mainWindow.show()

    sys.exit(app.exec_())

