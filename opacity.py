import argparse
import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np


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

    # load images
    image_one = Image.open(path_one).convert('L')
    image_one = np.asarray(image_one)

    image_two = Image.open(path_two).convert('L')
    image_two = np.asarray(image_two)

    print(image_one.shape)
    print(image_two.shape)

    plt.imshow(image_one, cmap='gray')
    plt.show()
    plt.imshow(image_two, cmap='gray')
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-one", type=str, default=None, help="Path to the first image.")
    parser.add_argument("-two", type=str, default=None, help="Path to the second image.")

    params = parser.parse_args()

    main(params)
