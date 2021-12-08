import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import SegmentEditorEffects
import functools

#
# LandmarkingView
#

class LandmarkingView(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "LandmarkingView"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    See more information in <a href="https://github.com/organization/projectname#LandmarkingView">module documentation</a>.
    """
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
    """

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", registerSampleData)

    # create environment for the extension (link views and shortcuts)
    extension_environment = ExtensionEnvironment()

    slicer.app.connect("startupCompleted()", extension_environment.initialiseShortcuts)  # shortcuts that don't depend on the chosen volumes


#
# Register sample data sets in Sample Data module
#


def registerSampleData():
  """
  Add data sets to Sample Data module.
  """
  # It is always recommended to provide sample data for users to make it easy to try the module,
  # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

  import SampleData
  iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

  # To ensure that the source code repository remains small (can be downloaded and installed quickly)
  # it is recommended to store data sets that are larger than a few MB in a Github release.

  # LandmarkingView1
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='LandmarkingView',
    sampleName='LandmarkingView1',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'LandmarkingView1.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
    fileNames='LandmarkingView1.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
    # This node name will be used when the data set is loaded
    nodeNames='LandmarkingView1'
  )

  # LandmarkingView2
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='LandmarkingView',
    sampleName='LandmarkingView2',
    thumbnailFileName=os.path.join(iconsPath, 'LandmarkingView2.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
    fileNames='LandmarkingView2.nrrd',
    checksums = 'SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
    # This node name will be used when the data set is loaded
    nodeNames='LandmarkingView2'
  )

#
# LandmarkingViewWidget
#

class LandmarkingViewWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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

    ExtensionEnvironment.linkViews()

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/LandmarkingView.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = LandmarkingViewLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # TODO add default us volumes like in original extenision
    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.inputSelector1.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.inputSelector2.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.inputSelector3.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

    # Buttons
    # create intersection outline
    self.ui.intersectionButton.connect('clicked(bool)', self.onIntersectionButton)
    # set foreground threshold to 1 for all chosen volumes
    self.ui.thresholdButton.connect('clicked(bool)', self.onThresholdButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

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
    if not self._parameterNode.GetNodeReference("InputVolume"):
      firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
      if firstVolumeNode:
        self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

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

    # Update node selectors and sliders
    self.ui.inputSelector1.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume1"))
    self.ui.inputSelector2.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume2"))
    self.ui.inputSelector3.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume3"))

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

    self._parameterNode.SetNodeReferenceID("InputVolume1", self.ui.inputSelector1.currentNodeID)
    self._parameterNode.SetNodeReferenceID("InputVolume2", self.ui.inputSelector2.currentNodeID)
    self._parameterNode.SetNodeReferenceID("InputVolume3", self.ui.inputSelector3.currentNodeID)

    self._parameterNode.EndModify(wasModified)

  def onIntersectionButton(self):
    """
    Run processing when user clicks "Create intersection" button.
    """
    try:
      # Compute output
      self.logic.process(self.ui.inputSelector1.currentNode(),
                         self.ui.inputSelector2.currentNode(),
                         self.ui.inputSelector3.currentNode())

      self.__initialise_views()

    except:
      pass

  def onThresholdButton(self):
    try:
      threshold=1

      # loop through all selected volumes
      for volume in [self.ui.inputSelector1.currentNode(),
                     self.ui.inputSelector2.currentNode(),
                     self.ui.inputSelector3.currentNode()]:

        current_name = volume.GetName()

        volNode = slicer.util.getNode(current_name)
        dispNode = volNode.GetDisplayNode()
        dispNode.ApplyThresholdOn()
        dispNode.SetLowerThreshold(threshold)  # 1 because we want to surrounding black pixels to disappear

    except Exception as e:
      slicer.util.errorDisplay("Failed to change lower thresholds: " + str(e))

#
# Initialise Extension evnironment with linking views and shortcuts
#
class ExtensionEnvironment:
  def __init__(self):
    # create variables
    self.fiducialtool = None
    self.shortcuts = None

    # run processing
    self.__initialiseFiducialPlacer()
    self.__createShortcuts()

  def __initialiseFiducialPlacer(self):
    """
    Switch to the fiducial placer tool
    """
    self.interactionNode = slicer.app.applicationLogic().GetInteractionNode()

  def __initialise_views(self, volumes=None):
    """
    Initialise views with the US volumes
    :param volumes: a list of volume names
    :return the composite node that can be used by the change view function
    """
    # todo move view changing to widget (or even all the shortcuts)
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

  def __change_view(self, direction='forward'):
    """
    Change the view forward or backward (take the list three possible volumes and for the two displayed volumes increase
    their index by one)
    :param direction:
    :return:
    """
    volumes = ["US1 Pre-dura", "US2 Post-dura", "US3 Resection Control"]
    volume_background = None
    volume_foreground = None

    # initialise views and get the composite node
    compositeNode = self.__initialise_views()

    # get current foreground and background volumes
    current_foreground_id = compositeNode.GetForegroundVolumeID()
    current_foreground_volume = slicer.mrmlScene.GetNodeByID(current_foreground_id)
    current_foreground_name = current_foreground_volume.GetName()
    current_background_id = compositeNode.GetBackgroundVolumeID()
    current_background_volume = slicer.mrmlScene.GetNodeByID(current_background_id)
    current_background_name = current_background_volume.GetName()

    # switch backgrounds
    if direction == 'forward':
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
    elif direction == 'backward':
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
      if direction == 'backward' or direction == 'forward':
        slicer.util.setSliceViewerLayers(background=volume_background, foreground=volume_foreground)
      else:
        print("wrong direction")
    else:
      print("No volumes to set for foreground and background")

  def __change_foreground_opacity_discrete(self, new_opacity=0.5):
    layoutManager = slicer.app.layoutManager()

    # iterate through all views and set opacity to
    for sliceViewName in layoutManager.sliceViewNames():
      view = layoutManager.sliceWidget(sliceViewName).sliceView()
      sliceNode = view.mrmlSliceNode()
      sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
      compositeNode = sliceLogic.GetSliceCompositeNode()
      compositeNode.SetForegroundOpacity(new_opacity)

  def __change_foreground_opacity_continuous(self, opacity_change=0.01):
    # TODO threshold change needs to be initialized once with setting it to 0.5 with discrete, otherwise it's stuck
    layoutManager = slicer.app.layoutManager()

    # iterate through all views and set opacity to
    for sliceViewName in layoutManager.sliceViewNames():
      view = layoutManager.sliceWidget(sliceViewName).sliceView()
      sliceNode = view.mrmlSliceNode()
      sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
      compositeNode = sliceLogic.GetSliceCompositeNode()
      compositeNode.SetForegroundOpacity(compositeNode.GetForegroundOpacity() + opacity_change)

  def __set_foreground_threshold(self, threshold):
    """
    Set foreground threshold to 1, so that the surrounding black pixels disappear
    """
    # get current foreground
    layoutManager = slicer.app.layoutManager()
    view = layoutManager.sliceWidget('Red').sliceView()
    sliceNode = view.mrmlSliceNode()
    sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
    compositeNode = sliceLogic.GetSliceCompositeNode()

    current_foreground_id = compositeNode.GetForegroundVolumeID()
    current_foreground_volume = slicer.mrmlScene.GetNodeByID(current_foreground_id)
    current_foreground_name = current_foreground_volume.GetName()

    volNode = slicer.util.getNode(current_foreground_name)
    dispNode = volNode.GetDisplayNode()
    dispNode.ApplyThresholdOn()
    dispNode.SetLowerThreshold(threshold)  # 1 because we want to surrounding black pixels to disappear
    #current_foreground_volume.AddObserver(slicer.vtkMRMLScalarVolumeDisplayNode.PointModifiedEvent, dispNode.SetLowerThreshold)

  @staticmethod
  def linkViews():
    """
    # link views
    # Set linked slice views  in all existing slice composite nodes and in the default node
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

  def __createShortcuts(self):
    self.shortcuts = [('d', lambda: self.interactionNode.SetCurrentInteractionMode(self.interactionNode.Place)),  # fiducial placement
                      ('a', functools.partial(self.__change_view, "backward")),  # volume switching dir1
                      ('s', functools.partial(self.__change_view, "forward")),  # volume switching dir2
                      ('1', functools.partial(self.__change_foreground_opacity_discrete, 0.0)),  # change opacity to 0.5
                      ('2', functools.partial(self.__change_foreground_opacity_discrete, 0.5)),  # change opacity to 0.5
                      ('3', functools.partial(self.__change_foreground_opacity_discrete, 1.0)),  # change opacity to 1.0
                      ('q', functools.partial(self.__change_foreground_opacity_continuous, 0.02)),  # incr. op. by .01
                      ('w', functools.partial(self.__change_foreground_opacity_continuous, -0.02)),  # decr. op. by .01
                      ('l', functools.partial(self.__set_foreground_threshold, 1))]  # set foreground threshold to 1

  def initialiseShortcuts(self):
    for (shortcutKey, callback) in self.shortcuts:
        shortcut = qt.QShortcut(slicer.util.mainWindow())
        shortcut.setKey(qt.QKeySequence(shortcutKey))
        shortcut.connect('activated()', callback)


#
# LandmarkingViewLogic
#

class LandmarkingViewLogic(ScriptedLoadableModuleLogic):
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
  def setup_segment_editor(segment_name, segmentationNode=None, volumeNode=None):
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
      segmentationNode.SetName(segment_name)

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

  def process(self, volume1, volume2, volume3):
    """
    Creates the intersectin of the first three volumes and siplays it as an outline
    """

    if volume1 is None or volume2 is None or volume3 is None:
      slicer.util.errorDisplay( "Select all three volumes")
      return

    import time
    startTime = time.time()
    logging.info('Processing started')

    # usVolumes = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
    usVolumes = (volume1, volume2, volume3)

    # initialise segment editor
    segmentEditorWidget, segmentEditorNode, segmentationNode = self.setup_segment_editor("us_outlines")

    addedSegmentID = []

    # for each volume create a threshold segmentation
    for idx, volume in enumerate(usVolumes):
      segmentEditorWidget.setMasterVolumeNode(volume)

      # Create segment
      addedSegmentID.append(segmentationNode.GetSegmentation().AddEmptySegment(volume.GetName()[0:3] + "_bb"))
      segmentEditorNode.SetSelectedSegmentID(addedSegmentID[idx])

      # Fill by thresholding
      segmentEditorWidget.setActiveEffectByName("Threshold")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("MinimumThreshold", "1")
      effect.setParameter("MaximumThreshold", "255")
      effect.self().onApply()

    # https://slicer.readthedocs.io/en/latest/developer_guide/modules/segmenteditor.html#effect-parameters
    # https://discourse.slicer.org/t/how-to-programmatically-use-logical-operator-add-function-from-segment-editor/16581/2
    # https://discourse.slicer.org/t/how-to-change-the-slice-fill-in-segmentations-in-a-python-script/20871/2
    # Display settings are stored in the display node
    intersection_segment_id = segmentationNode.GetSegmentation().AddEmptySegment("intersection")
    segmentEditorNode.SetSelectedSegmentID(intersection_segment_id)
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()

    # add first segmentations
    effect.setParameter("Operation", SegmentEditorEffects.LOGICAL_UNION)

    effect.setParameter("ModifierSegmentID", volume1.GetName()[0:3] + "_bb")
    effect.self().onApply()

    # intersect with the next two segmentations
    effect.setParameter("Operation", SegmentEditorEffects.LOGICAL_INTERSECT)

    effect.setParameter("ModifierSegmentID", volume2.GetName()[0:3] + "_bb")
    effect.self().onApply()

    effect.setParameter("ModifierSegmentID", volume3.GetName()[0:3] + "_bb")
    effect.self().onApply()

    # remove segments
    for id in addedSegmentID:
      if "intersection" not in id:
        segmentationNode.RemoveSegment(id)

    # display only outline
    # https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html#modify-segmentation-display-options
    # http://apidocs.slicer.org/master/classvtkMRMLSegmentationDisplayNode.html#afeca62a2a79513ab275db3840136709c
    segmentation = slicer.mrmlScene.GetFirstNodeByName('us_outlines')
    displayNode = segmentation.GetDisplayNode()
    displayNode.SetSegmentOpacity2DFill(intersection_segment_id, 0.0)  # Set fill opacity of a single segment
    displayNode.SetSegmentOpacity2DOutline(intersection_segment_id, 1.0)  # Set outline opacity of a single segment

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds'.format(stopTime-startTime))

#
# LandmarkingViewTest
#

class LandmarkingViewTest(ScriptedLoadableModuleTest):
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
    self.test_LandmarkingView1()

  def test_LandmarkingView1(self):
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

    # Get/create input data

    import SampleData
    registerSampleData()
    inputVolume = SampleData.downloadSample('LandmarkingView1')
    self.delayDisplay('Loaded test data set')

    inputScalarRange = inputVolume.GetImageData().GetScalarRange()
    self.assertEqual(inputScalarRange[0], 0)
    self.assertEqual(inputScalarRange[1], 695)

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    threshold = 100

    # Test the module logic

    logic = LandmarkingViewLogic()

    # Test algorithm with non-inverted threshold
    logic.process(inputVolume, outputVolume, threshold, True)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], threshold)

    # Test algorithm with inverted threshold
    logic.process(inputVolume, outputVolume, threshold, False)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], inputScalarRange[1])

    self.delayDisplay('Test passed')
