import argparse
import os


def main(args):

  # get paths to the two images
  if args.one is None:
    path_one = os.path.join(os.getcwd(), "images", "black_square.png")
  else:
    path_one = args.one

  if args.two is None:
    path_two = os.path.join(os.getcwd(), "images", "white_ellipse.png")
  else:
    path_two = args.two


if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument("-one", type=str, default=None, help="Path to the first image.")
  parser.add_argument("-two", type=str, default=None, help="Path to the second image.")

  params = parser.parse_args()

  main(params)
