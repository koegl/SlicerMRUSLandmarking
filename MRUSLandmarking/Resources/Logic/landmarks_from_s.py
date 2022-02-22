import os
import pickle

def load_numpy_landmarks(self):

    file_path = "C:/Users/fryde/Documents/university/master/thesis/code/mthesis-slicerLandmarkingView/misc/ag2146_T2SPACE_US1predura"
    file_name = os.path.basename(file_path)

    # split filename so we can extract to which volumes the landmarks relate to
    file_name = file_name.split('_')

    # load picked file
    # todo loading file shouldn't be hardcoded - let the user choose in the GUI which file to load
    # todo the pickled file needs to specify somewhere (in the filename) which dataset and especially which volumes
    with open(file_path, 'rb') as landmarks_file:
      landmarks = pickle.load(landmarks_file)

    # create and activate new node for new (loaded) landmarks
    markup_node_id = slicer.modules.markups.logic().AddNewFiducialNode("F")  # get id
    markup_node = slicer.mrmlScene.GetNodeByID(markup_node_id)  # get id with node

    for j in range(landmarks[0].shape[0]):
      for i in range(2):
        cors = landmarks[i][j]
        markup_node.AddFiducial(cors[0], cors[1], cors[2], "{}_{}".format(file_name[i+1], j))  # +1 because 0th is AG