import unittest
import numpy as np
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import SegmentEditorEffects
import functools

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
    # TODO: update with short description of the module and a link to online module documentation
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

    self.__linkViews()

    self.compositeNode = None
    self.volumes_ids = None

    # variable saying if views in 3-over-3 are linked or not
    self.topRowActive = True
    self.bottomRowActive = False
    self.view = 'normal'
    self.views_normal = ["Red", "Green", "Yellow"]
    self.views_plus = ["Red+", "Green+", "Yellow+"]

    self.automatic_assignment = False

    self.switch = False

    self.fiducial_nodes = {}  # a dict that will contain all fiducial node ids and their corresponding volume ids
    self.curve_nodes = {}  # a dict that will contain all curve node ids and their corresponding fiducial index
    self.landmarks = {}  # dict that stores all the landmarks (key is the index, value is the []x3 array of points

    # used for updating the correct row when rows are linked
    # self.changing = "bottom"

    # for switching between markup control points
    self.current_control_point_idx = 0

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
    self.ui.updateFlow.enabled = False
    self.ui.updateFlow.toolTip = "Automatic landmark assignment needs to be checked (the flow will work only on the new" \
                                 "automatically assigned set of landmarks (because of the naming scheem))"

    # Check boxes
    # Activate rows
    self.ui.topRowCheck.connect('clicked(bool)', self.onTopRowCheck)
    self.ui.bottomRowCheck.connect('clicked(bool)', self.onBottomRowCheck)

    # automatic landmark assignment
    self.ui.automaticLandmarks.connect('clicked(bool)', self.onAutomaticLandmarks)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

    # shortcuts
    self.__initialiseShortcuts()  # those that depend on the volumes - they have to be defined in this class,
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
    us_volumes = ["3D AX T2 SPACE Pre-op Thin-cut",
                  "US1 Pre-dura", "US2 Post-dura", "US3 Resection Control",
                  "3D SAG T2 SPC FLAIR Intra-op Thin-cut"]

    # only select default nodes when nothing is selected (otherwise changing modules back and forth triggers this)
    chosen_nodes = [selector.currentNode() for selector in self.input_selectors]
    # nothing is selected means that we have only None in the list
    if not any(chosen_nodes):
      for input_volume, volume_name in zip(input_volumes, us_volumes):
        if not self._parameterNode.GetNodeReference(input_volume):
          volumeNode = slicer.mrmlScene.GetFirstNodeByName(volume_name)
          if volumeNode:
            self._parameterNode.SetNodeReferenceID(input_volume, volumeNode.GetID())

    # update chosen volumes
    self.volumes_ids = []

    for selector in self.input_selectors:
      if selector.currentNode():
        self.volumes_ids.append(selector.currentNode().GetID())

    self.ui.topRowCheck.toolTip = "Switch to 3-over-3 view to disable top row"
    self.ui.bottomRowCheck.toolTip = "Switch to 3-over-3 view to enable bottom row"
    self.ui.automaticLandmarks.toolTip = "Automatically assign landmarks to lists based on the current volume"

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

    self._parameterNode.EndModify(wasModified)

    # update volumes
    self.volumes_ids = []

    for selector in self.input_selectors:
      if selector.currentNode():
        self.volumes_ids.append(selector.currentNode().GetID())

  def get_next_combination(self, current_volume_ids=None, direction="forward"):
    """
    Used for the shortcut to loop through the volumes. The idea is that always two consecutive images are overlayed. If
    we have images [A,B,C,D] then if we start with images [A,B] the next combination will b [B,C] etc. This function
    gets the current volume IDs and the switching direction as inputs and returns the next volume IDs.
    :param current_volume_ids: Two currently displayed volumes
    :param direction: The direction in which the switching will occur
    :return: The next two IDs which should be displayed
    """

    if not self.volumes_ids or not current_volume_ids:
      return None
    if direction not in ["forward", "backward"]:
      return None

    forward_combinations = []
    backward_combinations = []
    next_index = None

    # create list of possible forward pairs
    for i in range(len(self.volumes_ids)):
      if i == len(self.volumes_ids) - 1:
        index1 = len(self.volumes_ids) - 1
        index2 = 0
      else:
        index1 = i
        index2 = i + 1

      forward_combinations.append([self.volumes_ids[index1], self.volumes_ids[index2]])
      backward_combinations.append([self.volumes_ids[index2], self.volumes_ids[index1]])

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

    if self.switch and direction == "forward":
      direction = "backward"
    elif self.switch and direction == "backward":
      direction = "forward"

    if direction == "forward":
      if current_index == len(self.volumes_ids) - 1:
        next_index = 0
      else:
        next_index = current_index + 1

    elif direction == "backward":
      if current_index == 0:
        next_index = len(self.volumes_ids) - 1
      else:
        next_index = current_index - 1

    return combinations[next_index]

  def get_current_views(self):
    """
    Function to determine currently active views (slices) ('active' means the ones for which all the functionality
    applies)
    return: An array of current views
    """
    # both rows or no rows active in 3o3
    if self.topRowActive and self.bottomRowActive and self.view == '3on3':
      current_views = self.views_normal + self.views_plus

    elif (not self.topRowActive) and (not self.bottomRowActive) and self.view == '3on3':
      current_views = self.views_normal + self.views_plus

    # bottom row active in 3o3
    elif not self.topRowActive and self.bottomRowActive and self.view == '3on3':
      current_views = self.views_plus

    # all other times we only care about the top row (views_normal)
    else:
      current_views = self.views_normal

    return current_views

  def __initialise_views(self):
    """
    Initialise views with volumes. It only changes volumes if the currently displayed volumes are not in the list of
    chosen volumes.
    :return the composite node that can be used by the __change_view() function
    """
    # decide on slices to be updated depending on the view chosen
    current_views = self.get_current_views()

    update = False

    for view in current_views:

      layoutManager = slicer.app.layoutManager()
      view_logic = layoutManager.sliceWidget(view).sliceLogic()
      self.compositeNode = view_logic.GetSliceCompositeNode()

      current_background_id = self.compositeNode.GetBackgroundVolumeID()
      current_foreground_id = self.compositeNode.GetForegroundVolumeID()

      # check if there is a background
      if current_background_id is not None:

        # if it's not the correct volume, set the background and foreground
        if current_background_id not in self.volumes_ids:
          # update volumes
          update = True

      else:  # there is no background
        # update volumes
        update = True

      if update:
        self.compositeNode.SetBackgroundVolumeID(self.volumes_ids[1])
        self.compositeNode.SetForegroundVolumeID(self.volumes_ids[0])
        update = False

      # check if there is a foreground
      if current_foreground_id is not None:

        # if it's not the correct volume, set the background and foreground
        if current_foreground_id not in self.volumes_ids:
          # update volumes
          update = True

      else:  # there is no foreground
        # update volumes
        update = True

      if update:
        self.compositeNode.SetBackgroundVolumeID(self.volumes_ids[1])
        self.compositeNode.SetForegroundVolumeID(self.volumes_ids[0])
        update = False

  def __change_view(self, direction='forward'):
    """
    (This function is used as a shortcut)
    Change the view forward or backward (take the list of possible volumes and for the two displayed volumes increase
    their index by one) using the get_current_views() function
    :param direction: The direction in which the volumes are switched
    """

    if self.ui.inputSelector0.currentNode() is None and\
       self.ui.inputSelector1.currentNode() is None and\
       self.ui.inputSelector2.currentNode() is None and\
       self.ui.inputSelector3.currentNode() is None and\
       self.ui.inputSelector4.currentNode() is None:
      slicer.util.errorDisplay("Not enough volumes given for the volume switching shortcut (choose all in the 'Common "
                               "field of view'")
      return
    
    if direction not in ['forward', 'backward']:
      slicer.util.errorDisplay("Not enough volumes given for the volume switching shortcut (choose all in the 'Common "
                               "field of view'")
      return

    self.__initialise_views()

    current_views = self.get_current_views()

    for view in current_views:
      layoutManager = slicer.app.layoutManager()
      view_logic = layoutManager.sliceWidget(view)
      view_logic = view_logic.sliceLogic()
      self.compositeNode = view_logic.GetSliceCompositeNode()

      # get current foreground and background volumes
      current_foreground_id = self.compositeNode.GetForegroundVolumeID()
      current_background_id = self.compositeNode.GetBackgroundVolumeID()

      # switch backgrounds
      if direction == 'forward':
        next_combination = self.get_next_combination([current_foreground_id, current_background_id], "forward")

      else:
        next_combination = self.get_next_combination([current_foreground_id, current_background_id], "backward")

      volume_foreground = slicer.mrmlScene.GetNodeByID(next_combination[0])
      volume_background = slicer.mrmlScene.GetNodeByID(next_combination[1])

      # update volumes (if they both exist)
      if volume_foreground and volume_background:
        if direction == 'backward' or direction == 'forward':
          self.compositeNode.SetBackgroundVolumeID(volume_background.GetID())
          self.compositeNode.SetForegroundVolumeID(volume_foreground.GetID())

        else:
          slicer.util.errorDisplay("wrong direction")
      else:
        slicer.util.errorDisplay("No volumes to set for foreground and background")

      # rotate slices to lowest volume (otherwise the volumes can be missaligned a bit
      # slicer.app.layoutManager().sliceWidget(view).sliceController().rotateSliceToLowestVolumeAxes()

  def __change_foreground_opacity_discrete(self, new_opacity=0.5):
    """
    (This function is used as a shortcut)
    Changes the foreground opacity to a given value.
    :param new_opacity: The new foreground opacity

    """
    layoutManager = slicer.app.layoutManager()

    current_views = self.get_current_views()

    # iterate through all views and set opacity to
    for sliceViewName in current_views:
      view = layoutManager.sliceWidget(sliceViewName).sliceView()
      sliceNode = view.mrmlSliceNode()
      sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
      compositeNode = sliceLogic.GetSliceCompositeNode()
      compositeNode.SetForegroundOpacity(new_opacity)

  def __change_foreground_opacity_continuous(self, opacity_change=0.01):
    """
    (This function is used as a shortcut)
    Increases or decreases the foreground opacity by a given value
    :param opacity_change: The change in foreground opacity
    """

    layoutManager = slicer.app.layoutManager()

    current_views = self.get_current_views()

    # iterate through all views and set opacity to
    for sliceViewName in current_views:
      view = layoutManager.sliceWidget(sliceViewName).sliceView()
      sliceNode = view.mrmlSliceNode()
      sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
      compositeNode = sliceLogic.GetSliceCompositeNode()
      compositeNode.SetForegroundOpacity(compositeNode.GetForegroundOpacity() + opacity_change)

  def __jump_to_next_landmark(self, direction="forward"):
    """
    (This function is used as a shortcut)
    Jumps through all set landmarks.
    :param direction: The direction in which the landmarks are switched
    """
    # get markup node
    try:
      selectionNode = slicer.app.applicationLogic().GetSelectionNode()
      activeNodeID = selectionNode.GetActivePlaceNodeID()
      x = slicer.mrmlScene.GetNodeByID(activeNodeID)

    except Exception as e:
      slicer.util.errorDisplay("Create landmarks (control points) before trying to switch between them. The landmarks "
                               "list has to be named 'F'" + str(e))

    # get amount of control points
    control_points_amount = x.GetNumberOfControlPoints()

    # if there are 0 control points
    if control_points_amount == 0:
      slicer.util.errorDisplay("Create landmarks (control points) before trying to switch between them")
      return

    # increase or decrease index according to direction
    if direction == "forward":
      self.current_control_point_idx += 1

      # if it's too big, circle back to 0-th index
      if self.current_control_point_idx >= control_points_amount:
        self.current_control_point_idx = 0

    elif direction == "backward":
      self.current_control_point_idx -= 1

      # if it's too small start ath the last index again
      if self.current_control_point_idx < 0:
        self.current_control_point_idx = control_points_amount - 1

    else:  # wrong direction
      slicer.util.errorDisplay("Wrong switching direction (error in code).")
      return

    # get n-th control point vector
    pos = x.GetNthControlPointPositionVector(self.current_control_point_idx)

    # center views on current control point
    slicer.modules.markups.logic().JumpSlicesToLocation(pos[0], pos[1], pos[2], False, 0)

    # center crosshair on current control point
    crosshairNode = slicer.util.getNode("Crosshair")
    crosshairNode.SetCrosshairRAS(pos)
    crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowBasic)  # make it visible

  def __get_max_amount_of_fiducials(self):
    """
    Get the maximum number of landmarks stored in all fiducial nodes (that's how many curves need to exist)
    :return: The maximum
    """

    max_amount = 0
    try:
      # loop through all fiducial nodes
      for key, value in self.fiducial_nodes.items():
        # for each node, add all points to the control curve
        pointListNode = slicer.mrmlScene.GetNodeByID(value)
        numControlPoints = pointListNode.GetNumberOfControlPoints()

        if numControlPoints > max_amount:
          max_amount = numControlPoints

      return max_amount

    except:
      return 0

  def __create_all_fiducial_nodes(self):
    """
    Creates all fiducial nodes (one for each volume) (or updates the existing one)
    """

    # for volume_id in self.volumes_ids:
    #   volume.GetName()

    fiducial_names = ["M1__f", "U1__f", "U2__f", "U3__f", "M2__f"]

    for name, volume in zip(fiducial_names, [self.ui.inputSelector0.currentNode(),
                                              self.ui.inputSelector1.currentNode(),
                                              self.ui.inputSelector2.currentNode(),
                                              self.ui.inputSelector3.currentNode(),
                                              self.ui.inputSelector4.currentNode()]):

      if volume:  # we need to check if it is not none - nothing selected means the current node is none
        fiducial_name = name

        if not slicer.mrmlScene.GetFirstNodeByName(fiducial_name):  # if the fiducial node does not exist
          # create it and append the voume id and the fiducial id
          self.fiducial_nodes[volume.GetID()] = slicer.modules.markups.logic().AddNewFiducialNode(fiducial_name)
          # self.curve_nodes[self.fiducial_nodes[volume.GetID()]] = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode")

  def __create_all_curve_nodes(self):
    """
    Creates as many curve nodes as there are fiducials in the longest list
    """
    max_points = self.__get_max_amount_of_fiducials()

    for i in range(len(self.curve_nodes), max_points):  # add the difference in points
      self.curve_nodes[i + 1] = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode")

  def __activate_fiducial_node(self):
    """
    Function to activate the correct fiducial node. If the foreground opacity is bigger than 0, set the fiducial to the
    node corresponding to the foreground node, otherwise set it to the node corresponding to the background node
    """

    # for now we only consider top row

    # get background and foreground IDs
    layoutManager = slicer.app.layoutManager()
    view_logic = layoutManager.sliceWidget("Red").sliceLogic()
    compositeNode = view_logic.GetSliceCompositeNode()

    background_id = compositeNode.GetBackgroundVolumeID()
    foreground_id = compositeNode.GetForegroundVolumeID()

    # get foreground opacity
    foreground_opacity = compositeNode.GetForegroundOpacity()

    # get appropriate fiducial node (or create if it does not exist)

    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")

    if foreground_opacity > 0 and foreground_id:  # then activate the foreground fiducial node, else the background
      pointListNode = slicer.mrmlScene.GetNodeByID(self.fiducial_nodes[foreground_id])
    elif background_id:
      pointListNode = slicer.mrmlScene.GetNodeByID(self.fiducial_nodes[background_id])
    else:
      pointListNode = None


    if pointListNode:
      selectionNode.SetActivePlaceNodeID(pointListNode.GetID())

  def __markup_curve_adjustment(self, curve_node_id):
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

  def __fiducials(self):
    """
    Entire fiducial logic - create list, activate appropriate list and set the placement widget
    """
    slicer.modules.markups.logic().StartPlaceMode(0)

    if self.automatic_assignment == True:
      self.__create_all_fiducial_nodes()
      self.__activate_fiducial_node()

    # set control point visibility off in 3D
    for fiducial_node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode"):
      d = fiducial_node.GetDisplayNode()
      d.Visibility3DOff()

  def __create_shortcuts(self):
    """
    Function to create all shortcuts
    """

    self.shortcuts = [('d', lambda: self.__fiducials()),  # fiducial placement
                      ('a', functools.partial(self.__change_view, "backward")),  # volume switching dir1
                      ('s', functools.partial(self.__change_view, "forward")),  # volume switching dir2
                      ('1', functools.partial(self.__change_foreground_opacity_discrete, 0.0)),  # change opacity to 0.0
                      ('2', functools.partial(self.__change_foreground_opacity_discrete, 0.5)),  # change opacity to 0.5
                      ('3', functools.partial(self.__change_foreground_opacity_discrete, 1.0)),  # change opacity to 1.0
                      ('q', functools.partial(self.__change_foreground_opacity_continuous, 0.02)),  # incr. op. by .01
                      ('w', functools.partial(self.__change_foreground_opacity_continuous, -0.02)),  # decr. op. by .01
                      ('z', functools.partial(self.__jump_to_next_landmark, "backward")),
                      ('x', functools.partial(self.__jump_to_next_landmark, "forward"))]

  def __initialiseShortcuts(self):
    """
    Function to initialise shortcuts created with __create_shortcuts()
    """

    self.__create_shortcuts()

    for (shortcutKey, callback) in self.shortcuts:
      shortcut = qt.QShortcut(slicer.util.mainWindow())
      shortcut.setKey(qt.QKeySequence(shortcutKey))
      shortcut.connect('activated()', callback)

  def __linkViews(self):
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

  def onResetViewsButton(self):
    """
    Resets to the standard view when the reset button is clicked
    """
    try:
      # decide on slices to be updated depending on the view chosen
      current_views = self.get_current_views()

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
                         self.get_current_views())

      self.__initialise_views()

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
            dispNode.SetLowerThreshold(threshold)  # 1 because we want to surrounding black pixels to disappear

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

      self.__initialise_views()

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
      current_views = self.get_current_views()

      for view in current_views:
        layoutManager = slicer.app.layoutManager()
        view_logic = layoutManager.sliceWidget(view).sliceLogic()
        self.compositeNode = view_logic.GetSliceCompositeNode()

        current_background_id = self.compositeNode.GetBackgroundVolumeID()
        current_foreground_id = self.compositeNode.GetForegroundVolumeID()

        self.compositeNode.SetBackgroundVolumeID(current_foreground_id)
        self.compositeNode.SetForegroundVolumeID(current_background_id)

      # self.__initialise_views()

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
      self.activeRowsUpdate()

  def onUpdateFlow(self):
    """
    Everytime a new fiducial is placed, add it to the 3D view flow. Corresponding landmarks are connected with a line
    that should show the deformation over time (from volume to volume). The flow should be 'sensible'
    """
    # delete old curve nodes
    try:
      for curve_node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode"):
        slicer.mrmlScene.RemoveNode(curve_node)
      self.curve_nodes = {}
      self.landmarks = {}
    except Exception as e:
      print(e)

    # create curve nodes again
    self.__create_all_curve_nodes()

    # loop through all fiducial nodes
    for key, value in self.fiducial_nodes.items():
      # for each node, add all points to the control curve
      pointListNode = slicer.mrmlScene.GetNodeByID(value)
      numControlPoints = pointListNode.GetNumberOfControlPoints()
      positions = []
      for i in range(1, numControlPoints + 1):  # we start at 1 because that's how slicer numbers landmarks
        vector = pointListNode.GetNthControlPointPositionVector(i - 1)

        # create entry in landmark dict
        if i not in self.landmarks:
          self.landmarks[i] = []
        self.landmarks[i].append([vector.GetX(), vector.GetY(), vector.GetZ()])
        # positions.append([vector.GetX(), vector.GetY(), vector.GetZ()])

    for index, curve_node_id in self.curve_nodes.items():
      positions = np.asarray(self.landmarks[index])

      slicer.util.updateMarkupsControlPointsFromArray(curve_node_id, positions)

      self.__markup_curve_adjustment(curve_node_id)

  def activeRowsUpdate(self):
    """
    Updates the previously inactive row of slices (views) to the previously active - so that they are synced
    """
    try:
      if self.topRowActive and not self.bottomRowActive:
        group_normal = 0
        group_plus = 1
      elif not self.topRowActive and self.bottomRowActive:
        group_normal = 1
        group_plus = 0
      else:  # when both are checked or unchecked
        group_normal = 0
        group_plus = 0

        # unchecked means that we can check them again, as both unchecked doesn't make sense
        self.topRowActive = True
        self.bottomRowActive = True

        self.ui.topRowCheck.checked = True
        self.ui.bottomRowCheck.checked = True

      # set groups
      for i in range(3):
        slicer.app.layoutManager().sliceWidget(self.views_normal[i]).mrmlSliceNode().SetViewGroup(group_normal)
        slicer.app.layoutManager().sliceWidget(self.views_plus[i]).mrmlSliceNode().SetViewGroup(group_plus)

    except Exception as e:
      slicer.util.errorDisplay("Could not change active row(s). " + str(e))

  def onTopRowCheck(self, activate=True):
    """
    Updates the top row
    :param activate: Boolean value to define if row is activated
    """
    self.topRowActive = activate
    self.activeRowsUpdate()

  def onBottomRowCheck(self, activate=False):
    """
    Updates the bottom row
    :param activate: Boolean value to define if row is activated
    """
    self.bottomRowActive = activate
    self.activeRowsUpdate()

  def onAutomaticLandmarks(self, activate=False):
    self.automatic_assignment = activate

    if activate:
      self.ui.updateFlow.enabled = True

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
      slicer.util.errorDisplay("Select at least two US volumes (intersection is only calculated for US volumes). (They"
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
    logging.info('Processing completed in {0:.2f} seconds'.format(stopTime-startTime))

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
