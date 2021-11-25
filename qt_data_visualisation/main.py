import argparse
import utils


def main(args):

    print(utils.read_data(args.file_path))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-fp", "--file_path", type=str, default=None)

    params = parser.parse_args()

    main(params)
