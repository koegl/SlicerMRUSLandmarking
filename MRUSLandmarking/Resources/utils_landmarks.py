import slicer
import Resources


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
    # widget.current_landmarks_list = widget.ui.SimpleMarkupsWidget.currentNode()

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


def activate_fiducial_placement():
    """
    Entire fiducial logic - create list, activate appropriate list and set the placement widget
    """
    try:
        slicer.modules.markups.logic().StartPlaceMode(0)

        # set control point visibility off in 3D
        for fiducial_node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode"):
            d = fiducial_node.GetDisplayNode()
            d.Visibility3DOff()

    except Exception as e:
        slicer.util.errorDisplay("Could not activate fiducial placement.\n" + str(e))


def jump_to_next_landmark(widget, direction="forward"):
    """
    (This function is used as a shortcut)
    Jumps through all set landmarks.
    :param direction: The direction in which the landmarks are switched
    """
    try:

        if widget.nodes_circle is None:
            raise Exception("Pick the corresponding volumes first (or re-pick any existing one)")

        # set new landmark comment (if it is not empty)
        # set landmark comments
        new_comment = widget.ui.markupsCommentText.toPlainText()
        if new_comment == "x":  # this means delete the comment
            remove_landmark_comment(widget)
        elif new_comment != "":
            set_landmark_comment(widget, new_comment=new_comment)

        check_if_landmark_list_is_selected(widget)

        # get amount of control points
        control_points_amount = widget.current_landmarks_list.GetNumberOfControlPoints()

        # if there are 0 control points
        if control_points_amount == 0:
            slicer.util.errorDisplay("Create landmarks (control points) before trying to switch between them")
            return

        # increase or decrease index according to direction
        if direction == "forward":
            widget.current_control_point_idx += 1

            # if it's too big, circle back to 0-th index
            if widget.current_control_point_idx >= control_points_amount:
                widget.current_control_point_idx = 0

        elif direction == "backward":
            widget.current_control_point_idx -= 1

            # if it's too small start ath the last index again
            if widget.current_control_point_idx < 0:
                widget.current_control_point_idx = control_points_amount - 1

        else:  # wrong direction
            slicer.util.errorDisplay("Wrong switching direction (error in code).")
            return

        # update label
        widget.ui.landmarkNameLabel.setText(
            widget.current_landmarks_list.GetNthControlPointLabel(widget.current_control_point_idx))
        current_description = widget.current_landmarks_list.GetNthControlPointDescription(
            widget.current_control_point_idx)
        current_description = current_description.split(';')[0]

        if current_description == "Accepted":
            widget.ui.acceptedLandmarkCheck.checked = True
        else:
            widget.ui.acceptedLandmarkCheck.checked = False

        if current_description == "Modify":
            widget.ui.modifyLandmarkCheck.checked = True
        else:
            widget.ui.modifyLandmarkCheck.checked = False

        if current_description == "Rejected":
            widget.ui.rejectedLandmarkCheck.checked = True
        else:
            widget.ui.rejectedLandmarkCheck.checked = False

        # display comment
        description = widget.current_landmarks_list.GetNthControlPointDescription(
            widget.current_control_point_idx).split(';')
        if len(description) == 1:  # this means there is only a status
            comment = ''
        else:
            comment = description[1][1:]

        widget.ui.markupsCommentText.setPlainText(comment)

        # uncheck label vis
        widget.ui.labelVisCheck.checked = False

        # update volumes according to the current control point label
        if widget.view == "normal":
            current_label = widget.current_landmarks_list.GetNthControlPointLabel(widget.current_control_point_idx)
            for i in range(5):  # because we have 5 possible volumes

                # we need this reversal because jumping landmarks and volumes are reversed
                if direction == "forward":
                    new_direction = "backward"
                else:
                    new_direction = "forward"

                Resources.utils_views.change_view(widget, direction=new_direction)

                current_id = widget.compositeNode.GetBackgroundVolumeID()
                current_name = slicer.mrmlScene.GetNodeByID(current_id).GetName()

                if current_label.split(' ')[1].lower() in current_name.lower():
                    break

            # make all other fiducials not visible
            for i in range(control_points_amount):
                if i != widget.current_control_point_idx:
                    widget.current_landmarks_list.SetNthControlPointVisibility(i, False)
                else:
                    widget.current_landmarks_list.SetNthControlPointVisibility(i, True)

        else:

            second_control_point_idx = widget.current_control_point_idx + 1
            if second_control_point_idx == control_points_amount:
                second_control_point_idx = 0

            label_bottom = widget.current_landmarks_list.GetNthControlPointLabel(widget.current_control_point_idx)

            # change view groups of the normal views to 0
            for i in range(3):
                slicer.app.layoutManager().sliceWidget(widget.views_normal[i]).mrmlSliceNode().SetViewGroup(
                    0)
                slicer.app.layoutManager().sliceWidget(widget.views_plus[i]).mrmlSliceNode().SetViewGroup(1)

            storage_top_row = widget.topRowActive
            storage_bottom_row = widget.bottomRowActive
            widget.topRowActive = False
            widget.bottomRowActive = True

            for i in range(5):  # because we have 5 possible volumes

                # we need this reversal because jumping landmarks and volumes are reversed
                if direction == "forward":
                    new_direction = "backward"
                else:
                    new_direction = "forward"

                Resources.utils_views.change_view(widget, direction=new_direction)

                current_id = widget.compositeNode.GetBackgroundVolumeID()
                current_name = slicer.mrmlScene.GetNodeByID(current_id).GetName()

                if "pre" in current_name.lower() and "op" in current_name.lower() and "pre-op" in label_bottom.lower():
                    current_name = "pre-op"
                elif "intra" in current_name.lower() and "op" in current_name.lower() and "intra-op" in label_bottom.lower():
                    current_name = "intra-op"

                if label_bottom.split(' ')[1].lower() in current_name.lower():
                    break

            # get n-th control point vector
            pos = widget.current_landmarks_list.GetNthControlPointPositionVector(
                widget.current_control_point_idx)

            # center views on current control point
            slicer.modules.markups.logic().JumpSlicesToLocation(pos[0], pos[1], pos[2], True, 1)

            # center crosshair on current control point
            crosshairNode = slicer.util.getNode("Crosshair")
            crosshairNode.SetCrosshairRAS(pos)
            crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowBasic)  # make it visible

            label_top = widget.current_landmarks_list.GetNthControlPointLabel(second_control_point_idx)

            widget.topRowActive = True
            widget.bottomRowActive = False

            for i in range(5):  # because we have 5 possible volumes

                # we need this reversal because jumping landmarks and volumes are reversed
                if direction == "forward":
                    new_direction = "backward"
                else:
                    new_direction = "forward"

                Resources.utils_views.change_view(widget, direction=new_direction)

                current_id = widget.compositeNode.GetBackgroundVolumeID()
                current_name = slicer.mrmlScene.GetNodeByID(current_id).GetName()

                if "pre" in current_name.lower() and "op" in current_name.lower() and "pre-op" in label_top.lower():
                    current_name = "pre-op"
                elif "intra" in current_name.lower() and "op" in current_name.lower() and "intra-op" in label_top.lower():
                    current_name = "intra-op"

                if label_top.split(' ')[1].lower() in current_name.lower():
                    break

            # get n-th control point vector
            pos = widget.current_landmarks_list.GetNthControlPointPositionVector(second_control_point_idx)

            # center views on current control point
            slicer.modules.markups.logic().JumpSlicesToLocation(pos[0], pos[1], pos[2], True, 0)

            # # center crosshair on current control point
            # crosshairNode = slicer.util.getNode("Crosshair")
            # crosshairNode.SetCrosshairRAS(pos)
            # crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowBasic)  # make it visible

            widget.topRowActive = storage_top_row
            widget.bottomRowActive = storage_bottom_row

            Resources.utils_views.active_rows_update(widget)

            # make all other fiducials not visible

            for i in range(control_points_amount):
                if i == widget.current_control_point_idx or i == second_control_point_idx:
                    widget.current_landmarks_list.SetNthControlPointVisibility(i, True)
                else:
                    widget.current_landmarks_list.SetNthControlPointVisibility(i, False)

        turn_off_placement_mode()

    except Exception as e:

        turn_off_placement_mode()

        slicer.util.errorDisplay("Could not jump to next landmark.\n" + str(e))

