from PySide6.QtWidgets import QApplication, QLabel
# For a widget application using PySide6, you must always start by importing the appropriate class from the
# PySide6.QtWidgets module


def basic_widget(display_text="Hello World!"):
    """
    :param display_text: Text that will be displayed in the widget
    Simplest widget from https://doc.qt.io/qtforpython/tutorials/basictutorial/widgets.html
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
