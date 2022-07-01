import slicer

import Resources


def stc_activate_fiducial_placement():
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


def stc_change_view(widget, direction='forward'):
    """
    (This function is used as a shortcut)
    Change the view forward or backward (take the list of possible volumes and for the two displayed volumes increase
    their index by one) using the get_current_views() function
    :param direction: The direction in which the volumes are switched
    """

    try:
        if widget.ui.inputSelector0.currentNode() is None and \
           widget.ui.inputSelector1.currentNode() is None and \
           widget.ui.inputSelector2.currentNode() is None and \
           widget.ui.inputSelector3.currentNode() is None and \
           widget.ui.inputSelector4.currentNode() is None:
            slicer.util.errorDisplay(
                "Not enough volumes given for the volume switching shortcut (choose all in the 'Common "
                "field of view'")
            return

        if direction not in ['forward', 'backward']:
            slicer.util.errorDisplay(
                "Not enough volumes given for the volume switching shortcut (choose all in the 'Common "
                "field of view'")
            return

        Resources.utils_views.initialise_views(widget)

        current_views = Resources.utils_views.get_current_views(widget)

        for view in current_views:
            layoutManager = slicer.app.layoutManager()
            view_logic = layoutManager.sliceWidget(view)
            view_logic = view_logic.sliceLogic()
            widget.compositeNode = view_logic.GetSliceCompositeNode()

            # get current foreground and background volumes
            current_foreground_id = widget.compositeNode.GetForegroundVolumeID()
            current_background_id = widget.compositeNode.GetBackgroundVolumeID()

            # switch backgrounds
            if direction == 'forward':
                next_combination = Resources.utils_views.get_next_combination(widget, [current_foreground_id,
                                                                                       current_background_id],
                                                                              "forward")

            else:
                next_combination = Resources.utils_views.get_next_combination(widget, [current_foreground_id,
                                                                                       current_background_id],
                                                                              "backward")

            volume_foreground = slicer.mrmlScene.GetNodeByID(next_combination[0])
            volume_background = slicer.mrmlScene.GetNodeByID(next_combination[1])

            # update volumes (if they both exist)
            if volume_foreground and volume_background:
                if direction == 'backward' or direction == 'forward':
                    widget.compositeNode.SetBackgroundVolumeID(volume_background.GetID())
                    widget.compositeNode.SetForegroundVolumeID(volume_foreground.GetID())

                else:
                    slicer.util.errorDisplay("wrong direction")
            else:
                slicer.util.errorDisplay("No volumes to set for foreground and background")

            # rotate slices to lowest volume (otherwise the volumes can be missaligned a bit
            # slicer.app.layoutManager().sliceWidget(view).sliceController().rotateSliceToLowestVolumeAxes()

    except Exception as e:
        slicer.util.errorDisplay("Could not chnage view.\n" + str(e))


def stc_change_foreground_opacity_discrete(widget, new_opacity=0.5):
    """
    (This function is used as a shortcut)
    Changes the foreground opacity to a given value.
    :param new_opacity: The new foreground opacity
    """
    try:
        layoutManager = slicer.app.layoutManager()

        current_views = Resources.utils_views.get_current_views(widget)

        # iterate through all views and set opacity to
        for sliceViewName in current_views:
            view = layoutManager.sliceWidget(sliceViewName).sliceView()
            sliceNode = view.mrmlSliceNode()
            sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
            compositeNode = sliceLogic.GetSliceCompositeNode()
            compositeNode.SetForegroundOpacity(new_opacity)

    except Exception as e:
        slicer.util.errorDisplay("Could not change foreground opacity discretely.\n" + str(e))


def stc_change_foreground_opacity_continuous(widget, opacity_change=0.01):
    """
    (This function is used as a shortcut)
    Increases or decreases the foreground opacity by a given value
    :param opacity_change: The change in foreground opacity
    """
    try:
        layoutManager = slicer.app.layoutManager()

        current_views = Resources.utils_views.get_current_views(widget)

        # iterate through all views and set opacity to
        for sliceViewName in current_views:
            view = layoutManager.sliceWidget(sliceViewName).sliceView()
            sliceNode = view.mrmlSliceNode()
            sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
            compositeNode = sliceLogic.GetSliceCompositeNode()
            compositeNode.SetForegroundOpacity(compositeNode.GetForegroundOpacity() + opacity_change)

    except Exception as e:
        slicer.util.errorDisplay("Could not change foreground opacity continuously.\n" + str(e))


def stc_jump_to_next_landmark(widget, direction="forward"):
    """
    (This function is used as a shortcut)
    Jumps through all set landmarks.
    :param direction: The direction in which the landmarks are switched
    """
    try:
        # get markup node

        # set new landmark comment (if it is not empty)
        # set landmark comments
        new_comment = widget.ui.markupsCommentText.toPlainText()
        if new_comment == "x":  # this means delete the comment
            Resources.utils_landmarks.remove_landmark_comment(widget)
        elif new_comment != "":
            Resources.utils_landmarks.set_landmark_comment(widget, new_comment=new_comment)

        Resources.utils_landmarks.check_if_landmark_list_is_selected(widget)

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

        # get n-th control point vector
        pos = widget.current_landmarks_list.GetNthControlPointPositionVector(widget.current_control_point_idx)

        # center views on current control point
        slicer.modules.markups.logic().JumpSlicesToLocation(pos[0], pos[1], pos[2], False, 0)

        # center crosshair on current control point
        crosshairNode = slicer.util.getNode("Crosshair")
        crosshairNode.SetCrosshairRAS(pos)
        crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowBasic)  # make it visible

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

        # make all other fiducials not visible
        # for i in range(control_points_amount):
        #     if i != widget.current_control_point_idx:
        #         widget.current_landmarks_list.SetNthControlPointVisibility(i, False)
        #     else:
        #         widget.current_landmarks_list.SetNthControlPointVisibility(i, True)

        # uncheck label vis
        widget.ui.labelVisCheck.checked = False

        # update volumes according to the current control point label
        current_label = widget.current_landmarks_list.GetNthControlPointLabel(widget.current_control_point_idx)
        for i in range(5):  # because we have 5 possible volumes

            # we need this reversal because jumping landmarks and volumes are reversed
            if direction == "forward":
                new_direction = "backward"
            else:
                new_direction = "forward"

            Resources.shortcuts.stc_change_view(widget, direction=new_direction)

            current_id = widget.compositeNode.GetBackgroundVolumeID()
            current_name = slicer.mrmlScene.GetNodeByID(current_id).GetName()

            if current_label.split(' ')[1].lower() in current_name.lower():
                break

        Resources.utils_landmarks.turn_off_placement_mode()

    except Exception as e:
        slicer.util.errorDisplay("Could not jump to next landmark.\n" + str(e))


"""
stc_jump_to_next_landmark
"""
