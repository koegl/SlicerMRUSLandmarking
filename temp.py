import os
import glob
import multiprocessing
from joblib import Parallel, delayed

from utils import extract_features_from_file, match_features


num_cores = multiprocessing.cpu_count()

data_dir = "/Users/fryderykkogl/Data/sift"
extractor_path = "sift/featExtract.mac"
matcher_path = "sift/featMatchMultiple.mac"

# get all nifti files in the data directory
nifti_files = list(glob.glob(os.path.join(data_dir, "*.nii")))
nifti_files.sort()

# 1. extract all features

return_list = Parallel(n_jobs=num_cores)(delayed(extract_features_from_file)(nifti_files[i], extractor_path)
                                         for i in range(len(nifti_files)))


# 2. match all features with the ones from the last volume
key_files = list(glob.glob(os.path.join(data_dir, "*.key")))
key_files.sort()
reference_key_file = key_files[-1]

# in the command, the first file is the reference file
# featMatchMultiple.exe OAS1_0001.key OAS1_0002.key OAS1_0003.key

return_list = Parallel(n_jobs=num_cores)(delayed(match_features)(key_files[i], reference_key_file, matcher_path)
                                         for i in range(len(key_files) - 1))
