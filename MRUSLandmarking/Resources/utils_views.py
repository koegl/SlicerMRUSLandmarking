import slicer


def change_view(widget, direction='forward'):
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
                "Not enough volumes given for the volume switching shortcut")
            return

        if direction not in ['forward', 'backward']:
            slicer.util.errorDisplay(
                "Not enough volumes given for the volume switching shortcut")
            return

        initialise_views(widget)

        current_views = get_current_views(widget)

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
                next_combination = get_next_combination(widget, [current_foreground_id,
                                                                                       current_background_id],
                                                                              "forward")

            else:
                next_combination = get_next_combination(widget, [current_foreground_id,
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


def active_rows_update(widget):
    if widget.topRowActive and not widget.bottomRowActive:
        group_normal = 0
        group_plus = 1
    elif not widget.topRowActive and widget.bottomRowActive:
        group_normal = 1
        group_plus = 0
    else:  # when both are checked or unchecked
        group_normal = 0
        group_plus = 0

        # unchecked means that we can check them again, as both unchecked doesn't make sense
        widget.topRowActive = True
        widget.bottomRowActive = True

        widget.ui.topRowCheck.checked = True
        widget.ui.bottomRowCheck.checked = True

    # set groups
    for i in range(3):
        slicer.app.layoutManager().sliceWidget(widget.views_normal[i]).mrmlSliceNode().SetViewGroup(group_normal)
        slicer.app.layoutManager().sliceWidget(widget.views_plus[i]).mrmlSliceNode().SetViewGroup(group_plus)


def get_current_views(widget):
    """
    Function to determine currently active views (slices) ('active' means the ones for which all the functionality
    applies)
    return: An array of current views
            """
    # both rows or no rows active in 3o3
    if widget.topRowActive and widget.bottomRowActive and widget.view == '3on3':
        current_views = widget.views_normal + widget.views_plus

    elif (not widget.topRowActive) and (not widget.bottomRowActive) and widget.view == '3on3':
        current_views = widget.views_normal + widget.views_plus

    # bottom row active in 3o3
    elif not widget.topRowActive and widget.bottomRowActive and widget.view == '3on3':
        current_views = widget.views_plus

    # all other times we only care about the top row (views_normal)
    else:
        current_views = widget.views_normal

    return current_views


def initialise_views(widget):
    """
Initialise views with volumes. It only changes volumes if the currently displayed volumes are not in the list of
chosen volumes.
:return the composite node that can be used by the __change_view() function
"""
    # decide on slices to be updated depending on the view chosen
    current_views = get_current_views(widget)

    update = False

    for view in current_views:

        layoutManager = slicer.app.layoutManager()
        view_logic = layoutManager.sliceWidget(view).sliceLogic()
        widget.compositeNode = view_logic.GetSliceCompositeNode()

        current_background_id = widget.compositeNode.GetBackgroundVolumeID()
        current_foreground_id = widget.compositeNode.GetForegroundVolumeID()

        # check if there is a background
        if current_background_id is not None:

            # if it's not the correct volume, set the background and foreground
            if current_background_id not in widget.volumes_ids:
                # update volumes
                update = True

        else:  # there is no background
            # update volumes
            update = True

        if update:
            widget.compositeNode.SetBackgroundVolumeID(widget.volumes_ids[1])
            widget.compositeNode.SetForegroundVolumeID(widget.volumes_ids[0])
            update = False

        # check if there is a foreground
        if current_foreground_id is not None:

            # if it's not the correct volume, set the background and foreground
            if current_foreground_id not in widget.volumes_ids:
                # update volumes
                update = True

        else:  # there is no foreground
            # update volumes
            update = True

        if update:
            widget.compositeNode.SetBackgroundVolumeID(widget.volumes_ids[1])
            widget.compositeNode.SetForegroundVolumeID(widget.volumes_ids[0])
            update = False


def get_next_combination(widget, current_volume_ids=None, direction="forward"):
    """
Used for the shortcut to loop through the volumes. The idea is that always two consecutive images are overlayed. If
we have images [A,B,C,D] then if we start with images [A,B] the next combination will b [B,C] etc. This function
gets the current volume IDs and the switching direction as inputs and returns the next volume IDs.
:param current_volume_ids: Two currently displayed volumes
:param direction: The direction in which the switching will occur
:return: The next two IDs which should be displayed
"""

    if not widget.volumes_ids or not current_volume_ids:
        return None
    if direction not in ["forward", "backward"]:
        return None

    forward_combinations = []
    backward_combinations = []
    next_index = None

    # create list of possible forward pairs
    for i in range(len(widget.volumes_ids)):
        if i == len(widget.volumes_ids) - 1:
            index1 = len(widget.volumes_ids) - 1
            index2 = 0
        else:
            index1 = i
            index2 = i + 1

        forward_combinations.append([widget.volumes_ids[index1], widget.volumes_ids[index2]])
        backward_combinations.append([widget.volumes_ids[index2], widget.volumes_ids[index1]])

    try:
        if current_volume_ids in forward_combinations:
            current_index = forward_combinations.index(current_volume_ids)
        elif current_volume_ids in backward_combinations:
            current_index = backward_combinations.index(current_volume_ids)
        else:
            slicer.util.errorDisplay("Reset views to a valid order for volume switching.")
            return

    except Exception as e:
        slicer.util.errorDisplay("Reset views to a valid order for volume switching. " + str(e))
        return current_volume_ids

    combinations = forward_combinations

    if widget.switch and direction == "forward":
        direction = "backward"
    elif widget.switch and direction == "backward":
        direction = "forward"

    if direction == "forward":
        if current_index == len(widget.volumes_ids) - 1:
            next_index = 0
        else:
            next_index = current_index + 1

    elif direction == "backward":
        if current_index == 0:
            next_index = len(widget.volumes_ids) - 1
        else:
            next_index = current_index - 1

    return combinations[next_index]


def change_foreground_opacity_discrete(widget, new_opacity=0.5):
    """
    (This function is used as a shortcut)
    Changes the foreground opacity to a given value.
    :param new_opacity: The new foreground opacity
    """
    try:
        layoutManager = slicer.app.layoutManager()

        current_views = get_current_views(widget)

        # iterate through all views and set opacity to
        for sliceViewName in current_views:
            view = layoutManager.sliceWidget(sliceViewName).sliceView()
            sliceNode = view.mrmlSliceNode()
            sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
            compositeNode = sliceLogic.GetSliceCompositeNode()
            compositeNode.SetForegroundOpacity(new_opacity)

    except Exception as e:
        slicer.util.errorDisplay("Could not change foreground opacity discretely.\n" + str(e))


def change_foreground_opacity_continuous(widget, opacity_change=0.01):
    """
    (This function is used as a shortcut)
    Increases or decreases the foreground opacity by a given value
    :param opacity_change: The change in foreground opacity
    """
    try:
        layoutManager = slicer.app.layoutManager()

        current_views = get_current_views(widget)

        # iterate through all views and set opacity to
        for sliceViewName in current_views:
            view = layoutManager.sliceWidget(sliceViewName).sliceView()
            sliceNode = view.mrmlSliceNode()
            sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
            compositeNode = sliceLogic.GetSliceCompositeNode()
            compositeNode.SetForegroundOpacity(compositeNode.GetForegroundOpacity() + opacity_change)

    except Exception as e:
        slicer.util.errorDisplay("Could not change foreground opacity continuously.\n" + str(e))


def link_views():
    """
    Set linked slice views in all existing slice composite nodes and in the default node
    """

    sliceCompositeNodes = slicer.util.getNodesByClass("vtkMRMLSliceCompositeNode")
    defaultSliceCompositeNode = slicer.mrmlScene.GetDefaultNodeByClass("vtkMRMLSliceCompositeNode")
    if not defaultSliceCompositeNode:
        defaultSliceCompositeNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSliceCompositeNode")
        defaultSliceCompositeNode.UnRegister(
            None)  # CreateNodeByClass is factory method, need to unregister the result to prevent memory leaks
        slicer.mrmlScene.AddDefaultNode(defaultSliceCompositeNode)
    sliceCompositeNodes.append(defaultSliceCompositeNode)
    for sliceCompositeNode in sliceCompositeNodes:
        sliceCompositeNode.SetLinkedControl(True)
