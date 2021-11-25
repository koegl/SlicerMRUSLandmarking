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


def main(args):

    print(read_data(args.file_path))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-fp", "--file_path", type=str, default=None)

    params = parser.parse_args()

    main(params)
