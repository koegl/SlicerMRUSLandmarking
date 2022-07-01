import slicer


def turn_off_placement_mode():
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToViewTransformMode()
    interactionNode.SetPlaceModePersistence(0)


def print_landmark_inspection_results(widget):
    check_if_landmark_list_is_selected(widget)

    for i in range(widget.current_landmarks_list.GetNumberOfControlPoints()):

        status = widget.current_landmarks_list.GetNthControlPointDescription(i)

        if status == '':
            status = "Not checked"

        if status[0] == ';':
            status = status[2:]

        print(f"{widget.current_landmarks_list.GetNthControlPointLabel(i).ljust(12)}: {status}")

    turn_off_placement_mode()


def check_if_landmark_list_is_selected(widget):
    widget.current_landmarks_list = widget.ui.SimpleMarkupsWidget.currentNode()

    if widget.current_landmarks_list is None:
        raise ValueError("Please select a landmark list.")


def sort_landmarks(widget):
    check_if_landmark_list_is_selected(widget)

    # create a list to sort
    sort_list = []

    for i in range(widget.current_landmarks_list.GetNumberOfControlPoints()):
        sort_list.append([widget.current_landmarks_list.GetNthControlPointLabel(i),
                          widget.current_landmarks_list.GetNthControlPointID(i), -1])

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
                                                        widget.current_landmarks_list.GetName() + "_sorted")

    for idx, landmark in enumerate(final_list):
        index = widget.current_landmarks_list.GetNthControlPointIndexByID(landmark[1])

        sorted_markups.AddControlPoint(widget.current_landmarks_list.GetNthControlPointPosition(index),
                                       widget.current_landmarks_list.GetNthControlPointLabel(index))

        sorted_markups.SetNthControlPointDescription(idx,
                                                     widget.current_landmarks_list.GetNthControlPointDescription(index))


def remove_landmark_comment(widget):
    check_if_landmark_list_is_selected(widget)

    # get old description
    description = widget.current_landmarks_list.GetNthControlPointDescription(widget.current_control_point_idx)
    description = description.split(";")

    if description[0] != '':
        new_description = description[0]
    else:
        new_description = ''

    widget.current_landmarks_list.SetNthControlPointDescription(widget.current_control_point_idx, new_description)


def set_landmark_comment(widget, new_comment):
    check_if_landmark_list_is_selected(widget)

    # get old description
    description = widget.current_landmarks_list.GetNthControlPointDescription(widget.current_control_point_idx)
    description = description.split(";")

    if description == ['']:  # meaning there was no description
        new_description = "; " + new_comment
    elif description[0] != '':
        new_description = description[0] + "; " + new_comment
    else:
        new_description = "; " + new_comment

    widget.current_landmarks_list.SetNthControlPointDescription(widget.current_control_point_idx, new_description)


def set_landmark_status(widget, new_status):
    check_if_landmark_list_is_selected(widget)

    # get old description
    description = widget.current_landmarks_list.GetNthControlPointDescription(widget.current_control_point_idx)
    description = description.split(";")

    # get old comment
    if len(description) == 2:
        old_comment = description[1]  # it's the second part of the description
        new_description = new_status + ";" + old_comment

    else:  # if len is 1 this means that there is only a status
        new_description = new_status

    widget.current_landmarks_list.SetNthControlPointDescription(widget.current_control_point_idx, new_description)


def divide_landmarks_by_volume(widget):
    check_if_landmark_list_is_selected(widget)

    fiducial_node = widget.current_landmarks_list

    num_control_points = fiducial_node.GetNumberOfControlPoints()

    preop = []
    us1 = []
    us2 = []
    us3 = []
    intraop = []

    for i in range(num_control_points):
        label = fiducial_node.GetNthControlPointLabel(i)
        vector = fiducial_node.GetNthControlPointPosition(i)

        if "pre-op" in label.lower():
            preop.append([vector, label])
        elif "us1" in label.lower():
            us1.append([vector, label])
        elif "us2" in label.lower():
            us2.append([vector, label])
        elif "us3" in label.lower():
            us3.append([vector, label])
        elif "intra-op" in label.lower():
            intraop.append([vector, label])

    preop.sort(key=lambda y: y[1])
    us1.sort(key=lambda y: y[1])
    us2.sort(key=lambda y: y[1])
    us3.sort(key=lambda y: y[1])
    intraop.sort(key=lambda y: y[1])

    all_nodes = [preop, us1, us2, us3, intraop]

    max_len = max([len(i) for i in all_nodes])

    assert len(preop) == max_len or len(preop) == 0, "All volumes must have the same amount of landmarks (or none)"
    assert len(us1) == max_len or len(us1) == 0, "All volumes must have the same amount of landmarks (or none)"
    assert len(us2) == max_len or len(us2) == 0, "All volumes must have the same amount of landmarks (or none)"
    assert len(us3) == max_len or len(us3) == 0, "All volumes must have the same amount of landmarks (or none)"
    assert len(intraop) == max_len or len(
        intraop) == 0, "All volumes must have the same amount of landmarks (or none)"

    return all_nodes
