import slicer


def markup_curve_adjustment(curve_node_id):
    # get color table
    iron = slicer.util.getFirstNodeByName("Iron")

    # set visibility to only 3D
    curveNode = slicer.mrmlScene.GetNodeByID(curve_node_id.GetID())
    dispNode = curveNode.GetDisplayNode()
    dispNode.Visibility2DOff()

    # change curve to gradient
    dispNode.SetActiveScalarName("PedigreeIDs")
    dispNode.SetAndObserveColorNodeID(iron.GetID())

    # other parameters
    dispNode.SetScalarVisibility(1)
    dispNode.SetLineThickness(0.6)
    dispNode.SetTextScale(0)

    dispNode.UpdateAssignedAttribute()
    dispNode.Modified()



