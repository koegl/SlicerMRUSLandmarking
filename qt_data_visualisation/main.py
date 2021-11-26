import argparse
import utils
import sys

from PySide6.QtWidgets import QApplication

from qt_logic import DataWindow, Widget
from utils import read_data


def main(args):

    data = read_data()

    app = QApplication([])

    widget = Widget(data)
    data_window = DataWindow(widget)
    data_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-fp", "--file_path", type=str, default=None)

    params = parser.parse_args()

    main(params)
