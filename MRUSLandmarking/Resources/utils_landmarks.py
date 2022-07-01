import slicer


def turn_off_placement_mode():
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToViewTransformMode()
    interactionNode.SetPlaceModePersistence(0)


def print_landmark_inspection_results(mrus_landmarking_widget):
    check_if_landmark_list_is_selected(mrus_landmarking_widget)

    for i in range(mrus_landmarking_widget.current_landmarks_list.GetNumberOfControlPoints()):

        status = mrus_landmarking_widget.current_landmarks_list.GetNthControlPointDescription(i)

        if status == '':
            status = "Not checked"

        if status[0] == ';':
            status = status[2:]

        print(f"{mrus_landmarking_widget.current_landmarks_list.GetNthControlPointLabel(i).ljust(12)}: {status}")

    turn_off_placement_mode()


def check_if_landmark_list_is_selected(mrus_landmarking_widget):
    mrus_landmarking_widget.current_landmarks_list = mrus_landmarking_widget.ui.SimpleMarkupsWidget.currentNode()

    if mrus_landmarking_widget.current_landmarks_list is None:
        raise ValueError("Please select a landmark list.")


def sort_landmarks(mrus_landmarking_widget):
    check_if_landmark_list_is_selected(mrus_landmarking_widget)

    # create a list to sort
    sort_list = []

    for i in range(mrus_landmarking_widget.current_landmarks_list.GetNumberOfControlPoints()):
        sort_list.append([mrus_landmarking_widget.current_landmarks_list.GetNthControlPointLabel(i),
                          mrus_landmarking_widget.current_landmarks_list.GetNthControlPointID(i), -1])

    sort_list = sorted(sort_list, key=lambda x: x[0][0].split(' ')[0][1:])

    # create sublists for each landmark
    sublists = {}
    for packet in sort_list:
        prefix = packet[0].split(' ')[0]
        if prefix in sublists:
            sublists[prefix].append(packet)
        else:
            sublists[prefix] = [packet]

    sublists = list(sublists.items())

    # move intra to the last position of each sublist and sort each sublist
    for i in range(len(sublists)):
        sub = sublists[i][1]
        new_list = sorted(sub, key=lambda x: x[0].split(' ')[1])

        if "intra" in new_list[0][0].lower():
            temp = new_list.pop(0)
            new_list.append(temp)

        sublists[i] = (sublists[i][0], new_list)

    # create final sorted list
    final_list = []
    for _, packet in sublists:
        for sub in packet:
            final_list.append(sub)

    # create new markups list
    sorted_markups = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode",
                                                        mrus_landmarking_widget.current_landmarks_list.GetName() + "_sorted")

    for idx, landmark in enumerate(final_list):
        index = mrus_landmarking_widget.current_landmarks_list.GetNthControlPointIndexByID(landmark[1])

        sorted_markups.AddControlPoint(mrus_landmarking_widget.current_landmarks_list.GetNthControlPointPosition(index),
                                       mrus_landmarking_widget.current_landmarks_list.GetNthControlPointLabel(index))

        sorted_markups.SetNthControlPointDescription(idx,
                                                     mrus_landmarking_widget.current_landmarks_list.GetNthControlPointDescription(index))