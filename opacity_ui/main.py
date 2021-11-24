import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QSlider
from opacity_ui import Ui_MainWindow


class OpacityWindow(QMainWindow):
    def __init__(self):
        super(OpacityWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # slider
        self.ui.verticalSlider.setMinimum(0)
        self.ui.verticalSlider.setMaximum(1000)
        self.ui.verticalSlider.setTickInterval(100)
        self.ui.verticalSlider.setTickPosition(QSlider.TicksLeft)

        # whenever the slider changes, execute the opacity change
        self.ui.verticalSlider.valueChanged.connect(self.opacity_change)

    def opacity_change(self):
        x = self.ui.verticalSlider.value()
        print("{}^2 = {}".format(x, x**2))
        x = 0


if __name__ == "__main__":
    app = QApplication([])

    window = OpacityWindow()
    window.show()

    sys.exit(app.exec())
