import unittest
import numpy as np
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import SegmentEditorEffects
import functools
import importlib

import Resources.utils
import Resources.utils_landmarks
import Resources.utils_views
importlib.reload(Resources.utils)
importlib.reload(Resources.utils_landmarks)
importlib.reload(Resources.utils_views)


#
# MRUSLandmarking
#

class MRUSLandmarking(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "MRUSLandmarking"
        self.parent.categories = ["Informatics"]
        self.parent.dependencies = ["Markups"]
        self.parent.contributors = ["Fryderyk Kögl (TUM, BWH), Harneet Cheema (BWH, UOttawa), Tina Kapur (BWH)"]
        self.parent.helpText = """
    Module that gather useful Slicer functionality for setting landmarks in MR and US images. To start choose the
    volumes that you want to use, create an intersection of the US FOV to make sure your landmarks are all in an
    overlapping area and the customise your view. Use the shortcuts listed at the bottom to increase the efficiency of
    the workflow.
    https://github.com/koegl/MRUSLandmarking
    """
        self.parent.acknowledgementText = """
    This extension was developed at the Brigham and Women's Hospital by Fryderyk Kögl, Harneet Cheema and Tina Kapur.
    
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
    """


#
# MRUSLandmarkingWidget
#
#
class MRUSLandmarkingWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
    Called when the user opens the module the first time and the widget is initialized.
    """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

        Resources.utils_views.link_views()

        self.compositeNode = None
        self.volumes_ids = None

        # variable saying if views in 3-over-3 are linked or not
        self.topRowActive = True
        self.bottomRowActive = False
        self.view = 'normal'
        self.views_normal = ["Red", "Green", "Yellow"]
        self.views_plus = ["Red+", "Green+", "Yellow+"]

        self.labelVisCheck = True

        self.switch = False

        self.fiducial_nodes = {}  # a dict that will contain all fiducial node ids and their corresponding volume ids
        self.curve_nodes = {}  # a dict that will contain all curve node ids and their corresponding fiducial index

        # used for updating the correct row when rows are linked
        # self.changing = "bottom"

        # for switching between markup control points
        self.current_landmarks_list = None
        self.current_control_point_idx = 0

        self.landmark_dict = {}

        self.__initialiseShortcuts()

        self.nodes_circle_normal = None
        self.nodes_circle_plus = None
        self.nodes_circle = None
        self.old_volume_ids = []

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/MRUSLandmarking.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = MRUSLandmarkingLogic()

        # enable none option for input selectors
        self.ui.inputSelector0.noneEnabled = True
        self.ui.inputSelector1.noneEnabled = True
        self.ui.inputSelector2.noneEnabled = True
        self.ui.inputSelector3.noneEnabled = True
        self.ui.inputSelector4.noneEnabled = True

        # set node type for input selectors
        self.ui.inputSelector0.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.ui.inputSelector1.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.ui.inputSelector2.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.ui.inputSelector3.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.ui.inputSelector4.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        # self.ui.landmarksSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).

        self.ui.inputSelector0.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.inputSelector1.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.inputSelector2.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.inputSelector3.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.inputSelector4.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.SimpleMarkupsWidget.connect("markupsFiducialNodeChanged()", self.update_landmark_list_from_gui)

        self.input_selectors = [self.ui.inputSelector4,
                                self.ui.inputSelector3,
                                self.ui.inputSelector2,
                                self.ui.inputSelector1,
                                self.ui.inputSelector0]

        # Buttons
        # reset views
        self.ui.resetViewsButton.setStyleSheet('background-color: red;')
        self.ui.resetViewsButton.connect('clicked(bool)', self.onResetViewsButton)
        # create intersection outline
        self.ui.intersectionButton.connect('clicked(bool)', self.onIntersectionButton)
        # set foreground threshold to 1 for all chosen volumes
        self.ui.thresholdButton.connect('clicked(bool)', self.onThresholdButton)
        # change to standard view
        self.ui.viewStandardButton.connect('clicked(bool)', self.onViewStandardButton)
        # change to 3 over 3 view view
        self.ui.view3o3Button.connect('clicked(bool)', self.onView3o3Button)
        # switch order of displaying volumes
        self.ui.switchOrderButton.connect('clicked(bool)', self.onSwitchOrderButton)
        # sync all views
        self.ui.syncViewsButton.connect('clicked(bool)', self.onSyncViewsButton)
        # update landmark flow
        self.ui.updateFlow.connect('clicked(bool)', self.onUpdateFlow)
        # sort landmartks
        self.ui.sortLandmarksButton.connect('clicked(bool)', self.onSortLandmarksButton)

        self.ui.misc1Button.connect('clicked(bool)', self.onMisc1Button)
        self.ui.misc2Button.connect('clicked(bool)', self.onMisc2Button)

        # inspection results button
        self.ui.printResultsButton.connect('clicked(bool)', self.onPrintResultsButton)

        # Check boxes
        # Activate rows
        self.ui.topRowCheck.connect('clicked(bool)', self.onTopRowCheck)
        self.ui.bottomRowCheck.connect('clicked(bool)', self.onBottomRowCheck)

        # label visibility
        self.ui.labelVisCheck.connect('clicked(bool)', self.onLabelVisCheck)

        # landmark status
        self.ui.acceptedLandmarkCheck.connect('clicked(bool)', self.onAcceptedLandmarkCheck)
        self.ui.modifyLandmarkCheck.connect('clicked(bool)', self.onModifyLandmarkCheck)
        self.ui.rejectedLandmarkCheck.connect('clicked(bool)', self.onRejectedLandmarkCheck)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

        # shortcuts
        # self.__initialiseShortcuts()  # those that depend on the volumes - they have to be defined in this class,
        # as they need the updated ui stuff to work

    def cleanup(self):
        """
    Called when the application closes and the module widget is destroyed.
    """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
    Called each time the user opens a different module.
    """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
    Called just before the scene is closed.
    """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
    Called just after the scene is closed.
    """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        input_volumes = ["InputVolume0", "InputVolume1", "InputVolume2", "InputVolume3", "InputVolume4"]
        us_volumes = [["pre-op", "preop"], ["us1", "us1"], ["us2", "us2"], ["us3", "us3"], ["intra-op", "intraop"]]

        # only select default nodes when nothing is selected (otherwise changing modules back and forth triggers this)
        chosen_nodes = [selector.currentNode() for selector in self.input_selectors]

        # nothing is selected means that we have only None in the list
        volumeNode = None
        if not any(chosen_nodes):
            for input_volume, volume_name in zip(input_volumes, us_volumes):
                if not self._parameterNode.GetNodeReference(input_volume):

                    # try to get a volume node that contains one of the names
                    for node in slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode"):
                        if volume_name[0] in node.GetName().lower() or volume_name[1] in node.GetName().lower():
                            volumeNode = node
                            break

                    if volumeNode:
                        self._parameterNode.SetNodeReferenceID(input_volume, volumeNode.GetID())

        # if not self._parameterNode.GetNodeReference("Landmarks"):
        #     if self.ui.SimpleMarkupsWidget.currentNode() is not None:
        #         self._parameterNode.SetNodeReferenceID("Landmarks", self.ui.SimpleMarkupsWidget.currentNode().GetID())

        # update chosen volumes
        self.volumes_ids = []

        for selector in self.input_selectors:
            if selector.currentNode():
                self.volumes_ids.append(selector.currentNode().GetID())

        self.ui.topRowCheck.toolTip = "Switch to 3-over-3 view to disable top row"
        self.ui.bottomRowCheck.toolTip = "Switch to 3-over-3 view to enable bottom row"

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # Update node selectors
        self.ui.inputSelector0.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume0"))
        self.ui.inputSelector1.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume1"))
        self.ui.inputSelector2.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume2"))
        self.ui.inputSelector3.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume3"))
        self.ui.inputSelector4.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume4"))
        # self.ui.SimpleMarkupsWidget.setCurrentNode(self._parameterNode.GetNodeReference("Landmarks"))

        # update button states and tooltips - only if volumes are chosen, enable buttons
        if self._parameterNode.GetNodeReference("InputVolume0") or \
            self._parameterNode.GetNodeReference("InputVolume1") or \
            self._parameterNode.GetNodeReference("InputVolume2") or \
            self._parameterNode.GetNodeReference("InputVolume3") or \
            self._parameterNode.GetNodeReference("InputVolume4"):
            self.ui.intersectionButton.toolTip = "Compute intersection"
            self.ui.intersectionButton.enabled = True

            self.ui.thresholdButton.toolTip = "Set lower thresholds of chosen volumes to 1"
            self.ui.thresholdButton.enabled = True
        else:
            self.ui.intersectionButton.toolTip = "Select all input volumes first"
            self.ui.intersectionButton.enabled = False

            self.ui.thresholdButton.toolTip = "Select all input volumes first"
            self.ui.thresholdButton.enabled = False

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        self._parameterNode.SetNodeReferenceID("InputVolume0", self.ui.inputSelector0.currentNodeID)
        self._parameterNode.SetNodeReferenceID("InputVolume1", self.ui.inputSelector1.currentNodeID)
        self._parameterNode.SetNodeReferenceID("InputVolume2", self.ui.inputSelector2.currentNodeID)
        self._parameterNode.SetNodeReferenceID("InputVolume3", self.ui.inputSelector3.currentNodeID)
        self._parameterNode.SetNodeReferenceID("InputVolume4", self.ui.inputSelector4.currentNodeID)

        # if self.ui.SimpleMarkupsWidget.currentNode():
        #     self._parameterNode.SetNodeReferenceID("Landmarks", self.ui.SimpleMarkupsWidget.currentNode().GetID())

        # self.current_landmarks_list = self.ui.SimpleMarkupsWidget.currentNode()

        self._parameterNode.EndModify(wasModified)

        # update volumes
        self.old_volume_ids = self.volumes_ids
        self.volumes_ids = []

        for selector in self.input_selectors:
            if selector.currentNode():
                self.volumes_ids.append(selector.currentNode().GetID())

        # if the newly selected volume ids are different from the old, the update the circular data structure used for
        # changing views
        if self.old_volume_ids != self.volumes_ids:

            self.nodes_circle_normal = Resources.utils.VolumeCircle(max_length=len(self.volumes_ids))
            self.nodes_circle_plus = Resources.utils.VolumeCircle(max_length=len(self.volumes_ids))
            self.nodes_circle = Resources.utils.VolumeCircle(max_length=len(self.volumes_ids))

            for volume_id in self.volumes_ids:
                new_node = Resources.utils.VolumeNode(volume_id)
                self.nodes_circle_normal.add_volume_node(new_node)
                self.nodes_circle_plus.add_volume_node(new_node)
                self.nodes_circle.add_volume_node(new_node)

    def update_landmark_list_from_gui(self):
        self.current_landmarks_list = self.ui.SimpleMarkupsWidget.currentNode()

    def __create_shortcuts(self):
        """
        Function to create all shortcuts
        """

        self.shortcuts = [('d', lambda: Resources.utils_landmarks.activate_fiducial_placement()),  # fiducial placement
                          ('a', functools.partial(Resources.utils_views.change_view, self, "backward")),
                          ('s', functools.partial(Resources.utils_views.change_view, self, "forward")),
                          ('1', functools.partial(Resources.utils_views.change_foreground_opacity_discrete, self, 0.0)),
                          # change opacity to 0.0
                          ('2', functools.partial(Resources.utils_views.change_foreground_opacity_discrete, self, 0.5)),
                          # change opacity to 0.5
                          ('3', functools.partial(Resources.utils_views.change_foreground_opacity_discrete, self, 1.0)),
                          # change opacity to 1.0
                          ('q', functools.partial(Resources.utils_views.change_foreground_opacity_continuous, self, 0.02)),
                          # incr. op. by .01
                          ('w', functools.partial(Resources.utils_views.change_foreground_opacity_continuous, self, -0.02)),
                          # decr. op. by .01
                          ('z', functools.partial(Resources.utils_landmarks.jump_to_next_landmark, self, "backward")),
                          ('x', functools.partial(Resources.utils_landmarks.jump_to_next_landmark, self, "forward"))]

    def __initialiseShortcuts(self):
        """
    Function to initialise shortcuts created with __create_shortcuts()
    """

        self.__create_shortcuts()

        for (shortcutKey, callback) in self.shortcuts:
            shortcut = qt.QShortcut(slicer.util.mainWindow())
            shortcut.setKey(qt.QKeySequence(shortcutKey))
            shortcut.connect('activated()', callback)

    def onResetViewsButton(self):
        """
        Resets to the standard view when the reset button is clicked
        """
        try:

            # try to select nodes from selectors
            for selector in self.input_selectors:
                if selector.currentNode():
                    self.volumes_ids.append(selector.currentNode().GetID())

            # decide on slices to be updated depending on the view chosen
            current_views = Resources.utils_views.get_current_views(self)

            for view in current_views:
                layoutManager = slicer.app.layoutManager()
                view_logic = layoutManager.sliceWidget(view).sliceLogic()
                self.compositeNode = view_logic.GetSliceCompositeNode()

                volume_background = slicer.mrmlScene.GetNodeByID(self.volumes_ids[-1])
                volume_foreground = slicer.mrmlScene.GetNodeByID(self.volumes_ids[-2])

                self.compositeNode.SetBackgroundVolumeID(volume_background.GetID())
                self.compositeNode.SetForegroundVolumeID(volume_foreground.GetID())

            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

            # reset slice orientation
            sliceNodes = slicer.util.getNodesByClass("vtkMRMLSliceNode")
            sliceNodes[0].SetOrientationToAxial()
            sliceNodes[1].SetOrientationToCoronal()
            sliceNodes[2].SetOrientationToSagittal()

            # those below exist only if we have the 3o3 view
            if self.view == '3on3':
                sliceNodes[3].SetOrientationToAxial()
                sliceNodes[4].SetOrientationToCoronal()
                sliceNodes[5].SetOrientationToSagittal()

            # switch which button is enabled
            self.ui.view3o3Button.enabled = True
            self.ui.viewStandardButton.enabled = False

        except Exception as e:
            slicer.util.errorDisplay("Could not reset views - try manually. " + str(e))

    def onIntersectionButton(self):
        """
    Run processing when user clicks "Create intersection" button.
    """
        try:
            # Compute output
            self.logic.process([selector.currentNode() for selector in self.input_selectors if selector.currentNode()],
                               Resources.utils_views.get_current_views(self))

            Resources.utils_views.initialise_views(self)

        except Exception as e:
            slicer.util.errorDisplay("Failed to create intersection. " + str(e))

    def onThresholdButton(self):
        """
    Sets all lower thresholds of the US volumes to 1, so the black border disappears
    """
        # works only if us is somehwere in the file name
        try:
            threshold = 1

            # loop through all selected volumes
            for volume in [self.ui.inputSelector0.currentNode(),
                           self.ui.inputSelector1.currentNode(),
                           self.ui.inputSelector2.currentNode(),
                           self.ui.inputSelector3.currentNode(),
                           self.ui.inputSelector4.currentNode()]:

                if volume:  # we need to check if it is not none - nothing selected means the current node is none
                    current_name = volume.GetName()

                    if "us" in current_name.lower():
                        volNode = slicer.util.getNode(current_name)
                        dispNode = volNode.GetDisplayNode()
                        dispNode.ApplyThresholdOn()
                        dispNode.SetLowerThreshold(
                            threshold)  # 1 because we want to surrounding black pixels to disappear

        except Exception as e:
            slicer.util.errorDisplay("Failed to change lower thresholds. " + str(e))

    def onViewStandardButton(self):
        """
    Changes the view to standard
    """
        try:
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

            # set slice orientation
            sliceNodes = slicer.util.getNodesByClass("vtkMRMLSliceNode")
            sliceNodes[0].SetOrientationToAxial()
            sliceNodes[1].SetOrientationToCoronal()
            sliceNodes[2].SetOrientationToSagittal()

            self.ui.topRowCheck.toolTip = "Switch to 3-over-3 view to disable top row"
            self.ui.topRowCheck.enabled = False
            self.ui.topRowCheck.checked = True

            self.ui.bottomRowCheck.toolTip = "Switch to 3-over-3 view to enable bottom row"
            self.ui.bottomRowCheck.enabled = False
            self.ui.bottomRowCheck.checked = False

            self.view = 'normal'

            # set sync views button to disabled
            self.ui.syncViewsButton.enabled = False

            # disable the button and enable 3o3 button
            self.ui.view3o3Button.enabled = True
            self.ui.viewStandardButton.enabled = False

        except Exception as e:
            slicer.util.errorDisplay("Failed to change to standard view. " + str(e))

    def onView3o3Button(self):
        """
    CHanges the view to 3 over 3
    """
        try:
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutThreeOverThreeView)

            # set slice orientation
            sliceNodes = slicer.util.getNodesByClass("vtkMRMLSliceNode")
            sliceNodes[0].SetOrientationToAxial()
            sliceNodes[1].SetOrientationToCoronal()
            sliceNodes[2].SetOrientationToSagittal()
            sliceNodes[3].SetOrientationToAxial()
            sliceNodes[4].SetOrientationToCoronal()
            sliceNodes[5].SetOrientationToSagittal()

            Resources.utils_views.initialise_views(self)

            self.ui.topRowCheck.toolTip = "Activate top row"
            self.ui.topRowCheck.enabled = True
            self.ui.topRowCheck.checked = True

            self.ui.bottomRowCheck.toolTip = "Activate bottom row"
            self.ui.bottomRowCheck.enabled = True
            self.ui.bottomRowCheck.checked = False

            self.view = '3on3'

            # set sync views button to enabled
            self.ui.syncViewsButton.enabled = True

            # disable the button and enable normal button
            self.ui.view3o3Button.enabled = False
            self.ui.viewStandardButton.enabled = True

        except Exception as e:
            slicer.util.errorDisplay("Failed to change to 3 over 3 view. " + str(e))

    def onSwitchOrderButton(self):
        """
    Changes the order in which the volumes are displayed
    """
        try:

            self.switch = not self.switch

            # reverse order of names
            self.volumes_ids.reverse()

            # switch views
            current_views = Resources.utils_views.get_current_views(self)

            for view in current_views:
                layoutManager = slicer.app.layoutManager()
                view_logic = layoutManager.sliceWidget(view).sliceLogic()
                self.compositeNode = view_logic.GetSliceCompositeNode()

                current_background_id = self.compositeNode.GetBackgroundVolumeID()
                current_foreground_id = self.compositeNode.GetForegroundVolumeID()

                self.compositeNode.SetBackgroundVolumeID(current_foreground_id)
                self.compositeNode.SetForegroundVolumeID(current_background_id)

            # Resources.utils_views.initialise_views(self)

        except Exception as e:
            slicer.util.errorDisplay("Failed to change the display order. " + str(e))

    def onSyncViewsButton(self):
        """
    Sync all views in the 3o3 view
    """

        # set lower row volumes to those of the upper view
        if self.view == '3on3':  # if it is 3on3, we want it to update all slices

            layoutManager = slicer.app.layoutManager()

            for i in range(3):
                view_logic_normal = layoutManager.sliceWidget(self.views_normal[i]).sliceLogic()
                compositeNode_normal = view_logic_normal.GetSliceCompositeNode()
                view_logic_plus = layoutManager.sliceWidget(self.views_plus[i]).sliceLogic()
                compositeNode_plus = view_logic_plus.GetSliceCompositeNode()

                # change volumes to those from the top row
                background_normal_id = compositeNode_normal.GetBackgroundVolumeID()
                foreground_normal_id = compositeNode_normal.GetForegroundVolumeID()

                compositeNode_plus.SetBackgroundVolumeID(background_normal_id)
                compositeNode_plus.SetForegroundVolumeID(foreground_normal_id)

                # change foreground opacities to those from the top row
                compositeNode_plus.SetForegroundOpacity(compositeNode_normal.GetForegroundOpacity())

                # update offset (sometimes when updating rows, they are updated to the wrong offset)
                view_logic_plus.SetSliceOffset(view_logic_normal.GetSliceOffset())

            # link rest of funcitonality
            self.topRowActive = True
            self.bottomRowActive = True
            Resources.utils_views.active_rows_update(self)

    def onUpdateFlow(self):

        try:

            # delete old curve nodes
            for curve_node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode"):
                slicer.mrmlScene.RemoveNode(curve_node)
            self.curve_nodes = {}

            fiducial_nodes = Resources.utils_landmarks.divide_landmarks_by_volume(self)
            max_len = max([len(i) for i in fiducial_nodes])

            # create curve nodes
            for i in range(max_len):
                self.curve_nodes[i] = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode")

            # loop through all curve nodes and add points
            for index, curve_node_id in self.curve_nodes.items():

                all_points = []

                if len(fiducial_nodes[0]) > 0:
                    all_points.append(fiducial_nodes[0][index][0])
                if len(fiducial_nodes[1]) > 0:
                    all_points.append(fiducial_nodes[1][index][0])
                if len(fiducial_nodes[2]) > 0:
                    all_points.append(fiducial_nodes[2][index][0])
                if len(fiducial_nodes[3]) > 0:
                    all_points.append(fiducial_nodes[3][index][0])
                if len(fiducial_nodes[4]) > 0:
                    all_points.append(fiducial_nodes[4][index][0])

                all_points = np.asarray(all_points)

                slicer.util.updateMarkupsControlPointsFromArray(curve_node_id, all_points)

                Resources.utils.markup_curve_adjustment(curve_node_id)

            # change tool to pointer
            interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
            interactionNode.SwitchToViewTransformMode()
            # also turn off place mode persistence if required
            interactionNode.SetPlaceModePersistence(0)

        except Exception as e:
            slicer.util.errorDisplay("Could not update flow.\n" + str(e))

    def onTopRowCheck(self, activate=True):
        """
        Updates the top row
        :param activate: Boolean value to define if row is activated
        """
        self.topRowActive = activate
        Resources.utils_views.active_rows_update(self)

    def onBottomRowCheck(self, activate=False):
        """
        Updates the bottom row
        :param activate: Boolean value to define if row is activated
        """
        self.bottomRowActive = activate
        Resources.utils_views.active_rows_update(self)

    def onLabelVisCheck(self, activate=True):

        try:
            previous_state = not self.ui.labelVisCheck.checked
            Resources.utils_landmarks.check_if_landmark_list_is_selected(self)

            for i in range(self.current_landmarks_list.GetNumberOfControlPoints()):
                self.current_landmarks_list.SetNthControlPointVisibility(i, activate)

        except Exception as e:
            self.ui.labelVisCheck.checked = previous_state  # assign previous checked state
            slicer.util.errorDisplay("Could not change label visibility.\n" + str(e))

    def onAcceptedLandmarkCheck(self, activate=True):
        try:
            if activate is True:
                Resources.utils_landmarks.set_landmark_status(self, "Accepted")
                self.ui.modifyLandmarkCheck.checked = False
                self.ui.rejectedLandmarkCheck.checked = False

            if activate is False:
                Resources.utils_landmarks.set_landmark_status(self, "")

        except Exception as e:
            slicer.util.errorDisplay("Could not change landmark status.\n" + str(e))

    def onModifyLandmarkCheck(self, activate=True):
        try:
            if activate is True:
                Resources.utils_landmarks.set_landmark_status(self, "Modify")
                self.ui.acceptedLandmarkCheck.checked = False
                self.ui.rejectedLandmarkCheck.checked = False

            if activate is False:
                Resources.utils_landmarks.set_landmark_status(self, "")

        except Exception as e:
            slicer.util.errorDisplay("Could not change landmark status.\n" + str(e))

    def onRejectedLandmarkCheck(self, activate=True):
        try:
            if activate is True:
                Resources.utils_landmarks.set_landmark_status(self, "Rejected")
                self.ui.modifyLandmarkCheck.checked = False
                self.ui.acceptedLandmarkCheck.checked = False

            if activate is False:
                Resources.utils_landmarks.set_landmark_status(self, "")

        except Exception as e:
            slicer.util.errorDisplay("Could not change landmark status.\n" + str(e))

    def onPrintResultsButton(self):
        try:
            Resources.utils_landmarks.print_landmark_inspection_results(self)

        except Exception as e:
            slicer.util.errorDisplay("Could not print results.\n" + str(e))

    def onSortLandmarksButton(self):
        try:
            Resources.utils_landmarks.sort_landmarks(self)

        except Exception as e:
            slicer.util.errorDisplay("Could not sort landmarks.\n" + str(e))

    def onMisc1Button(self):
        try:
            Resources.utils_landmarks.jump_to_next_landmark(self, "forward")

        except Exception as e:
            slicer.util.errorDisplay("Could not misc1.\n" + str(e))

    def onMisc2Button(self):
        try:
            Resources.utils_landmarks.jump_to_next_landmark(self, "backward")

        except Exception as e:
            slicer.util.errorDisplay("Could not misc2.\n" + str(e))

