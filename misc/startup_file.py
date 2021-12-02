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
interactionNode = slicer.app.applicationLogic().GetInteractionNode()
shortcuts = [('d', lambda: interactionNode.SetCurrentInteractionMode(interactionNode.Place))]

for (shortcutKey, callback) in shortcuts:
    shortcut = qt.QShortcut(slicer.util.mainWindow())
    shortcut.setKey(qt.QKeySequence(shortcutKey))
    shortcut.connect( 'activated()', callback)
