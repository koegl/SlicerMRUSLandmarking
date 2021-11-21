import numpy as np
import matplotlib.pyplot as plt


# function to change opacity between two images
def opacity_change2(image1, image2, opacity):
    """
    Function to blend two images into one
    :param image1: Bottom image
    :param image2: Top image
    :param opacity: Opacity of top image
    :return: the blended image
    """

    # assert correct values
    assert image1.shape == image2.shape, "Images have different shapes"
    assert 0.0 <= opacity <= 1.0, "Opacity out of range"

    blend = (1 - opacity) * image1 + opacity * image2

    return blend


# function to change opacity between three images
def opacity_change3(image1, image2, image3, opacity2, opacity3, threshold=0):
    """
    Function to blend two images into one
    :param image1: Bottom image
    :param image2: Middle image
    :param image3: Top image
    :param opacity2: Opacity of middle image
    :param opacity3: Opacity of top image
    :param threshold: values below this value are not displayed
    :return: the blended image
    """

    # assert correct values
    assert image1.shape == image2.shape == image3.shape, "Images have different shapes"
    assert 0.0 <= opacity2 <= 1.0, "Opacity2 (of middle image) out of range"
    assert 0.0 <= opacity3 <= 1.0, "Opacity3 (of top image) out of range"

    # adjust for 0 pixels
    image2_threshold = np.where(image2 != threshold)
    image3_threshold = np.where(image3 != threshold)

    blend_12 = np.copy(image1)

    blend_12[image2_threshold] = (1 - opacity2) * image1[image2_threshold] + opacity2 * image2[image2_threshold]

    blend_123 = np.copy(blend_12)
    blend_123[image3_threshold] = (1 - opacity3) * blend_12[image3_threshold] + opacity3 * image3[image3_threshold]

    return blend_123
