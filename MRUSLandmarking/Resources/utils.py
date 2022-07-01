
def print_results(mrus_landmarking_widget):
    mrus_landmarking_widget.checkIfLandmarksAreSelected()

    for i in range(mrus_landmarking_widget.current_landmarks_list.GetNumberOfControlPoints()):

        status = mrus_landmarking_widget.current_landmarks_list.GetNthControlPointDescription(i)

        if status == '':
            status = "Not checked"

        if status[0] == ';':
            status = status[2:]

        print(f"{mrus_landmarking_widget.current_landmarks_list.GetNthControlPointLabel(i).ljust(12)}: {status}")

    turn_off_placement_mode()


def turn_off_placement_mode():
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToViewTransformMode()
    interactionNode.SetPlaceModePersistence(0)

