import os
import pickle
import json


class LandmarkIO:
    def __init__(self, markups_list_name="F"):
        self.markups_list_name = markups_list_name

    def export_landmarks_to_numpy(self):
        """
        Export Slicer landmarks to numpy landmarks (S)
        """
        pass

    def export_landmarks_to_json(self):
        """
        Export Slicer landmarks to json
        """

        pointListNode = slicer.util.getNode.getNode(self.markups_list_name)
        outputFileName = "/Users/fryderykkogl/Desktop/test.json"

        # Get markup positions
        data = []
        for fidIndex in range(pointListNode.GetNumberOfControlPoints()):
            coords = [0, 0, 0]
            pointListNode.GetNthControlPointPosition(fidIndex, coords)
            data.append({"label": pointListNode.GetNthControlPointLabel(), "position": coords})

        import json
        with open(outputFileName, "w") as outfile:
            json.dump(data, outfile)

    def load_numpy_landmarks(self):

        file_path = "C:/Users/fryde/Documents/university/master/thesis/code/mthesis-slicerLandmarkingView/misc/ag2146_T2SPACE_US1predura"
        file_name = os.path.basename(file_path)

        # split filename so we can extract to which volumes the landmarks relate to
        file_name = file_name.split('_')

        # load picked file
        with open(file_path, 'rb') as landmarks_file:
          landmarks = pickle.load(landmarks_file)

        # create and activate new node for new (loaded) landmarks
        markup_node_id = slicer.modules.markups.logic().AddNewFiducialNode("F")  # get id
        markup_node = slicer.mrmlScene.GetNodeByID(markup_node_id)  # get id with node

        for j in range(landmarks[0].shape[0]):
          for i in range(2):
            cors = landmarks[i][j]
            markup_node.AddFiducial(cors[0], cors[1], cors[2], "{}_{}".format(file_name[i+1], j))  # +1 because 0th is AG

