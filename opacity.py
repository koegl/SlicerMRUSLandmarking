import argparse
import os
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import numpy as np


# interactive function to change opacity
def opacity_change(image1, image2, opacity):

    blend = np.empty(image1.shape)

    for i in range(image1.shape[0]):
        for j in range(image1.shape[1]):
            blend[i, j] = (1 - opacity) * image1[i, j] + opacity * image2[i, j]

    return blend


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

    # get opacity
    opacity = args.op

    # load images
    image_one = Image.open(path_one).convert('L')
    image_one = np.asarray(image_one)

    image_two = Image.open(path_two).convert('L')
    image_two = np.asarray(image_two)

    # blend images
    # interactive display
    # create plot
    fig, ax = plt.subplots()
    img = plt.imshow(opacity_change(image_one, image_two, opacity), cmap='gray')
    plt.subplots_adjust(left=0.25)

    # create slider
    axop = plt.axes([0.1, 0.25, 0.0225, 0.63])
    opacity_slider = Slider(
        ax=axop,
        label="Amplitude",
        valmin=0.0,
        valmax=1.0,
        valinit=opacity,
        orientation="vertical"
    )

    # The function to be called anytime a slider's value changes
    def slider_update(val):
        ax.imshow(opacity_change(image_one, image_two, opacity_slider.val), cmap='gray')
        fig.canvas.draw_idle()

    opacity_slider.on_changed(slider_update)

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
    parser.add_argument("-op", type=float, default=1.0, help="Opacity, range: [0,1]")

    params = parser.parse_args()

    main(params)
