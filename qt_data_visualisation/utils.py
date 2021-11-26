import argparse
import pandas as pd
import os

from PySide6.QtCore import QDateTime, QTimeZone


def read_data(file_path=None):
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

    # remove wrong magnitudes
    data = data.drop(data[data.mag < 0].index)
    magnitudes = data["mag"]

    # local timezone
    timezone = QTimeZone(b"Europe/Berlin")

    # get timestamp transformed to our timezone
    times = data["time"].apply(lambda x: transform_date(x, timezone))

    return times, magnitudes


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
