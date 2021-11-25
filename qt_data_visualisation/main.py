import argparse
import pandas as pd
import os


def read_data(file_path):
    return pd.read_csv(file_path)


def main(args):

    if args.file_path is None:
        path = os.path.join(os.getcwd(), "..", "data", "all_day.csv")
        data = read_data(path)
    else:
        data = read_data(args.file_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-fp", "--file_path", type=str, default=None)

    params = parser.parse_args()

    main(params)
