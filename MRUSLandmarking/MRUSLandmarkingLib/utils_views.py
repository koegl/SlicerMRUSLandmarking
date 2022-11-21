import slicer


def change_view(widget, direction='forward'):
    """
    (This function is used as a shortcut)
    Change the view forward or backward. If 'forward', then foreground becomes the old background; if 'backward', then
    baclground becomes the old foreground
    :param direction: The direction in which the volumes are switched
    """

    try:
        if len(widget.volumes_ids) < 2:
            raise Exception("Not enough volumes for volume switching")

        # initialise views with volumes in case none are shown
        initialise_views(widget)

        # get the current views (it it's normal or 3on3)
        current_views = get_current_views(widget)

        # get the next volumes
        if direction == 'forward':
            update_circle_node(widget, "forward")  # updates current node to background

            volume_foreground = slicer.mrmlScene.GetNodeByID(widget.nodes_circle.get_current_node())
            volume_background = slicer.mrmlScene.GetNodeByID(widget.nodes_circle.get_next_node())
        else:
            update_circle_node(widget, "backward")  # updates current node to foreground

            volume_background = slicer.mrmlScene.GetNodeByID(widget.nodes_circle.get_current_node())
            volume_foreground = slicer.mrmlScene.GetNodeByID(widget.nodes_circle.get_previous_node())

        # set the next volumes in all the views
        for view in current_views:
            layoutManager = slicer.app.layoutManager()
            view_logic = layoutManager.sliceWidget(view)
            view_logic = view_logic.sliceLogic()
            widget.compositeNode = view_logic.GetSliceCompositeNode()

            # update volumes (if they both exist)
            if volume_foreground and volume_background:
                widget.compositeNode.SetBackgroundVolumeID(volume_background.GetID())
                widget.compositeNode.SetForegroundVolumeID(volume_foreground.GetID())
            else:
                raise Exception("No volumes to set for foreground and background")

    except Exception as e:
        slicer.util.errorDisplay("Could not change view.\n" + str(e))


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
    """
    # decide on slices to be updated depending on the view chosen
    current_views = get_current_views(widget)

    update = False

    layout_manager = slicer.app.layoutManager()

    for view in current_views:

        view_logic = layout_manager.sliceWidget(view).sliceLogic()
        widget.compositeNode = view_logic.GetSliceCompositeNode()

        current_background_id = widget.compositeNode.GetBackgroundVolumeID()
        current_foreground_id = widget.compositeNode.GetForegroundVolumeID()

        if current_background_id not in widget.volumes_ids and current_foreground_id not in widget.volumes_ids:
            update = True

        if update is True:
            widget.compositeNode.SetBackgroundVolumeID(widget.volumes_ids[1])
            widget.compositeNode.SetForegroundVolumeID(widget.volumes_ids[0])


def update_circle_node(widget, direction):

    if widget.nodes_circle is None:
        raise Exception("Pick a volume first - or re-pick any existing one")

    if direction == "forward":
        while widget.nodes_circle.current_volume_node.volume_id != widget.compositeNode.GetBackgroundVolumeID():
            widget.nodes_circle.get_next_node()

    elif direction == "backward":
        while widget.nodes_circle.current_volume_node.volume_id != widget.compositeNode.GetForegroundVolumeID():
            widget.nodes_circle.get_next_node()


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
