from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QHeaderView, QSizePolicy, QTableView, QWidget
from PySide6.QtGui import QAction, QKeySequence, QColor
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex

from utils import read_data


class DataWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Earthquakes information")
        self.setCentralWidget(widget)

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        # status bar
        self.status = self.statusBar()
        self.status.showMessage("Data loaded and plotted")

        # window dimensions
        geometry = self.screen().availableGeometry()
        self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)


class CustomTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        QAbstractTableModel.__init__(self)
        self.load_data(data)

    def load_data(self, data):
        self.input_dates = data[0].values
        self.input_magnitudes = data[1].values

        self.column_count = 2
        self.row_count = len(self.input_magnitudes)

    # virtual function from parent class that has to be implemented
    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex):
        return self.column_count

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("Date", "Magnitude")[section]
        else:
            return f"{section}"

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            if column == 0:
                date = self.input_dates[row].toPython()
                return str(date)[:-3]
            elif column == 1:
                magnitude = self.input_magnitudes[row]
                return f"{magnitude:.2f}"
        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight

        return None


class Widget(QWidget):
    def __init__(self, data):
        QWidget.__init__(self)

        # getting the model
        self.model = CustomTableModel(data)

        # creating a QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # QTableView heaers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()

        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)

        self.horizontal_header.setStretchLastSection(True)

        # QWidget layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # set the layout to the QWidget
        self.setLayout(self.main_layout)

