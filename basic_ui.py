import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QLineEdit, QVBoxLayout, QLabel, QWidget
from PySide6.QtGui import QIcon, QPixmap
from ui_mainwindow import Ui_MainWindow


# create a personalized class for our widget to setup this generated design from uimainwindow
# https://doc.qt.io/qtforpython/tutorials/basictutorial/uifiles.html
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # connect button to a function
        self.ui.pushButton.clicked.connect(self.hello)

        # connect ok to a function
        self.ui.buttonBox.accepted.connect(self.ok)
        self.ui.buttonBox.rejected.connect(self.rej)

        self.label = QLabel(self)
        self.pixmap = QPixmap("f3.jpeg")
        self.label.setPixmap(self.pixmap)

    def hello(self):
        print(self.ui.lineEdit.text())

    def ok(self):
        print("ok")

    def rej(self):
        print("cancel")

    def appl(self):
        print("apply")


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
