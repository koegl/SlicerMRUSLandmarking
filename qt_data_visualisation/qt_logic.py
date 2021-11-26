from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QHeaderView, QSizePolicy, QTableView, QWidget
from PySide6.QtGui import QAction, QKeySequence, QColor, QPainter
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QDateTime
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis


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

        # QTableView headers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()

        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)

        self.horizontal_header.setStretchLastSection(True)

        # creating a QChart
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.add_series("Magnitude (Column 1)", [0, 1])

        # creating QChartView
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # QWidget layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # right layout
        size.setVerticalStretch(4)
        self.chart_view.setSizePolicy(size)
        self.main_layout.addWidget(self.chart_view)

        # set the layout to the QWidget
        self.setLayout(self.main_layout)

    def add_series(self, name, columns):
        # create QLineSeries
        self.series = QLineSeries()
        self.series.setName(name)

        # filling QLineSeries
        for i in range(self.model.rowCount()):
            # getting the data
            t = self.model.index(i, 0).data()
            date_fmt = "yyyy-MM-dd HH:mm:ss.zzz"

            x = QDateTime().fromString(t, date_fmt).toSecsSinceEpoch()
            y = float(self.model.index(i, 1).data())

            if x > 0 and y > 0:
                self.series.append(x, y)

        self.chart.addSeries(self.series)

        # Setting X-axis
        self.axis_x = QDateTimeAxis()
        self.axis_x.setTickCount(10)
        self.axis_x.setFormat("dd.MM (h:mm)")
        self.axis_x.setTitleText("Date")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)

        # Setting Y-axis
        self.axis_y = QValueAxis()
        self.axis_y.setTickCount(10)
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setTitleText("Magnitude")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

        # Getting the color from the QChart to use it on the QTableView
        color_name = self.series.pen().color().name()
        self.model.color = f"{color_name}"


