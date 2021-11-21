import argparse


def main(args):
  pass


if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument("-one", type=str, default=None, help="Path to the first image.")
  parser.add_argument("-two", type=str, default=None, help="Path to the second image.")

  params = parser.parse_args()

  main(params)
