import sys
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QDialog, QLineEdit, QVBoxLayout, QTableWidget,\
    QTableWidgetItem
from PySide6.QtCore import Slot
from PySide6.QtGui import QColor
# For a widget application using PySide6, you must always start by importing the appropriate class from the
# PySide6.QtWidgets module


def basic_widget(display_text="Hello World!"):
    """
    Simplest widget from https://doc.qt.io/qtforpython/tutorials/basictutorial/widgets.html
    :param display_text: Text that will be displayed in the widget.
    """

    # After the imports, you create a QApplication instance
    app = QApplication([])  # Qt can receive command line arguments, so you may pass any argument to the QApplication
    # object

    # Now we create a QLabel object -  widget that can present text (simple or rich, like html), and images
    label = QLabel("<font color=red size=40>{}</font>".format(display_text))

    # After creating the label, we call show() on it:
    label.show()

    # Finally, we call app.exec() to enter the Qt main loop and start to execute the Qt code. In reality, it is only
    # here where the label is shown
    app.exec()


# The @Slot() is a decorator that identifies a function as a slot. It is not important to understand why for now,
# but use it always to avoid unexpected behavior.
@Slot()
def say_hello():
    """
    function that logs the message to the console:
    https://doc.qt.io/qtforpython/tutorials/basictutorial/clickablebutton.html
    """
    print("Button clicked")


def simple_button():
    """
    Simple button from https://doc.qt.io/qtforpython/tutorials/basictutorial/clickablebutton.html
    """
    # create Qt Application
    app = QApplication([])

    # Create a clickable button with a text on it
    button = QPushButton("Click me")

    # before showing the button we must connect it to a function (say_hello() in our case)
    # the QPushButton has a predefined signal called 'clicked,' which is triggered every time the button is clicked
    # we will connect this signal to the function
    button.clicked.connect(say_hello)

    # show the button
    button.show()

    # run the main Qt loop
    app.exec()


# you can create any class that subclasses PySide6 widgets
class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("My Form")

        # create widgets
        self.edit = QLineEdit("Write my name here")
        self.button = QPushButton("Show Greetings")

        # create a layout - vertical
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)

        # set dialog layout
        self.setLayout(layout)

        # connect button
        self.button.clicked.connect(self.greetings)

    def greetings(self):
        print("Hello {}".format(self.edit.text()))


def dialog_app():
    """
    Simple dialog from https://doc.qt.io/qtforpython/tutorials/basictutorial/dialog.html
    """
    app = QApplication([])

    # create and show the form
    form = Form()
    form.show()

    app.exec()


def table_widget():
    """
    Simple table widget from https://doc.qt.io/qtforpython/tutorials/basictutorial/tablewidget.html
    """
    colors = [("Red", "#FF0000"),
              ("Green", "#00FF00"),
              ("Blue", "#0000FF"),
              ("Black", "#000000"),
              ("White", "#FFFFFF"),
              ("Electric Green", "#41CD52"),
              ("Dark Blue", "#222840"),
              ("Yellow", "#F9E56d")]

    # translate hex into rgb
    def get_rgb_from_hex(code_replace):
        code_hex = code_replace.replace("#", "")
        rgb = tuple(int(code_hex[i:i + 2], 16) for i in (0, 2, 4))
        return QColor.fromRgb(rgb[0], rgb[1], rgb[2])

    app = QApplication()

    table = QTableWidget()
    table.setRowCount(len(colors))
    table.setColumnCount(len(colors[0]) + 1)  # '+1' to display a column with the color
    table.setHorizontalHeaderLabels(["Name", "Hex Code", "Color"])

    # Iterate the data structure, create the QTableWidgetItems instances,
    # and add them into the table using a x, y coordinate

    for i, (name, code) in enumerate(colors):
        item_name = QTableWidgetItem(name)
        item_code = QTableWidgetItem(code)
        item_color = QTableWidgetItem()
        item_color.setBackground(get_rgb_from_hex(code))

        table.setItem(i, 0, item_name)
        table.setItem(i, 1, item_code)
        table.setItem(i, 2, item_color)

    table.show()

    sys.exit(app.exec())
