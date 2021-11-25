import argparse
import pandas as pd
import os

from PySide6.QtCore import QDateTime, QTimeZone


def read_data(file_path):
    """
    Read data from a csv file
    :param file_path: The path tot he file
    :return: loaded csv data
    """
    if file_path is None:
        path = os.path.join(os.getcwd(), "..", "data", "all_day.csv")
        data = pd.read_csv(path)
    else:
        data = pd.read_csv(file_path)

    return data


def transform_date(utc, timezone=None):
    """
    Function to transform date int Qt format
    :param utc: the time
    :param timezone: optional parameter for the timezone
    :return: the date in qt format
    """

    utc_format = "yyyy-MM-ddTHH:mm:ss.zzzZ"
    qt_date = QDateTime().fromString(utc, utc_format)

    if timezone:
        qt_date.setTimeZone(timezone)

    return qt_date
