# unpickle numpy array with landmark coordinates

import pickle

# load and unpickle file
with open("lmrks5", 'rb') as landmarks_file:
    landmarks = pickle.load(landmarks_file)

print(landmarks)

print(5)



path = "C:/Users/fryde/Documents/university/master/thesis/code/mthesis-slicerLandmarkingView/misc/lmrks5"


