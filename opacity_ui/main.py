import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from opacity_ui import Ui_MainWindow


class OpacityWindow(QMainWindow):
    def __init__(self):
        super(OpacityWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def print_slider_value(self):
        print(self.ui.verticalSlider.value())


if __name__ == "__main__":
    app = QApplication([])

    window = OpacityWindow()
    window.show()

    sys.exit(app.exec())
