import os


def extract_features_from_file(image_path, extractor_path):
    """
    Extracts features from a given image and saves to the same file name with a .key extension
    :param image_path: path to the image
    :param extractor_path: path to the sift extractor
    """

    feature_save_path = image_path.replace(".nii", ".key")

    command = f"{extractor_path} -2 {image_path} {feature_save_path}"

    os.system(command)


def match_features(feature_file, reference_file, matcher_path):
    """
    Matches the features from the feature_file to the reference_file
    param: feature_file: path to the feature file
    param: reference_file: path to the reference file
    param: matcher_path: path to the matcher
    """

    command = f"{matcher_path} {reference_file} {feature_file}"

    os.system(command)



