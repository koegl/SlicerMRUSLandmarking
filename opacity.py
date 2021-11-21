import argparse
import os
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import numpy as np

import utils


# TODO change the code so that it can work on a concatenated image (where two images are concatenated)
# TODO after the above todo, extend the code so that it can work for 3 and more images
def main(args):
    # get paths to the two images
    if args.one is None:
        path_one = os.path.join(os.getcwd(), "images", "cat_normal.png")
    else:
        path_one = args.one

    if args.two is None:
        path_two = os.path.join(os.getcwd(), "images", "cat_white.png")
    else:
        path_two = args.two

    if args.three is None:
        path_three = os.path.join(os.getcwd(), "images", "cat_black.png")
    else:
        path_three = args.three

    # load images and convert to grayscale
    image_one = Image.open(path_one).convert('L')
    image_one = np.asarray(image_one) / 255

    image_two = Image.open(path_two).convert('L')
    image_two = np.asarray(image_two) / 255

    image_three = Image.open(path_three).convert('L')
    image_three = np.asarray(image_three) / 255

    opacity2 = 0.5
    opacity3 = 0.5

    # blend images
    # interactive display
    # create plot
    fig, ax = plt.subplots()
    plt.imshow(utils.opacity_change3(image_one, image_two, image_three, opacity2, opacity3), cmap='gray', vmin=0.0, vmax=1.0)
    plt.subplots_adjust(left=0.35)

    # create sliders
    ax_opacity2 = plt.axes([0.1, 0.25, 0.0225, 0.63])
    opacity2_slider = Slider(
        ax=ax_opacity2,
        label="Opacity2",
        valmin=0.0,
        valmax=1.0,
        valinit=opacity2,
        orientation="vertical"
    )

    ax_opacity3 = plt.axes([0.2, 0.25, 0.0225, 0.63])
    opacity3_slider = Slider(
        ax=ax_opacity3,
        label="Opacity3",
        valmin=0.0,
        valmax=1.0,
        valinit=opacity3,
        orientation="vertical"
    )

    # The function to be called anytime a slider's value changes
    def slider_update(val):
        ax.imshow(utils.opacity_change3(image_one, image_two, image_three, opacity2_slider.val, opacity3_slider.val), cmap='gray', vmin=0.0, vmax=1.0)
        fig.canvas.draw_idle()

    opacity2_slider.on_changed(slider_update)
    opacity3_slider.on_changed(slider_update)

    plt.show()

    # plt.imshow(image_one, cmap='gray')
    # plt.show()
    # plt.imshow(image_two, cmap='gray')
    # plt.show()
    # plt.imshow(image_blended, cmap='gray')
    # plt.show()

    print(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-one", type=str, default=None, help="Path to the first image.")
    parser.add_argument("-two", type=str, default=None, help="Path to the second image.")
    parser.add_argument("-three", type=str, default=None, help="Path to the third image.")

    params = parser.parse_args()

    main(params)