#
# MRUSLandmarkingLogic
#

class MRUSLandmarkingLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def __init__(self):
        """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
        ScriptedLoadableModuleLogic.__init__(self)

    @staticmethod
    def setup_segment_editor(segmentationNode=None, volumeNode=None):
        """
    Runs standard setup of segment editor widget and segment editor node
    :param segmentationNode a seg node you can also pass
    :param volumeNode a volume node you can pass
    """

        if segmentationNode is None:
            # Create segmentation node
            segmentationNode = slicer.vtkMRMLSegmentationNode()
            slicer.mrmlScene.AddNode(segmentationNode)
            segmentationNode.CreateDefaultDisplayNodes()

        segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
        segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
        segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
        slicer.mrmlScene.AddNode(segmentEditorNode)
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(segmentationNode)
        segmentEditorWidget.setMRMLScene(slicer.mrmlScene)

        if volumeNode:
            segmentEditorWidget.setMasterVolumeNode(volumeNode)

        return segmentEditorWidget, segmentEditorNode, segmentationNode

    def process(self, volumes=None, current_views=None):
        """
    Creates the intersection of the us volumes and displays it as an outline
    """

        if volumes is None and current_views is None:
            return

        if current_views is None:
            current_views = ["Red", "Green", "Yellow"]

        # save current background and foreground (because changing the master volume twice changes the back-/foregrounds
        layoutManager = slicer.app.layoutManager()
        view_logic = layoutManager.sliceWidget(current_views[0]).sliceLogic()
        self.compositeNode = view_logic.GetSliceCompositeNode()
        current_background_id = self.compositeNode.GetBackgroundVolumeID()
        current_foreground_id = self.compositeNode.GetForegroundVolumeID()

        import time
        startTime = time.time()
        logging.info('Processing started')

        usVolumes = []
        for volume in volumes:
            matches = ["us1", "us2", "us3", "us4", "us5", "us6"]
            if any(x in volume.GetName().lower() for x in matches):
                usVolumes.append(volume)

        if len(usVolumes) <= 1:
            slicer.util.errorDisplay(
                "Select at least two US volumes (intersection is only calculated for US volumes). (They"
                "need to contain us1, us2, us3, us4, us5 or us6 in their names")
            return

        # initialise segment editor
        segmentEditorWidget, segmentEditorNode, segmentationNode = self.setup_segment_editor()

        addedSegmentID = []

        # for each volume create a threshold segmentation
        for idx, volume in enumerate(usVolumes):
            segmentEditorWidget.setMasterVolumeNode(volume)

            # Create segment
            addedSegmentID.append(segmentationNode.GetSegmentation().AddEmptySegment())
            segmentEditorNode.SetSelectedSegmentID(addedSegmentID[idx])

            # Fill by thresholding
            segmentEditorWidget.setActiveEffectByName("Threshold")
            effect = segmentEditorWidget.activeEffect()
            effect.setParameter("MinimumThreshold", "1")
            effect.setParameter("MaximumThreshold", "255")
            effect.self().onApply()

        # set background and foreground in all views
        for view in current_views:
            layoutManager = slicer.app.layoutManager()
            view_logic = layoutManager.sliceWidget(view).sliceLogic()
            self.compositeNode = view_logic.GetSliceCompositeNode()
            self.compositeNode.SetBackgroundVolumeID(current_background_id)
            self.compositeNode.SetForegroundVolumeID(current_foreground_id)

        # https://slicer.readthedocs.io/en/latest/developer_guide/modules/segmenteditor.html#effect-parameters
        # https://discourse.slicer.org/t/how-to-programmatically-use-logical-operator-add-function-from-segment-editor/16581/2
        # https://discourse.slicer.org/t/how-to-change-the-slice-fill-in-segmentations-in-a-python-script/20871/2
        # Display settings are stored in the display node
        intersection_segment_id = segmentationNode.GetSegmentation().AddEmptySegment()
        segmentEditorNode.SetSelectedSegmentID(intersection_segment_id)
        segmentEditorWidget.setActiveEffectByName("Logical operators")
        effect = segmentEditorWidget.activeEffect()

        # add first segmentations
        effect.setParameter("Operation", SegmentEditorEffects.LOGICAL_UNION)

        effect.setParameter("ModifierSegmentID", addedSegmentID[0])
        effect.self().onApply()

        # intersect with the next two segmentations
        effect.setParameter("Operation", SegmentEditorEffects.LOGICAL_INTERSECT)

        for id in addedSegmentID:
            effect.setParameter("ModifierSegmentID", id)
            effect.self().onApply()

            # remove segments
            segmentationNode.RemoveSegment(id)

        # display only outline
        # https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html#modify-segmentation-display-options
        # http://apidocs.slicer.org/master/classvtkMRMLSegmentationDisplayNode.html#afeca62a2a79513ab275db3840136709c
        segmentation = slicer.mrmlScene.GetNodeByID(segmentationNode.GetID())
        displayNode = segmentation.GetDisplayNode()
        displayNode.SetSegmentOpacity2DFill(intersection_segment_id, 0.0)  # Set fill opacity of a single segment
        displayNode.SetSegmentOpacity2DOutline(intersection_segment_id, 1.0)  # Set outline opacity of a single segment

        stopTime = time.time()
        logging.info('Processing completed in {0:.2f} seconds'.format(stopTime - startTime))


#
# MRUSLandmarkingTest
#
#
class MRUSLandmarkingTest(ScriptedLoadableModuleTest):
    """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
    """
        self.setUp()
        self.test_MRUSLandmarking1()

    def test_MRUSLandmarking1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

        self.delayDisplay("Starting the test")

        logic = MRUSLandmarkingLogic()

        logic.process(None, None)

        self.delayDisplay('Test passed')
