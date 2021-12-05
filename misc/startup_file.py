# Python commands in this file are executed on Slicer startup

# Examples:
#
# Load a scene file
# slicer.util.loadScene('c:/Users/SomeUser/Documents/SlicerScenes/SomeScene.mrb')
#
# Open a module (overrides default startup module in application settings / modules)
# slicer.util.mainWindow().moduleSelector().selectModule('SegmentEditor')
#

# automatically link views
# Set linked slice views  in all existing slice composite nodes and in the default node
sliceCompositeNodes = slicer.util.getNodesByClass("vtkMRMLSliceCompositeNode")
defaultSliceCompositeNode = slicer.mrmlScene.GetDefaultNodeByClass("vtkMRMLSliceCompositeNode")
if not defaultSliceCompositeNode:
  defaultSliceCompositeNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSliceCompositeNode")
  defaultSliceCompositeNode.UnRegister(None)  # CreateNodeByClass is factory method, need to unregister the result to prevent memory leaks
  slicer.mrmlScene.AddDefaultNode(defaultSliceCompositeNode)
sliceCompositeNodes.append(defaultSliceCompositeNode)
for sliceCompositeNode in sliceCompositeNodes:
  sliceCompositeNode.SetLinkedControl(True)
