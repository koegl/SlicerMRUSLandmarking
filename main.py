import os


image_path = "/Users/fryderykkogl/Data/sift/US2.nii"
extractor_path = "sift/featExtract.mac"

# Extract features from a given image
feature_save_path = image_path.replace(".nii", ".key")
command = f"{extractor_path} {image_path} {feature_save_path}"
os.system(command)
