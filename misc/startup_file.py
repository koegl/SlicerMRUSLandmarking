# Python commands in this file are executed on Slicer startup

# Examples:
#
# Load a scene file
# slicer.util.loadScene('c:/Users/SomeUser/Documents/SlicerScenes/SomeScene.mrb')
#
# Open a module (overrides default startup module in application settings / modules)
# slicer.util.mainWindow().moduleSelector().selectModule('SegmentEditor')
#

# ADDING SHORTCUTS
# https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html
# Switching to markups control point placement mode
# switching between us volumes (the us-volumes are hardcoded now) # TODO un-hardcode the volumes - somehow get them from
# my extension


def initialise_views(volumes=None):
    if volumes is None:
        volumes = ["US1 Pre-dura", "US2 Post-dura", "US3 Resection Control"]

    # get current foreground and background volumes
    layoutManager = slicer.app.layoutManager()
    view = layoutManager.sliceWidget('Red').sliceView()
    sliceNode = view.mrmlSliceNode()
    sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
    compositeNode = sliceLogic.GetSliceCompositeNode()

    current_background_id = compositeNode.GetBackgroundVolumeID()
    current_foreground_id = compositeNode.GetForegroundVolumeID()

    # check if there is a background
    if current_background_id is not None:
        current_background_volume = slicer.mrmlScene.GetNodeByID(current_background_id)
        current_background_name = current_background_volume.GetName()

        # if it's not the correct volume, set the background and foreground
        if current_background_name not in volumes:
            volume_background = slicer.mrmlScene.GetFirstNodeByName(volumes[2])
            volume_foreground = slicer.mrmlScene.GetFirstNodeByName(volumes[1])

            # update volumes
            slicer.util.setSliceViewerLayers(background=volume_background, foreground=volume_foreground)

    else:  # there is no background
        volume_background = slicer.mrmlScene.GetFirstNodeByName(volumes[2])
        volume_foreground = slicer.mrmlScene.GetFirstNodeByName(volumes[1])

        # update volumes
        slicer.util.setSliceViewerLayers(background=volume_background, foreground=volume_foreground)

    # check if there is a foreground
    if current_foreground_id is not None:
        current_foreground_volume = slicer.mrmlScene.GetNodeByID(current_background_id)
        current_foreground_name = current_foreground_volume.GetName()

        # if it's not the correct volume, set the background and foreground
        if current_foreground_name not in volumes:
            volume_background = slicer.mrmlScene.GetFirstNodeByName(volumes[2])
            volume_foreground = slicer.mrmlScene.GetFirstNodeByName(volumes[1])
            # update volumes
            slicer.util.setSliceViewerLayers(background=volume_background, foreground=volume_foreground)

    else:  # there is no foreground
        volume_background = slicer.mrmlScene.GetFirstNodeByName(volumes[2])
        volume_foreground = slicer.mrmlScene.GetFirstNodeByName(volumes[1])

        # update volumes
        slicer.util.setSliceViewerLayers(background=volume_background, foreground=volume_foreground)

    return compositeNode


