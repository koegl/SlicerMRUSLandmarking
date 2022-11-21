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


class VolumeNode:
    def __init__(self, volume_id: str = ""):
        self.volume_id = volume_id
        self.next_node = None
        self.previous_node = None


class VolumeCircle:
    def __init__(self, max_length=5):
        self.current_volume_node = None
        self.max_length = max_length
        self.current_length = 0

        self.first_node = None

    def add_volume_node(self, volume_node: 'VolumeNode'):

        if self.current_length == self.max_length:
            print(f"Cannot add more than {self.max_length} nodes. Nothing added.")
            return

        if self.current_volume_node is None:
            self.current_volume_node = volume_node
            self.first_node = volume_node
            self.current_length += 1
            return

        if self.current_volume_node is not None and self.current_length < self.max_length:
            self.current_volume_node.next_node = volume_node

            volume_node.previous_node = self.current_volume_node

            self.current_volume_node = volume_node

            self.current_length += 1

            if self.current_length == self.max_length:
                self.current_volume_node.next_node = self.first_node
                self.first_node.previous_node = self.current_volume_node

    def get_next_node(self):
        self.current_volume_node = self.current_volume_node.next_node
        return self.current_volume_node.volume_id

    def get_previous_node(self):
        self.current_volume_node = self.current_volume_node.previous_node
        return self.current_volume_node.volume_id

    def get_current_node(self):
        return self.current_volume_node.volume_id