def change_view_forward():

    volumes = ["US1 Pre-dura", "US2 Post-dura", "US3 Resection Control"]
    volume_background = None
    volume_foreground = None

    # initialise views and get the composite node
    compositeNode = initialise_views()

    # get current foreground and background volumes
    current_foreground_id = compositeNode.GetForegroundVolumeID()
    current_foreground_volume = slicer.mrmlScene.GetNodeByID(current_foreground_id)
    current_foreground_name = current_foreground_volume.GetName()
    current_background_id = compositeNode.GetBackgroundVolumeID()
    current_background_volume = slicer.mrmlScene.GetNodeByID(current_background_id)
    current_background_name = current_background_volume.GetName()

    # switch backgrounds
    if current_background_name == volumes[2] and current_foreground_name == volumes[1]:
        volume_background = current_foreground_volume
        volume_foreground = slicer.mrmlScene.GetFirstNodeByName(volumes[0])
    elif current_background_name == volumes[1] and current_foreground_name == volumes[0]:
        volume_background = current_foreground_volume
        volume_foreground = slicer.mrmlScene.GetFirstNodeByName(volumes[2])
    elif current_background_name == volumes[0] and current_foreground_name == volumes[2]:
        volume_background = current_foreground_volume
        volume_foreground = slicer.mrmlScene.GetFirstNodeByName(volumes[1])

    elif current_background_name == volumes[2] and current_foreground_name == volumes[0]:
        volume_foreground = current_background_volume
        volume_background = slicer.mrmlScene.GetFirstNodeByName(volumes[1])
    elif current_background_name == volumes[0] and current_foreground_name == volumes[1]:
        volume_foreground = current_background_volume
        volume_background = slicer.mrmlScene.GetFirstNodeByName(volumes[2])
    elif current_background_name == volumes[1] and current_foreground_name == volumes[2]:
        volume_foreground = current_background_volume
        volume_background = slicer.mrmlScene.GetFirstNodeByName(volumes[0])

    # update volumes (if they both exist)
    if volume_foreground and volume_background:
        slicer.util.setSliceViewerLayers(background=volume_background, foreground=volume_foreground)
    else:
        print("No volumes to set for foreground and background")


def change_view_backward():

    volumes = ["US1 Pre-dura", "US2 Post-dura", "US3 Resection Control"]
    volume_background = None
    volume_foreground = None

    # initialise views and get the composite node
    compositeNode = initialise_views()

    # TODO link all views (red, green and yellow)
    # set variables for current foreground and background
    current_background_id = compositeNode.GetBackgroundVolumeID()
    current_foreground_id = compositeNode.GetForegroundVolumeID()
    current_foreground_volume = slicer.mrmlScene.GetNodeByID(current_foreground_id)
    current_background_volume = slicer.mrmlScene.GetNodeByID(current_background_id)
    current_foreground_name = current_foreground_volume.GetName()
    current_background_name = current_background_volume.GetName()

    # switch backgrounds
    if current_background_name == volumes[2] and current_foreground_name == volumes[1]:
        volume_foreground = current_background_volume
        volume_background = slicer.mrmlScene.GetFirstNodeByName(volumes[0])
    elif current_background_name == volumes[1] and current_foreground_name == volumes[0]:
        volume_foreground = current_background_volume
        volume_background = slicer.mrmlScene.GetFirstNodeByName(volumes[2])
    elif current_background_name == volumes[0] and current_foreground_name == volumes[2]:
        volume_foreground = current_background_volume
        volume_background = slicer.mrmlScene.GetFirstNodeByName(volumes[1])

    elif current_background_name == volumes[2] and current_foreground_name == volumes[0]:
        volume_background = current_foreground_volume
        volume_foreground = slicer.mrmlScene.GetFirstNodeByName(volumes[1])
    elif current_background_name == volumes[0] and current_foreground_name == volumes[1]:
        volume_background = current_foreground_volume
        volume_foreground = slicer.mrmlScene.GetFirstNodeByName(volumes[2])
    elif current_background_name == volumes[1] and current_foreground_name == volumes[2]:
        volume_background = current_foreground_volume
        volume_foreground = slicer.mrmlScene.GetFirstNodeByName(volumes[0])

    # update volumes (if they both exist)
    if volume_foreground and volume_background:
        slicer.util.setSliceViewerLayers(background=volume_background, foreground=volume_foreground)
    else:
        print("No volumes to set for foreground and background")


interactionNode = slicer.app.applicationLogic().GetInteractionNode()


shortcuts = [('d', lambda: interactionNode.SetCurrentInteractionMode(interactionNode.Place)),
             ('a', change_view_forward),
             ('s', change_view_backward)]

for (shortcutKey, callback) in shortcuts:
    shortcut = qt.QShortcut(slicer.util.mainWindow())
    shortcut.setKey(qt.QKeySequence(shortcutKey))
    shortcut.connect('activated()', callback)
