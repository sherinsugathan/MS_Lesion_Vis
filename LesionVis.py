#==========================================
# Title:  MS Lesion Visualization Project
# Author: Sherin Sugathan
# Last Modified Date:   9 Jan 2020
#==========================================

import sys
import os
import vtk
import itk
import logging
import math
import Settings
import Subject
import LesionUtils
import LesionMapper
from LesionMapper import LesionMapper
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
import nibabel as nib
import numpy as np
import json
import ctypes
import time
import copy
from ctypes import wintypes


from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QCheckBox, QButtonGroup, QAbstractButton
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt
from PyQt5.QtCore import QTimer
from os import system, name
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from freesurfer_surface import Surface, Vertex, Triangle
from enum import Enum

class Ui(Qt.QMainWindow):

    # Main Initialization
    def __init__(self):
        super(Ui, self).__init__()
        # Needed for windows task bar icon
        myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        lpBuffer = wintypes.LPWSTR()
        AppUserModelID = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID
        AppUserModelID(ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR))
        appid = lpBuffer.value
        ctypes.windll.kernel32.LocalFree(lpBuffer)
        if appid is not None:
            print(appid)
        # End taskbar icon enable.
        uic.loadUi("lesionui.ui", self)
        logging.info('UI file loaded successfully.')
        self.dataFolderInitialized = False # Flag to indicate that the dataset folder is properly set.
        self.volumeDataLoaded = False # Flag to indicate that volume data is initialized and loaded.
        #self.showMaximized()
        self.initUI()
        self.clear()
        logging.info('UI initialized successfully.')
        self.initVTK()
        
        self.showMaximized()
        #self.message = "tick"
        #self.timer = QTimer()
        #self.timer.timeout.connect(self.onTimerEvent)
        #self.timer.start(100)
        logging.info('VTK initialized successfully.')


    # Initialize the UI.    
    def initUI(self):
        self.pushButton_LoadFolder.clicked.connect(self.on_click_browseFolder) # Attaching button click Handlers
        self.pushButton_LoadData.clicked.connect(self.on_click_LoadData) # Attaching button click Handlers for load surfaces.
        self.pushButton_LoadStructural.clicked.connect(self.on_click_LoadStructural) # Attaching button click Handlers for load structural brain volumes.
        self.dial.setMinimum(0)
        self.dial.setMaximum(500)
        self.dial.setValue(500)
        self.dial.valueChanged.connect(self.on_DialMoved)
        self.pushButton_UnselectAllSubjects.clicked.connect(self.on_click_UnselectAllSubjects) # Attaching button click Handlers
        self.checkBox_DepthPeeling.stateChanged.connect(self.depthpeel_state_changed) # Attaching handler for depth peeling state change.
        self.checkBox_PerLesion.stateChanged.connect(self.perLesion_state_changed) # Attaching handler for per lesion.
        self.checkBox_Parcellation.stateChanged.connect(self.parcellation_state_changed) # Attaching handler for parcellation display.
        self.checkBox_LesionMappingDualView.stateChanged.connect(self.dual_view_state_changed) # Attaching handler for dual view display.
        self.pushButton_Screenshot.clicked.connect(self.on_click_CaptureScreeshot) # Attaching button click Handlers
        self.comboBox_LesionFilter.currentTextChanged.connect(self.on_combobox_changed_LesionFilter) # Attaching handler for lesion filter combobox selection change.
        # self.comboBox_VisType.addItem("Default View")
        # self.comboBox_VisType.addItem("Transparent Surfaces")
        # self.comboBox_VisType.addItem("Lesion Intensity Raw Vis.")
        # self.comboBox_VisType.addItem("Lesion Difference With NAWM")
        # self.comboBox_VisType.addItem("Lesion Classification View")
        # self.comboBox_VisType.addItem("Lesion Surface Mapping")
        # self.comboBox_VisType.addItem("Study Lesion Impact")
        self.comboBox_VisType.addItem("Full Data View - Raw")
        self.comboBox_VisType.addItem("Lesion Colored - Continuous")
        self.comboBox_VisType.addItem("Lesion Colored - Discrete")
        self.comboBox_VisType.addItem("Lesion Colored - Distance")
        self.comboBox_VisType.addItem("Lesion Surface Mapping")

        self.comboBox_LesionFilter.addItem("None")
        self.comboBox_LesionFilter.addItem("Voxel Count")
        self.comboBox_LesionFilter.addItem("Elongation")
        self.comboBox_LesionFilter.addItem("Perimeter")
        self.comboBox_LesionFilter.addItem("Spherical Radius")
        self.comboBox_LesionFilter.addItem("Spherical Perimeter")
        self.comboBox_LesionFilter.addItem("Flatness")
        self.comboBox_LesionFilter.addItem("Roundness")

        self.mprA_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRA)
        self.mprB_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRB)
        self.mprC_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRC)
        self.horizontalSliderLesionFilter.valueChanged.connect(self.on_sliderChangedLesionFilter)

        pm = Qt.QPixmap("fundAndSupportLogos.png")
        self.imageLabel.setPixmap(pm.scaled(self.imageLabel.size().width(), self.imageLabel.size().height(), 1,1))
        pmMain = Qt.QPixmap("AppLogo.png")
        self.logoLabel.setPixmap(pmMain.scaled(self.logoLabel.size().width(), self.logoLabel.size().height(), 1,1))
        modeIconSize = Qt.QSize(50, 50)
        normalModeIcon = Qt.QPixmap("icons/normalMode.png")
        dualModeIcon = Qt.QPixmap("icons/dualMode.png")
        unfoldModeIcon = Qt.QPixmap("icons/2DMode.png")

        self.pushButton_NormalMode.setIcon(QtGui.QIcon(normalModeIcon))
        self.pushButton_DualMode.setIcon(QtGui.QIcon(dualModeIcon))
        self.pushButton_2DMode.setIcon(QtGui.QIcon(unfoldModeIcon))
        self.pushButton_NormalMode.setIconSize(modeIconSize)
        self.pushButton_DualMode.setIconSize(modeIconSize)
        self.pushButton_2DMode.setIconSize(modeIconSize)

    def onTimerEvent(self):
        if self.message == "tick":
            self.message = "tock"
            #self.brodmannTextActor.SetInput("Hello")
            #self.iren.Render()
        else:
            self.message = "tick"
            #self.brodmannTextActor.SetInput("Sherin")
            #self.iren.Render()

    # Initialize vtk
    def initVTK(self):
        # Define viewport ranges (3 MPRS and 1 volume rendering)
        #self.mprA_Viewport=[0.0, 0.667, 0.333, 1.0]
        #self.mprB_Viewport=[0.0, 0.334, 0.333, 0.665]
        #self.mprC_Viewport=[0.0, 0.0, 0.1, 0.1]
        #self.VR_Viewport=[0.335, 0, 1.0, 1.0]
        self.parcellation_Viewport = [0.8, 0, 1, 0.32]
        #self.dualViewportLeft = [0.0, 0.0, 0.5, 1.0]
        #self.dualViewportRight = [0.5, 0.0, 1.0, 1.0]

        self.vl = Qt.QVBoxLayout()
        self.vl_MPRA = Qt.QVBoxLayout()
        self.vl_MPRB = Qt.QVBoxLayout()
        self.vl_MPRC = Qt.QVBoxLayout()
        self.vl_LesionMapDualLeft = Qt.QVBoxLayout()
        self.vl_LesionMapDualRight = Qt.QVBoxLayout()

        # Frame widgets
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkWidgetMPRA = QVTKRenderWindowInteractor(self.frame_MPRA)
        self.vtkWidgetMPRB = QVTKRenderWindowInteractor(self.frame_MPRB)
        self.vtkWidgetMPRC = QVTKRenderWindowInteractor(self.frame_MPRC)
        self.vtkWidgetLesionMapDualLeft = QVTKRenderWindowInteractor(self.frame_DualLeft)
        self.vtkWidgetLesionMapDualRight = QVTKRenderWindowInteractor(self.frame_DualRight)
        # Orientation cube.
        self.axesActor = vtk.vtkAnnotatedCubeActor()
        self.vl.addWidget(self.vtkWidget)
        self.vl_MPRA.addWidget(self.vtkWidgetMPRA)
        self.vl_MPRB.addWidget(self.vtkWidgetMPRB)
        self.vl_MPRC.addWidget(self.vtkWidgetMPRC)
        self.vl_LesionMapDualLeft.addWidget(self.vtkWidgetLesionMapDualLeft)
        self.vl_LesionMapDualRight.addWidget(self.vtkWidgetLesionMapDualRight)
        self.vtkWidget.Initialize()
        self.vtkWidgetMPRA.Initialize()
        self.vtkWidgetMPRB.Initialize()
        self.vtkWidgetMPRC.Initialize()
        self.vtkWidgetLesionMapDualLeft.Initialize()
        self.vtkWidgetLesionMapDualRight.Initialize()

        self.ren = vtk.vtkRenderer() # Renderer for volume
        self.renMapOutcome = vtk.vtkRenderer() # Renderer for displaying mapping outcomes.
        self.renMPRA = vtk.vtkRenderer() # Renderer for MPR A
        self.renMPRB = vtk.vtkRenderer() # Renderer for MPR B
        self.renMPRC = vtk.vtkRenderer() # Renderer for MPR C
        self.renDualLeft = vtk.vtkRenderer() # Renderer for dual view lesion map left
        self.renDualRight = vtk.vtkRenderer() # Renderer for dual view lesion map right
        self.renOrientationCube = vtk.vtkRenderer()
        self.ren.SetBackground(0.0235,0.0711,0.0353)
        
        self.renMPRA.SetBackground(0,0,0)
        self.renMPRB.SetBackground(0,0,0)
        self.renMPRC.SetBackground(0,0,0)
        #self.ren.SetViewport(self.VR_Viewport[0], self.VR_Viewport[1], self.VR_Viewport[2], self.VR_Viewport[3])
        self.renMapOutcome.SetViewport(self.parcellation_Viewport[0], self.parcellation_Viewport[1], self.parcellation_Viewport[2], self.parcellation_Viewport[3])
        self.renDualLeft.SetBackground(0.0235,0.0711,0.0353)
        self.renDualRight.SetBackground(0.0235,0.0711,0.0353)
        #self.renDual.SetBackground(0, 1, 0)
        if self.checkBox_DepthPeeling.isChecked():
            self.ren.SetUseDepthPeeling(True)
            self.ren.SetMaximumNumberOfPeels(4)
        
        #self.renMPRA.SetViewport(self.mprA_Viewport[0], self.mprA_Viewport[1], self.mprA_Viewport[2], self.mprA_Viewport[3])
        #self.renMPRB.SetViewport(self.mprB_Viewport[0], self.mprB_Viewport[1], self.mprB_Viewport[2], self.mprB_Viewport[3])
        #self.renMPRC.SetViewport(self.mprC_Viewport[0], self.mprC_Viewport[1], self.mprC_Viewport[2], self.mprC_Viewport[3])

        # GPU enable attempt
        #self.renderWindow = vtk.vtkGenericOpenGLRenderWindow()
        #self.vtkWidget.SetRenderWindow(self.renderWindow)
        self.vtkWidget.GetRenderWindow().SetAlphaBitPlanes(True)
        self.vtkWidget.GetRenderWindow().SetMultiSamples(0)
    
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        #self.vtkWidget.GetRenderWindow().AddRenderer(self.renMapOutcome)

        #self.vtkWidget.GetRenderWindow().AddRenderer(self.renOrientationCube)
        #self.vtkWidget.GetRenderWindow().AddRenderer(self.renMPRB)
        #self.vtkWidget.GetRenderWindow().AddRenderer(self.renMPRC)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.SetRenderWindow(self.vtkWidget.GetRenderWindow())

        self.vtkWidgetMPRA.GetRenderWindow().AddRenderer(self.renMPRA)
        self.iren_MPRA = self.vtkWidgetMPRA.GetRenderWindow().GetInteractor()
        self.vtkWidgetMPRB.GetRenderWindow().AddRenderer(self.renMPRB)
        self.iren_MPRB = self.vtkWidgetMPRB.GetRenderWindow().GetInteractor()
        self.vtkWidgetMPRC.GetRenderWindow().AddRenderer(self.renMPRC)
        self.iren_MPRC = self.vtkWidgetMPRC.GetRenderWindow().GetInteractor()
        self.vtkWidgetLesionMapDualLeft.GetRenderWindow().AddRenderer(self.renDualLeft)
        self.iren_LesionMapDualLeft = self.vtkWidgetLesionMapDualLeft.GetRenderWindow().GetInteractor()
        self.vtkWidgetLesionMapDualRight.GetRenderWindow().AddRenderer(self.renDualRight)
        self.iren_LesionMapDualRight = self.vtkWidgetLesionMapDualRight.GetRenderWindow().GetInteractor()

        self.resliceImageViewerMPRA = vtk.vtkResliceImageViewer()
        self.resliceImageViewerMPRB = vtk.vtkResliceImageViewer()
        self.resliceImageViewerMPRC = vtk.vtkResliceImageViewer()
        self.resliceImageViewerMPRA.GetImageActor().RotateZ(180)
        #self.resliceImageViewerMPRB.GetImageActor().RotateY(90)  # Apply 90 degree rotation once to fix the viewer's nature to display data with wrong rotation (against convention).
        #self.resliceImageViewerMPRC.GetImageActor().RotateX(90)  # Apply 90 degree rotation once to fix the viewer's nature to display data with wrong rotation (against convention).
        #self.renMPRB.ResetCamera() # Needed for making the camera look at the slice properly.
        #self.renMPRC.ResetCamera() # Needed for making the camera look at the slice properly.

        self.informationKey = vtk.vtkInformationStringKey.MakeKey("ID", "vtkActor")
        self.informationUniqueKey = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")
        #self.actorInformationKey = vtk.vtkInformationStringVectorKey.MakeKey("actorInformation", "vtkActor")
        self.lesionSeededFiberTracts = False

        self.niftyReaderT1 = vtk.vtkNIFTIImageReader() # Common niftyReader.
        self.currentSliceVolume = vtk.vtkNIFTIImageReader()
        self.voxelSpaceCorrectedMask = vtk.vtkNIFTIImageReader()
        self.modelListBoxSurfaces = QtGui.QStandardItemModel() # List box for showing loaded surfaces.
        self.listView.setModel(self.modelListBoxSurfaces)
        self.listView.selectionModel().selectionChanged.connect(self.onSurfaceListSelectionChanged) # Event handler for surface list view selection changed.

        self.sliceNumberTextMPRA = vtk.vtkTextActor() # MPRA Slice number
        self.sliceNumberTextMPRB = vtk.vtkTextActor() # MPRB Slice number
        self.sliceNumberTextMPRC = vtk.vtkTextActor() # MPRC Slice number
        self.sliceNumberTextMPRA.UseBorderAlignOff()
        self.sliceNumberTextMPRA.SetPosition(0,0)
        self.sliceNumberTextMPRA.GetTextProperty().SetFontFamily(4)
        self.sliceNumberTextMPRA.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
        self.sliceNumberTextMPRA.GetTextProperty().SetFontSize(14)
        self.sliceNumberTextMPRA.GetTextProperty().ShadowOn()
        self.sliceNumberTextMPRA.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
        self.renMPRA.AddActor2D(self.sliceNumberTextMPRA)
        self.sliceNumberTextMPRB.UseBorderAlignOff()
        self.sliceNumberTextMPRB.SetPosition(0,0)
        self.sliceNumberTextMPRB.GetTextProperty().SetFontFamily(4)
        self.sliceNumberTextMPRB.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
        self.sliceNumberTextMPRB.GetTextProperty().SetFontSize(14)
        self.sliceNumberTextMPRB.GetTextProperty().ShadowOn()
        self.sliceNumberTextMPRB.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
        self.renMPRB.AddActor2D(self.sliceNumberTextMPRB)
        self.sliceNumberTextMPRC.UseBorderAlignOff()
        self.sliceNumberTextMPRC.SetPosition(0,0)
        self.sliceNumberTextMPRC.GetTextProperty().SetFontFamily(4)
        self.sliceNumberTextMPRC.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
        self.sliceNumberTextMPRC.GetTextProperty().SetFontSize(14)
        self.sliceNumberTextMPRC.GetTextProperty().ShadowOn()
        self.sliceNumberTextMPRC.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
        self.renMPRC.AddActor2D(self.sliceNumberTextMPRC)

        # Text overlay support in main renderer.
        self.overlayDataMain = {"Lesion ID":"NA", "Voxel Count":"NA", "Centroid":"NA", "Elongation":"NA", "Lesion Perimeter":"NA", "Lesion Spherical Radius":"NA", "Lesion Spherical Perimeter":"NA", "Lesion Flatness":"NA", "Lesion Roundness":"NA"}
        self.overlayDataGlobal = {"Lesion Load":"0", "Depth Peeling":"Disabled", "OpenGL Renderer":"Unknown"}
        self.textActorLesionStatistics = vtk.vtkTextActor()
        self.textActorGlobal = vtk.vtkTextActor()
        self.depthPeelingStatus = "Depth Peeling : Enabled"
        self.numberOfLesions = 0
        self.textActorLesionStatistics.UseBorderAlignOff()
        self.textActorLesionStatistics.SetPosition(10,0)
        self.textActorLesionStatistics.GetTextProperty().SetFontFamily(4)
        self.textActorLesionStatistics.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
        self.textActorLesionStatistics.GetTextProperty().SetFontSize(14)
        self.textActorLesionStatistics.GetTextProperty().ShadowOn()
        self.textActorLesionStatistics.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )

        self.textActorGlobal.UseBorderAlignOff()
        self.textActorGlobal.GetTextProperty().SetFontFamily(4)
        self.textActorGlobal.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
        self.textActorGlobal.GetTextProperty().SetFontSize(14)
        self.textActorGlobal.GetTextProperty().ShadowOn()
        self.textActorGlobal.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )

        ui_path = os.path.dirname(os.path.abspath(__file__))
        fontPath = os.path.join(ui_path, "fonts\\RobotoMono-Medium.ttf")
        self.brodmannTextActor = vtk.vtkTextActor()
        self.brodmannTextActor.UseBorderAlignOn()
        self.brodmannTextActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        self.brodmannTextActor.SetPosition(0.5,0)
        self.brodmannTextActor.GetTextProperty().SetFontFamily(4)
        self.brodmannTextActor.GetTextProperty().SetFontFile(fontPath)
        self.brodmannTextActor.GetTextProperty().SetFontSize(20)
        self.brodmannTextActor.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
        self.brodmannTextActor.GetTextProperty().SetJustificationToCentered()
        #self.brodmannTextActor.SetInput("NA")

        self.actorPropertiesMain = []
        self.actorPropertiesDual = []

        self.style = LesionUtils.MouseInteractorHighLightActor(None, self.iren, self.overlayDataMain, self.textActorLesionStatistics, self.overlayDataGlobal, self.textActorGlobal, self.informationKey, self.informationUniqueKey, self.lesionSeededFiberTracts, self.mprA_Slice_Slider, self.mprB_Slice_Slider, self.mprC_Slice_Slider)
        self.style.SetDefaultRenderer(self.ren)
        self.style.brodmannTextActor = self.brodmannTextActor
        self.style.vtkWidget = self.vtkWidget
        self.style.renMapOutcome = self.renMapOutcome
        self.renMapOutcome.AddActor2D(self.brodmannTextActor)
        self.iren.SetInteractorStyle(self.style)

        self.ren.ResetCamera() # Main Renderer Camera Reset
        self.frame.setLayout(self.vl)
        self.renMPRA.ResetCamera() # MPRA Camera Reset
        self.frame_MPRA.setLayout(self.vl_MPRA)
        self.renMPRB.ResetCamera() # MPRB Camera Reset
        self.frame_MPRB.setLayout(self.vl_MPRB)
        self.renMPRC.ResetCamera() # MPRC Camera Reset
        self.frame_MPRC.setLayout(self.vl_MPRC)
        self.renDualLeft.ResetCamera() # Lesion Mapping Dual Camera Left Reset
        self.frame_DualLeft.setLayout(self.vl_LesionMapDualLeft)
        self.renDualRight.ResetCamera() # Lesion Mapping Dual Camera Right Reset
        self.frame_DualRight.setLayout(self.vl_LesionMapDualRight)

        self.buttonGroupModality = QButtonGroup()
        self.buttonGroupModality.addButton(self.pushButton_T1)
        self.buttonGroupModality.addButton(self.pushButton_T2)
        self.buttonGroupModality.addButton(self.pushButton_FLAIR)
        self.buttonGroupModality.setExclusive(True)
        self.buttonGroupModality.buttonClicked.connect(self.on_buttonGroupModalityChanged)

        self.buttonGroupVis = QButtonGroup()
        self.buttonGroupVis.addButton(self.pushButton_Continuous)
        self.buttonGroupVis.addButton(self.pushButton_Discrete)
        self.buttonGroupVis.addButton(self.pushButton_Distance)
        self.buttonGroupVis.setExclusive(True)
        self.buttonGroupVis.buttonClicked.connect(self.on_buttonGroupVisChanged)

        self.buttonGroupModes = QButtonGroup()
        self.buttonGroupModes.addButton(self.pushButton_NormalMode)
        self.buttonGroupModes.addButton(self.pushButton_DualMode)
        self.buttonGroupModes.addButton(self.pushButton_2DMode)
        self.buttonGroupModes.setExclusive(True)
        self.buttonGroupModes.buttonClicked.connect(self.on_buttonGroupModesChanged)

        self.show()
        self.iren.Initialize()
        self.iren_MPRA.Initialize()
        self.iren_MPRB.Initialize()
        self.iren_MPRC.Initialize()
        self.iren_LesionMapDualLeft.Initialize()
        self.iren_LesionMapDualRight.Initialize()

        self.imageLabel.hide()

        openglRendererInUse = self.ren.GetRenderWindow().ReportCapabilities().splitlines()[1].split(":")[1].strip()
        self.overlayDataGlobal["OpenGL Renderer"] = openglRendererInUse

    def ScrollSlice(self, obj, ev):
        print("Before Event")
        obj.OnMouseWheelForward()

    # Load and Render Structural data as image slices.
    def LoadStructuralSlices(self, subjectFolder, modality, IsOverlayEnabled = False):
        if(True):
            fileName = subjectFolder + "\\structural\\"+modality+".nii"
            fileNameOverlay = subjectFolder + "\\lesionMask\\ConnectedComponents"+modality+"VoxelSpaceCorrected.nii"
            self.niftyReaderT1.SetFileName(fileName)
            self.niftyReaderT1.Update()
            self.currentSliceVolume.SetFileName(fileName)
            self.currentSliceVolume.Update()
            self.voxelSpaceCorrectedMask.SetFileName(fileNameOverlay)
            self.voxelSpaceCorrectedMask.Update()

            # currentVolume = None
            # if(IsOverlayEnabled == True):
            #     currentVolume = self.voxelSpaceCorrectedMask
            # else:
            #     currentVolume = self.currentSliceVolume
            blendedVolume = LesionUtils.computeVolumeMaskBlend(self.currentSliceVolume, self.voxelSpaceCorrectedMask, 0.5)
            range = self.currentSliceVolume.GetOutput().GetPointData().GetScalars().GetRange()
            #print("RANGE", range[1], range[0])

            window = (range[1] - range[0])/2.0
            level = range[0] + (window/2.0)
            #print(window, level)
            ################################
            # MPR A    #####################
            ################################
            self.resliceImageViewerMPRA.SetInputData(blendedVolume.GetOutput())
            self.resliceImageViewerMPRA.SetRenderWindow(self.vtkWidgetMPRA.GetRenderWindow())
            self.resliceImageViewerMPRA.SetRenderer(self.renMPRA)
            self.resliceImageViewerMPRA.SetSliceOrientation(2)
            self.resliceImageViewerMPRA.SliceScrollOnMouseWheelOn()
            self.resliceImageViewerMPRA.SetColorWindow(window)
            self.resliceImageViewerMPRA.SetColorLevel(level)
            self.mprA_Slice_Slider.setMaximum(self.resliceImageViewerMPRA.GetSliceMax())
            self.resliceImageViewerMPRA.SetSlice(math.ceil((self.resliceImageViewerMPRA.GetSliceMin()+self.resliceImageViewerMPRA.GetSliceMax())/2))
            self.mprA_Slice_Slider.setValue(math.ceil((self.resliceImageViewerMPRA.GetSliceMin()+self.resliceImageViewerMPRA.GetSliceMax())/2))
            # Define Interactor
            # #interactorMPRA = vtk.vtkInteractorStyleImage()
            # interactorMPRA = LesionUtils.MyMPRInteractorStyle()
            # interactorMPRA.SetDefaultRenderer(self.renMPRA)
            # interactorMPRA.SetInteractionModeToImageSlicing()
            # #interactorMPRA.AddObserver("MouseWheelForwardEvent", self.ScrollSlice)
            # self.iren_MPRA.SetInteractorStyle(interactorMPRA)
            # #self.iren_MPRA.AddObserver("MouseWheelForwardEvent", self.ScrollSlice)
            # #self.resliceImageViewerMPRA.SetupInteractor(self.iren_MPRA)
            # #self.iren_MPRA.Initialize()

            interactorMPRA = vtk.vtkInteractorStyleImage()
            interactorMPRA.SetInteractionModeToImageSlicing()
            self.iren_MPRA.SetInteractorStyle(interactorMPRA)
            self.resliceImageViewerMPRA.SetupInteractor(self.iren_MPRA)
            
            ################################
            # MPR B    #####################
            ################################
            self.resliceImageViewerMPRB.SetInputData(blendedVolume.GetOutput())
            self.resliceImageViewerMPRB.SetRenderWindow(self.vtkWidgetMPRB.GetRenderWindow())
            self.resliceImageViewerMPRB.SetRenderer(self.renMPRB)
            self.resliceImageViewerMPRB.SetSliceOrientation(1)
            self.resliceImageViewerMPRB.SetColorWindow(window)
            self.resliceImageViewerMPRB.SetColorLevel(level)
            self.resliceImageViewerMPRB.SetResliceModeToAxisAligned()
            self.mprB_Slice_Slider.setMaximum(self.resliceImageViewerMPRB.GetSliceMax())
            self.resliceImageViewerMPRB.SetSlice(math.ceil((self.resliceImageViewerMPRB.GetSliceMin() + self.resliceImageViewerMPRB.GetSliceMax())/2))
            self.mprB_Slice_Slider.setValue(math.ceil((self.resliceImageViewerMPRB.GetSliceMin() + self.resliceImageViewerMPRB.GetSliceMax())/2))
            # Define Interactor
            interactorMPRB = vtk.vtkInteractorStyleImage()
            interactorMPRB.SetInteractionModeToImageSlicing()
            self.iren_MPRB.SetInteractorStyle(interactorMPRB)
            self.resliceImageViewerMPRB.SetupInteractor(self.iren_MPRB)

            ################################
            # MPR C    #####################
            ################################
            self.resliceImageViewerMPRC.SetResliceModeToAxisAligned()
            self.resliceImageViewerMPRC.SetInputData(blendedVolume.GetOutput())
            self.resliceImageViewerMPRC.SetRenderWindow(self.vtkWidgetMPRC.GetRenderWindow())
            self.resliceImageViewerMPRC.SetRenderer(self.renMPRC)
            self.resliceImageViewerMPRC.SetSliceOrientation(0)
            self.resliceImageViewerMPRC.SetColorWindow(window)
            self.resliceImageViewerMPRC.SetColorLevel(level)
            self.mprC_Slice_Slider.setMaximum(self.resliceImageViewerMPRC.GetSliceMax())
            self.resliceImageViewerMPRC.SliceScrollOnMouseWheelOn()
            self.resliceImageViewerMPRC.SetSlice(math.ceil((self.resliceImageViewerMPRC.GetSliceMin()+self.resliceImageViewerMPRC.GetSliceMax())/2))
            self.mprC_Slice_Slider.setValue(math.ceil((self.resliceImageViewerMPRC.GetSliceMin()+self.resliceImageViewerMPRC.GetSliceMax())/2))
            # Define Interactor
            interactorMPRC = vtk.vtkInteractorStyleImage()
            interactorMPRC.SetInteractionModeToImageSlicing()
            self.iren_MPRC.SetInteractorStyle(interactorMPRC)
            self.resliceImageViewerMPRC.SetupInteractor(self.iren_MPRC)

            self.renMPRA.ResetCamera()
            self.renMPRB.ResetCamera()
            self.renMPRC.ResetCamera()
            self.renMPRA.GetActiveCamera().Zoom(1.5)
            self.renMPRB.GetActiveCamera().Zoom(1.5)
            self.renMPRC.GetActiveCamera().Zoom(1.5)

            self.iren_MPRA.Render()
            self.iren_MPRB.Render()
            self.iren_MPRC.Render()
        
    #####################################
    # MAIN LOADER: Load and Render Data #
    #####################################
    def renderData(self, fileNames, settings=None):
        # Performance log
        start_time = time.time()
        
        self.subjectFolder = os.path.join(self.lineEdit_DatasetFolder.text(), str(self.comboBox_AvailableSubjects.currentText()))
        # Load data for MPRs.
        self.LoadStructuralSlices(self.subjectFolder, "T1", True)
        #self.comboBox_MPRModality.setCurrentIndex(0) # Default is T1   # TODO : Remove this old UI element

        self.actors = []
        self.lesionCentroids = []
        self.lesionNumberOfPixels = []
        self.lesionElongation = []
        self.lesionPerimeter = []
        self.lesionSphericalRadius = []
        self.lesionSphericalPerimeter = []
        self.lesionFlatness = []
        self.lesionRoundness = []
        self.lesionAverageIntensity  = []
        self.lesionAverageSurroundingIntensity = []
        #self.lesionRegionNumberQuantized = []
        self.lesionAffectedPointIdsLh = []
        self.lesionAffectedPointIdsRh = []
        self.lesionAverageLesionIntensityT1 = []
        self.lesionAverageSuroundingIntensityT1 = []
        self.lesionAverageLesionIntensityT2 = []
        self.lesionAverageSuroundingIntensityT2 = []
        self.lesionAverageLesionIntensityFLAIR = []
        self.lesionAverageSuroundingIntensityFLAIR = []

        # load precomputed lesion properties
        structureInfo = None
        with open(self.subjectFolder + "\\structure-def3.json") as fp: 
            structureInfo = json.load(fp)
        self.numberOfLesionElements = len(structureInfo)

        jsonTransformationMatrix = LesionUtils.getJsonDataTransformMatrix(self.subjectFolder)
        
        for jsonElementIndex in (range(1,self.numberOfLesionElements+1)):
            for p in structureInfo[str(jsonElementIndex)]:
                center = p["Centroid"]
                npixels = p["NumberOfPixels"]

                center.append(1)
                transformedCenter = list(np.matmul(center, jsonTransformationMatrix))
                transformedCenter.pop()
                self.lesionCentroids.append(transformedCenter)
                self.lesionNumberOfPixels.append(npixels)
                self.lesionElongation.append(p["Elongation"])
                self.lesionPerimeter.append(p["Perimeter"])
                self.lesionSphericalRadius.append(p["SphericalRadius"])
                self.lesionSphericalPerimeter.append(p["SphericalPerimeter"])
                self.lesionFlatness.append(p["Flatness"])
                self.lesionRoundness.append(p["Roundness"])
                self.lesionAverageIntensity.append(p["AverageLesionIntensity"])
                self.lesionAverageSurroundingIntensity.append(p["AverageSurroundingIntensity"])
                #self.lesionRegionNumberQuantized.append(p["RegionNumberQuantized"])
                self.lesionAffectedPointIdsLh.append(p["AffectedPointIdsLh"])
                self.lesionAffectedPointIdsRh.append(p["AffectedPointIdsRh"])
                self.lesionAverageLesionIntensityT1.append(p["AverageLesionIntensity"])
                self.lesionAverageSuroundingIntensityT1.append(p["AverageSurroundingIntensity"])
                self.lesionAverageLesionIntensityT2.append(p["AverageLesionIntensityT2"])
                self.lesionAverageSuroundingIntensityT2.append(p["AverageSurroundingIntensityT2"])
                self.lesionAverageLesionIntensityFLAIR.append(p["AverageLesionIntensityFLAIR"])
                self.lesionAverageSuroundingIntensityFLAIR.append(p["AverageSurroundingIntensityFLAIR"])

        self.style.addLesionData(self.subjectFolder, self.lesionCentroids, self.lesionNumberOfPixels, self.lesionElongation, self.lesionPerimeter, self.lesionSphericalRadius, self.lesionSphericalPerimeter, self.lesionFlatness, self.lesionRoundness, self.lesionSeededFiberTracts)

        self.requestedVisualizationType = str(self.comboBox_VisType.currentText())
        #self.lesionActors = LesionUtils.extractLesions(self.subjectFolder,self.numberOfLesionElements, self.informationKey,self.informationUniqueKey, self.requestedVisualizationType, self.lesionAverageIntensity, self.lesionAverageSurroundingIntensity, self.lesionRegionNumberQuantized, True)
        self.lesionActors = LesionUtils.extractLesions2(self.subjectFolder, self.informationUniqueKey)
        LesionUtils.lesionColorMapping(self.subjectFolder, self.numberOfLesionElements, self.requestedVisualizationType, self.lesionActors)
        for actor in self.lesionActors:
            self.actors.append(actor)
        # Also add lesions string to the loaded items listbox.
        item = QtGui.QStandardItem("lesions")
        item.setCheckable(True)
        item.setCheckState(2)
        self.modelListBoxSurfaces.appendRow(item)
        self.listView.setSelectionRectVisible(True)
        self.modelListBoxSurfaces.itemChanged.connect(self.on_itemChanged)

        # populate the user interface with the structure values
        #self.populateStructureInterface(structureInfo)

        # Compute lesion properties (Deprecated. TODO - Remove Safely)
        # connectedComponentImage, connectedComponentFilter = LesionUtils.computeLesionProperties(subjectFolder)

        translationFilePath = os.path.join(self.subjectFolder, "meta\\cras.txt")
        f = open(translationFilePath, "r")
        t_vector = []
        for t in f:
            t_vector.append(t)
        t_vector = list(map(float, t_vector))
        transform = vtk.vtkTransform()
        transform.PostMultiply()
        transform.Translate(t_vector[0], t_vector[1], t_vector[2])
        f.close()

        for i in range(len(fileNames)):

            # Check if files are wavefront OBJ and in the whitelist according to settings.
            if fileNames[i].endswith(".obj") and os.path.basename(fileNames[i]) in settings.getSurfaceWhiteList():
                loadFilePath = os.path.join(self.subjectFolder, fileNames[i])      
                reader = vtk.vtkOBJReader()
                reader.SetFileName(loadFilePath)
                reader.Update()
                mapper = vtk.vtkOpenGLPolyDataMapper()
                mapper.SetInputConnection(reader.GetOutputPort())
                #transform = vtk.vtkTransform()
                #transform.Identity()
                #mrmlDataFileName = open ( subjectFolder + "\\meta\\mrml.txt" , 'r')
                #arrayList = list(np.asfarray(np.array(mrmlDataFileName.readline().split(",")),float))
                #QFormMatrixT1 = self.niftyReaderT1.GetQFormMatrix()
                #qFormListT1 = [0] * 16 #the matrix is 4x4
                #QFormMatrixT1.DeepCopy(qFormListT1, QFormMatrixT1)
                #print(arrayList)
                #print(qFormListT1)
                #transform.SetMatrix(qFormListT1)
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                #transform.Identity()
                #actor.SetUserTransform(transform)

                information = vtk.vtkInformation()
                # Apply transparency settings and add information.
                if "lh.pial" in fileNames[i]:
                    actor.GetProperty().SetOpacity(settings.lh_pial_transparency)
                    information.Set(self.informationKey,"lh.pial")
                    self.lhpialMapper = mapper
                if "rh.pial" in fileNames[i]:
                    actor.GetProperty().SetOpacity(settings.rh_pial_transparency)
                    information.Set(self.informationKey,"rh.pial")
                    self.rhpialMapper = mapper
                if "lh.white" in fileNames[i]:
                    actor.GetProperty().SetOpacity(settings.lh_white_transparency)
                    information.Set(self.informationKey,"lh.white")
                    self.lhwhiteMapper = mapper
                if "rh.white" in fileNames[i]:
                    actor.GetProperty().SetOpacity(settings.rh_white_transparency)
                    information.Set(self.informationKey,"rh.white")
                    self.rhwhiteMapper = mapper

                if "pial" in fileNames[i] or "white" in fileNames[i]:
                    actor.SetUserTransform(transform)
                    #f.close()
                    if("rh.white" in fileNames[i]):
                        #self.rhwhite = actor
                        self.style.rhactor = actor  # TODO: Temporary code. To be removed soon.
                    if("lh.white" in fileNames[i]):
                        #self.lhwhite = actor
                        self.style.lhactor = actor  # TODO: Temporary code. To be removed soon.


                if(fileNames[i].endswith("lesions.obj")==False):
                    actor.GetProperty().SetInformation(information)
                    actor.GetProperty().SetColor(1, 0.964, 0.878)
                    self.actors.append(actor)
   
                # Also add to the listBox showing loaded surfaces.
                item = QtGui.QStandardItem(os.path.basename(fileNames[i]))
                item.setCheckable(True)
                item.setCheckState(2)      
                self.modelListBoxSurfaces.appendRow(item)
                self.listView.setSelectionRectVisible(True)
                self.modelListBoxSurfaces.itemChanged.connect(self.on_itemChanged)

        # Update overlay text and add it to the renderer
        self.overlayDataGlobal["Lesion Load"] = self.numberOfLesionElements
        self.overlayDataGlobal["Depth Peeling"] = "Enabled" if self.checkBox_DepthPeeling.isChecked() else "Disabled"
        LesionUtils.updateOverlayText(self.iren, self.overlayDataMain, self.overlayDataGlobal, self.textActorLesionStatistics, self.textActorGlobal)
        self.ren.AddActor2D(self.textActorLesionStatistics)
                        
        frameHeight = self.frame.frameRect().height()
        self.textActorGlobal.SetPosition(10, frameHeight-100)
        self.ren.AddActor2D(self.textActorGlobal)
        # Check if full streamline computation is requested.
        if(str(self.comboBox_VisType.currentText())=='Lesion Surface Mapping'):
            print("Computing streamlines")
            fiberActor = LesionUtils.computeStreamlines(self.subjectFolder)
            information = vtk.vtkInformation()
            information.Set(self.informationKey,"structural tracts")
            fiberActor.GetProperty().SetInformation(information)
            self.actors.append(fiberActor)
            item = QtGui.QStandardItem("structural tracts")
            item.setCheckable(True)
            item.setCheckState(2)      
            self.modelListBoxSurfaces.appendRow(item)

        # Add all actors to renderer.
        for a in self.actors:
            self.ren.AddActor(a)

        self.ren.ResetCamera()
        self.iren.Render()


        # End of performance log. Print elapsed time.
        print("--- %s seconds ---" % (time.time() - start_time))

    def updateLesionColorsContinuous(self):
        # visType = None
        # if(str(self.comboBox_VisType.currentText())=="Lesion Colored - Continuous"):
        #     visType = "Cont"
        # if(str(self.comboBox_VisType.currentText())=="Lesion Colored - Discrete"):
        #     visType = "Disc"
        # if(str(self.comboBox_VisType.currentText())=="Lesion Colored - Distance"):
        #     visType = "Dist"      
        modality = None
        if(self.buttonGroupModality.checkedButton().text() == "T1"):
            modality = "T1"
        if(self.buttonGroupModality.checkedButton().text() == "T2"):
            modality = "T2"
        if(self.buttonGroupModality.checkedButton().text() == "FLAIR"):
            modality = "FLAIR"

        colorFilePath = self.subjectFolder + "\\surfaces\\colorArrayCont" + modality + ".pkl"
        LesionUtils.loadColorFileAndAssignToLesions(colorFilePath, self.lesionActors)
        self.iren.Render()

    def updateLesionColorsDiscrete(self):
        thresholdMin = -10
        thresholdMax = 10
        numberOfLesions = len(self.lesionActors)
        for dataIndex in range(numberOfLesions):
            self.lesionActors[dataIndex].GetMapper().ScalarVisibilityOff()

            if(self.buttonGroupModality.checkedButton().text() == "T1"):
                intensityDifference = self.lesionAverageLesionIntensityT1[dataIndex] - self.lesionAverageSuroundingIntensityT1[dataIndex]
            if(self.buttonGroupModality.checkedButton().text() == "T2"):
                intensityDifference = self.lesionAverageLesionIntensityT2[dataIndex] - self.lesionAverageSuroundingIntensityT2[dataIndex]
            if(self.buttonGroupModality.checkedButton().text() == "FLAIR"):
                intensityDifference = self.lesionAverageLesionIntensityFLAIR[dataIndex] - self.lesionAverageSuroundingIntensityFLAIR[dataIndex]

            if(intensityDifference < thresholdMin):
                self.lesionActors[dataIndex].GetProperty().SetColor(103/255.0, 169/255.0, 207/255.0)
            if(intensityDifference >= thresholdMin and intensityDifference <=thresholdMax):
                self.lesionActors[dataIndex].GetProperty().SetColor(247/255.0, 247/255.0, 247/255.0)
            if(intensityDifference >= thresholdMax):
                self.lesionActors[dataIndex].GetProperty().SetColor(239/255.0, 138/255.0, 98/255.0)
        self.iren.Render()

    def updateLesionColorsDistance(self):
        colorFilePath = self.subjectFolder + "\\surfaces\\colorArrayDistMRI.pkl"
        LesionUtils.loadColorFileAndAssignToLesions(colorFilePath, self.lesionActors)
        self.iren.Render()

    # Handler for browse folder button click.
    @pyqtSlot()
    def on_click_browseFolder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file:
            self.lineEdit_DatasetFolder.setText(file)
            self.comboBox_AvailableSubjects.clear()
            dataFolders = [ name for name in os.listdir(file) if os.path.isdir(os.path.join(file, name)) ]
            for dataFolderName in dataFolders:
                self.comboBox_AvailableSubjects.addItem(dataFolderName)

    ##########################################
    # Handler for load data
    ##########################################
    @pyqtSlot()
    def on_click_LoadData(self):
        if(self.volumeDataLoaded==True):
            self.ren.RemoveVolume(self.volume) # Remove existing volume from scene.
            self.model_structural.removeRows(0,self.model_structural.rowCount())
        self.volumeDataLoaded=False # Initialize volume load status to false.
        self.stackedWidget_MainRenderers.setCurrentIndex(0) # Set current widget = large renderer
        self.checkBox_LesionMappingDualView.setCheckState(QtCore.Qt.Unchecked)
        self.dualLoadedOnce = False # Boolean indicating whether dual mode initialized atleast once.
        self.mainLoadedOnce = False # Boolean indicating whether main mode initialized atleast once.
        self.ren.RemoveAllViewProps() # Remove all actors from the list of actors before loading new subject data.
        self.modelListBoxSurfaces.removeRows(0, self.modelListBoxSurfaces.rowCount()) # Clear all elements in the surface listView.

        # Fetch required display settings.
        if(self.dataFolderInitialized==False or self.checkBox_persistSettings.isChecked() == False):
            self.settings = Settings.getSettings(Settings.visMapping(self.comboBox_VisType.currentText()))
            self.lesionFilterParamSettings = Settings.LesionFilterParamSettings(1000,1000,1000,1000,1000,1000,1000)

        subjectFolder = os.path.join(self.lineEdit_DatasetFolder.text(), str(self.comboBox_AvailableSubjects.currentText()))
        if subjectFolder:
            subjectFiles = [f for f in LesionUtils.getListOfFiles(subjectFolder) if os.path.isfile(os.path.join(subjectFolder, f))]
            self.renderData(subjectFiles, self.settings)  # Render the actual data
            # Initialize annotation data
            self.colorsRh, self.colorsLh, self.labelsRh, self.labelsLh, self.regionsRh, self.regionsLh, self.metaRh, self.metaLh, self.uniqueLabelsRh, self.uniqueLabelsLh, self.areaRh, self.areaLh, self.polyDataRh, self.polyDataLh = LesionUtils.initializeSurfaceAnnotationColors(subjectFolder, self.rhwhiteMapper, self.lhwhiteMapper)
            #self.colorsRh, self.colorsLh, self.labelsRh, self.labelsLh, self.regionsRh, self.regionsLh, self.metaRh, self.metaLh, self.uniqueLabelsRh, self.uniqueLabelsLh, self.areaRh, self.areaLh, self.polyDataRh, self.polyDataLh = LesionUtils.initializeSurfaceAnnotationColors(subjectFolder, self.rhpialMapper, self.lhpialMapper)
            # If parcellation enabled
            if self.checkBox_Parcellation.isChecked():
                self.rhwhiteMapper.ScalarVisibilityOn()
                self.rhwhiteMapper.GetInput().GetPointData().SetScalars(self.colorsRh)
                self.lhwhiteMapper.ScalarVisibilityOn()
                self.lhwhiteMapper.GetInput().GetPointData().SetScalars(self.colorsLh)

            self.style.labelsRh = self.labelsRh
            self.style.regionsRh = self.regionsRh
            self.style.metaRh = self.metaRh
            self.style.uniqueLabelsRh = self.uniqueLabelsRh
            self.style.areaRh = self.areaRh
            self.style.labelsLh = self.labelsLh
            self.style.regionsLh = self.regionsLh
            self.style.metaLh = self.metaLh
            self.style.uniqueLabelsLh = self.uniqueLabelsLh
            self.style.areaLh = self.areaLh
            self.style.polyDataRh = self.polyDataRh
            self.style.polyDataLh = self.polyDataLh
            self.style.renMapOutcome = self.renMapOutcome

        # Load orientation cube only once.
        if(self.dataFolderInitialized==False):
            # Render orientation cube.
            self.axesActor.SetXPlusFaceText('R')
            self.axesActor.SetXMinusFaceText('L')
            self.axesActor.SetYMinusFaceText('H')
            self.axesActor.SetYPlusFaceText('F')
            self.axesActor.SetZMinusFaceText('P')
            self.axesActor.SetZPlusFaceText('A')
            self.axesActor.GetTextEdgesProperty().SetColor(1,1,1)
            self.axesActor.GetTextEdgesProperty().SetLineWidth(1)
            self.axesActor.GetCubeProperty().SetColor(0.133,0.49,0.21)
            self.axes = vtk.vtkOrientationMarkerWidget()
            self.axes.SetOrientationMarker(self.axesActor)
            self.axes.SetViewport( 0.9, 0.9, 1.0, 1.0 )
            self.axes.SetCurrentRenderer(self.ren)
            self.axes.SetInteractor(self.iren)
            self.axes.EnabledOn()
            #self.axes.InteractiveOn()
        self.iren.Render()

        self.dataFolderInitialized=True
        # Handler for load data button click
   
    # Handler for load structural data
    @pyqtSlot()
    def on_click_LoadStructural(self):
        if(self.dataFolderInitialized==True and self.volumeDataLoaded==False):
            subjectFolder = os.path.join(self.lineEdit_DatasetFolder.text(), str(self.comboBox_AvailableSubjects.currentText()))

            t1StructuralNiftyFileName = subjectFolder + "\\structural\\T1.nii"
            #mrmlDataFileName = open ( subjectFolder + "\\meta\\mrml.txt" , 'r')
            niftiReader = vtk.vtkNIFTIImageReader()
            niftiReader.SetFileName(t1StructuralNiftyFileName)
            niftiReader.Update()
            QFormMatrixT1 = niftiReader.GetQFormMatrix()
            qFormListT1 = [0] * 16 #the matrix is 4x4
            QFormMatrixT1.DeepCopy(qFormListT1, QFormMatrixT1)

            ijkras_transform = vtk.vtkTransform()
            #arrayList = list(np.asfarray(np.array(mrmlDataFileName.readline().split(",")),float))
            ijkras_transform.SetMatrix(qFormListT1)
            ijkras_transform.Update()

            # Ray cast volume mapper
            volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
            volumeMapper.SetInputConnection(niftiReader.GetOutputPort())
            self.volume = vtk.vtkVolume()
            self.volume.SetMapper(volumeMapper)
            self.volume.SetUserTransform(ijkras_transform) # Apply the IJK to RAS and origin transform.
            opacityTransferFunction = vtk.vtkPiecewiseFunction()
            opacityTransferFunction.AddPoint(5,0.0)
            opacityTransferFunction.AddPoint(1500,0.1)
            volprop = vtk.vtkVolumeProperty()
            volprop.SetScalarOpacity(opacityTransferFunction)
            self.volume.SetProperty(volprop)
            self.ren.AddVolume(self.volume)
            # Add to list
            self.model_structural = QtGui.QStandardItemModel()
            item = QtGui.QStandardItem("T1.nii")
            item.setCheckable(True)
            item.setCheckState(2)      
            self.model_structural.appendRow(item)
            self.listView_Structural.setModel(self.model_structural)
            self.listView_Structural.setSelectionRectVisible(True)
            self.model_structural.itemChanged.connect(self.on_itemChanged_Structural)

            #mrmlDataFileName.close()

            self.iren.Render()
            self.volumeDataLoaded=True # Indicate that volume data is loaded properly.

    # Handler for checkbox check status change for surface data.
    @pyqtSlot(QtGui.QStandardItem)
    def on_itemChanged(self,  item):
        state = ['UNCHECKED', 'TRISTATE',  'CHECKED'][item.checkState()]
        if(state == 'UNCHECKED'):
            for actorItem in self.actors:
                if(actorItem.GetProperty().GetInformation().Get(self.informationKey) != None):
                    if actorItem.GetProperty().GetInformation().Get(self.informationKey) in item.text():
                        self.ren.RemoveActor(actorItem)
                    continue
                if(actorItem.GetProperty().GetInformation().Get(self.informationUniqueKey) != None):
                    if (actorItem.GetProperty().GetInformation().Get(self.informationUniqueKey).isdigit() and "lesions" in item.text()):
                        self.ren.RemoveActor(actorItem)
            self.frame.setLayout(self.vl)
            self.iren.Render()
        else:
            for actorItem in self.actors:
                if(actorItem.GetProperty().GetInformation().Get(self.informationKey) != None):
                    if actorItem.GetProperty().GetInformation().Get(self.informationKey) in item.text():
                        self.ren.AddActor(actorItem)
                    continue
                if(actorItem.GetProperty().GetInformation().Get(self.informationUniqueKey) != None):
                    if (actorItem.GetProperty().GetInformation().Get(self.informationUniqueKey).isdigit() and "lesions" in item.text()):
                        self.ren.AddActor(actorItem)
            self.frame.setLayout(self.vl)
            self.iren.Render()

    # Handler for checkbox check status change for structural data.
    @pyqtSlot(QtGui.QStandardItem)
    def on_itemChanged_Structural(self,  item):
        state = ['UNCHECKED', 'TRISTATE',  'CHECKED'][item.checkState()]
        if(state == 'UNCHECKED'):
            #removeIndex = item.index()
            self.ren.RemoveVolume(self.volume)
            #self.ren.ResetCamera()
            self.frame.setLayout(self.vl)
            self.iren.Render()
        else:
            #addIndex = item.index()
            self.ren.AddVolume(self.volume)
            #self.ren.ResetCamera()
            self.frame.setLayout(self.vl)
            self.iren.Render()

    # Handler for MPRA Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRA(self):
        # Setup the slide number text and add it to the renderer
        self.sliceNumberTextMPRA.SetInput(str(self.mprA_Slice_Slider.value()))
        self.resliceImageViewerMPRA.SetSlice(self.mprA_Slice_Slider.value())

    # Handler for MPRB Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRB(self):
        # Setup the slide number text and add it to the renderer
        self.sliceNumberTextMPRB.SetInput(str(self.mprB_Slice_Slider.value()))
        self.resliceImageViewerMPRB.SetSlice(self.mprB_Slice_Slider.value())

    # Handler for MPRC Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRC(self):
        # Setup the slide number text and add it to the renderer
        self.sliceNumberTextMPRC.SetInput(str(self.mprC_Slice_Slider.value()))
        self.resliceImageViewerMPRC.SetSlice(self.mprC_Slice_Slider.value())

    # Handler for Lesion Filter Slider change.
    @pyqtSlot()
    def on_sliderChangedLesionFilter(self):
        if(self.dataFolderInitialized == True):
            sliderValue = self.horizontalSliderLesionFilter.value()
            if (str(self.comboBox_LesionFilter.currentText())=="Voxel Count"):
                NewMax = max(self.lesionNumberOfPixels)
                NewMin = min(self.lesionNumberOfPixels)
                NewRange = NewMax - NewMin
                self.lesionFilterParamSettings.lesionNumberOfPixels = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionNumberOfPixels, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Elongation"):
                NewMax = max(self.lesionElongation)
                NewMin = min(self.lesionElongation)
                NewRange = NewMax - NewMin
                self.lesionFilterParamSettings.lesionElongation = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionElongation, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Perimeter"):
                NewMax = max(self.lesionPerimeter)
                NewMin = min(self.lesionPerimeter)
                NewRange = NewMax - NewMin
                self.lesionFilterParamSettings.lesionPerimeter = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionPerimeter, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Spherical Radius"):
                NewMax = max(self.lesionSphericalRadius)
                NewMin = min(self.lesionSphericalRadius)
                NewRange = NewMax - NewMin
                self.lesionFilterParamSettings.lesionSphericalRadius = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionSphericalRadius, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Spherical Perimeter"):
                NewMax = max(self.lesionSphericalPerimeter)
                NewMin = min(self.lesionSphericalPerimeter)
                NewRange = NewMax - NewMin
                self.lesionFilterParamSettings.lesionSphericalPerimeter = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionSphericalPerimeter, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Flatness"):
                NewMax = max(self.lesionFlatness)
                NewMin = min(self.lesionFlatness)
                NewRange = NewMax - NewMin
                self.lesionFilterParamSettings.lesionFlatness = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionFlatness, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Roundness"):
                NewMax = max(self.lesionRoundness)
                NewMin = min(self.lesionRoundness)
                NewRange = NewMax - NewMin
                self.lesionFilterParamSettings.lesionRoundness = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionRoundness, NewMax, NewMin)
            OldMin = 1
            OldMax = 1000
            OldValue = self.horizontalSliderLesionFilter.value()
            OldRange = 999
            NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
            self.label_lesionFilterCurrent.setText(str("{0:.2f}".format(NewValue)))

            # Filter lesions.
            LesionUtils.filterLesionsAndRender(removeIndices, self.actors, self.informationUniqueKey, self.ren)
            self.iren.Render()

    # Handler for modality change(slices and VR) inside button group
    @pyqtSlot(QAbstractButton)
    def on_buttonGroupModalityChanged(self, btn):
        if(self.dataFolderInitialized == True):
            if(btn.text()=="T1"):
                self.LoadStructuralSlices(self.subjectFolder, "T1")
                if(self.buttonGroupVis.checkedButton().text() == "Continuous"):
                    self.updateLesionColorsContinuous()
                if(self.buttonGroupVis.checkedButton().text() == "Discrete"):
                    self.updateLesionColorsDiscrete()
            if(btn.text()=="T2"):
                self.LoadStructuralSlices(self.subjectFolder, "T2")
                if(self.buttonGroupVis.checkedButton().text() == "Continuous"):
                    self.updateLesionColorsContinuous()
                if(self.buttonGroupVis.checkedButton().text() == "Discrete"):
                    self.updateLesionColorsDiscrete()
            if(btn.text()=="FLAIR"):
                self.LoadStructuralSlices(self.subjectFolder, "3DFLAIR")
                if(self.buttonGroupVis.checkedButton().text() == "Continuous"):
                    self.updateLesionColorsContinuous()
                if(self.buttonGroupVis.checkedButton().text() == "Discrete"):
                    self.updateLesionColorsDiscrete()

    # Handler for color visualization change inside button group
    @pyqtSlot(QAbstractButton)
    def on_buttonGroupVisChanged(self, btn):
        if(self.dataFolderInitialized == True):
            if(btn.text()=="Continuous"):
                self.updateLesionColorsContinuous()
            if(btn.text()=="Discrete"):
                self.updateLesionColorsDiscrete()
            if(btn.text()=="Distance"):
                self.updateLesionColorsDistance()

    # Handler for mode change inside button group
    @pyqtSlot(QAbstractButton)
    def on_buttonGroupModesChanged(self, btn):
        #print(btn.id())
        print(self.buttonGroupModes.checkedId())

    # Handler for Dial moved.
    @pyqtSlot()
    def on_DialMoved(self):
        if(self.dataFolderInitialized == True):
            self.opacityValueLabel.setText(str(self.dial.value()/float(500)))
            for actorItem in self.actors:
                if(actorItem.GetProperty().GetInformation().Get(self.informationKey) != None):
                    if(self.listView.model().itemFromIndex(self.listView.currentIndex()) == None):
                        return
                    if actorItem.GetProperty().GetInformation().Get(self.informationKey) in self.listView.model().itemFromIndex(self.listView.currentIndex()).text():
                        actorItem.GetProperty().SetOpacity(self.dial.value()/float(500))
                        break
            self.iren.Render()
            # Update settings.
            currentIndex = self.listView.currentIndex()
            if currentIndex.row() > -1:
                item = self.listView.model().itemFromIndex(currentIndex).text()
                if item is not None:
                    if item.endswith("lh.pial.obj"):
                        self.settings.lh_pial_transparency = self.dial.value()/float(500)
                    if item.endswith("rh.pial.obj"):
                        self.settings.rh_pial_transparency = self.dial.value()/float(500)
                    if item.endswith("lh.white.obj"):
                        self.settings.lh_white_transparency = self.dial.value()/float(500)
                    if item.endswith("rh.white.obj"):
                        self.settings.rh_white_transparency = self.dial.value()/float(500)

    # Handle when item selection in the surface list is changed.
    @pyqtSlot()
    def onSurfaceListSelectionChanged(self):
        currentIndex = self.listView.currentIndex()
        if currentIndex.row() > -1:
            item = self.listView.model().itemFromIndex(currentIndex).text()
            if item is not None:
                if item.endswith("lh.pial.obj"):
                    self.dial.setValue(self.settings.lh_pial_transparency*500)
                if item.endswith("rh.pial.obj"):
                    self.dial.setValue(self.settings.rh_pial_transparency*500)
                if item.endswith("lh.white.obj"):
                    self.dial.setValue(self.settings.lh_white_transparency*500)
                if item.endswith("rh.white.obj"):
                    self.dial.setValue(self.settings.rh_white_transparency*500)

    # Handler for unselecting all subjects at once-
    @pyqtSlot()
    def on_click_UnselectAllSubjects(self):
        model = self.listView.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.isCheckable() and item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
        self.iren.Render()

    # Handler for capturing the screenshot.
    @pyqtSlot()
    def on_click_CaptureScreeshot(self):
        LesionUtils.captureScreenshot(self.ren.GetRenderWindow())

    # Handler for depth peeling checkbox
    @pyqtSlot()
    def depthpeel_state_changed(self):
        if self.checkBox_DepthPeeling.isChecked():
            self.ren.SetUseDepthPeeling(True)
            self.ren.SetMaximumNumberOfPeels(4)
        else:
            self.ren.SetUseDepthPeeling(False)
        self.overlayDataGlobal["Depth Peeling"] = "Enabled" if self.checkBox_DepthPeeling.isChecked() else "Disabled"
        LesionUtils.updateOverlayText(self.iren, self.overlayDataMain, self.overlayDataGlobal, self.textActorLesionStatistics, self.textActorGlobal)
        self.iren.Render()

    # Handler for per lesion analysis.
    @pyqtSlot()
    def perLesion_state_changed(self):
        if self.checkBox_PerLesion.isChecked():
            self.lesionSeededFiberTracts = True
        else:
            self.lesionSeededFiberTracts = False

    # Handler for parcellation display
    @pyqtSlot()
    def parcellation_state_changed(self):
        print("READ", self.resliceImageViewerMPRA.GetColorWindow())
        print("READ", self.resliceImageViewerMPRA.GetColorLevel())

        if(self.dataFolderInitialized == True):
            if self.checkBox_Parcellation.isChecked():
                for actorItem in self.actors:
                    if(actorItem.GetProperty().GetInformation().Get(self.informationKey) != None):
                        if actorItem.GetProperty().GetInformation().Get(self.informationKey) in ["lh.pial", "lh.white"]:
                            actorItem.GetMapper().ScalarVisibilityOn()
                            actorItem.GetMapper().GetInput().GetPointData().SetScalars(self.colorsLh)
                        if actorItem.GetProperty().GetInformation().Get(self.informationKey) in ["rh.pial", "rh.white"]:
                            actorItem.GetMapper().ScalarVisibilityOn()
                            actorItem.GetMapper().GetInput().GetPointData().SetScalars(self.colorsRh)
            else:
                for actorItem in self.actors:
                    if(actorItem.GetProperty().GetInformation().Get(self.informationKey) != None):
                        if actorItem.GetProperty().GetInformation().Get(self.informationKey) in ["lh.pial", "lh.white", "rh.pial", "rh.white"]:
                            actorItem.GetMapper().ScalarVisibilityOff()
            if(self.dualLoadedOnce == True): # Update dual view also.
                self.lesionMapperDual.Refresh()
            self.iren.Render()

    # Handler for dual view mode.
    @pyqtSlot()
    def dual_view_state_changed(self):
        if(self.dataFolderInitialized == True):
            if self.checkBox_LesionMappingDualView.isChecked():
                self.stackedWidget_MainRenderers.setCurrentIndex(1)
                self.actorPropertiesMain = LesionUtils.saveActorProperties(self.actors) # Save actor properties of main.
                self.actorScalarPropertiesMain, self.actorScalarDataMain = LesionUtils.saveActorScalarDataProperties(self.actors)
                if(self.dualLoadedOnce==False):
                    self.lesionMapperDual = LesionMapper(self)
                    self.lesionMapperDual.ClearData()
                    self.lesionMapperDual.AddData()
                    #self.actorPropertiesDual = LesionUtils.saveActorProperties(self.actors)
                    self.dualLoadedOnce = True
                else:
                    LesionUtils.restoreActorProperties(self.actors, self.actorPropertiesDual)
                    LesionUtils.restoreActorScalarDataProperties(self.actors, self.actorScalarPropertiesDual, self.actorScalarDataDual)
            else:
                self.stackedWidget_MainRenderers.setCurrentIndex(0)
                if(self.mainLoadedOnce == True):
                    LesionUtils.restoreActorProperties(self.actors, self.actorPropertiesMain)
                    LesionUtils.restoreActorScalarDataProperties(self.actors, self.actorScalarPropertiesMain, self.actorScalarDataMain)
                self.actorPropertiesDual = LesionUtils.saveActorProperties(self.actors) # Save actor properties of dual.
                self.actorScalarPropertiesDual, self.actorScalarDataDual = LesionUtils.saveActorScalarDataProperties(self.actors)
                self.mainLoadedOnce = True
                if(self.checkBox_Parcellation.isChecked()):
                    self.rhwhiteMapper.GetInput().GetPointData().SetScalars(self.colorsRh)
                    self.lhwhiteMapper.GetInput().GetPointData().SetScalars(self.colorsLh)    
                #self.lesionMapperDual.RemoveData()
                # if self.checkBox_LesionMappingDualView.isChecked():
                #     if(self.vtkWidget.GetRenderWindow().HasRenderer(self.ren) == True):
                #         self.vtkWidget.GetRenderWindow().RemoveRenderer(self.ren)
                #     if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == True):
                #         self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renMapOutcome)
                #     self.vtkWidget.GetRenderWindow().AddRenderer(self.renDual)
                #     self.style.SetDefaultRenderer(self.renDual)
        self.iren.Render()

    # Handler for lesion filtering selected text changed.
    @pyqtSlot()
    def on_combobox_changed_LesionFilter(self): 
        if(self.dataFolderInitialized ==True):
            if (str(self.comboBox_LesionFilter.currentText())=="Voxel Count"):
                self.label_lesionFilterMin.setText(str(min(self.lesionNumberOfPixels)))
                self.label_lesionFilterMax.setText(str(max(self.lesionNumberOfPixels)))
                self.horizontalSliderLesionFilter.setValue(self.lesionFilterParamSettings.lesionNumberOfPixels)
            elif (str(self.comboBox_LesionFilter.currentText())=="Elongation"):
                self.label_lesionFilterMin.setText(str("{0:.2f}".format(min(self.lesionElongation))))
                self.label_lesionFilterMax.setText(str("{0:.2f}".format(max(self.lesionElongation))))
                self.horizontalSliderLesionFilter.setValue(self.lesionFilterParamSettings.lesionElongation)
            elif (str(self.comboBox_LesionFilter.currentText())=="Perimeter"):
                self.label_lesionFilterMin.setText(str("{0:.2f}".format(min(self.lesionPerimeter))))
                self.label_lesionFilterMax.setText(str("{0:.2f}".format(max(self.lesionPerimeter))))
                self.horizontalSliderLesionFilter.setValue(self.lesionFilterParamSettings.lesionPerimeter)
            elif (str(self.comboBox_LesionFilter.currentText())=="Spherical Radius"):
                self.label_lesionFilterMin.setText(str("{0:.2f}".format(min(self.lesionSphericalRadius))))
                self.label_lesionFilterMax.setText(str("{0:.2f}".format(max(self.lesionSphericalRadius))))
                self.horizontalSliderLesionFilter.setValue(self.lesionFilterParamSettings.lesionSphericalRadius)
            elif (str(self.comboBox_LesionFilter.currentText())=="Spherical Perimeter"):
                self.label_lesionFilterMin.setText(str("{0:.2f}".format(min(self.lesionSphericalPerimeter))))
                self.label_lesionFilterMax.setText(str("{0:.2f}".format(max(self.lesionSphericalPerimeter))))
                self.horizontalSliderLesionFilter.setValue(self.lesionFilterParamSettings.lesionSphericalPerimeter)
            elif (str(self.comboBox_LesionFilter.currentText())=="Flatness"):
                self.label_lesionFilterMin.setText(str("{0:.2f}".format(min(self.lesionFlatness))))
                self.label_lesionFilterMax.setText(str("{0:.2f}".format(max(self.lesionFlatness))))
                self.horizontalSliderLesionFilter.setValue(self.lesionFilterParamSettings.lesionFlatness)
            elif (str(self.comboBox_LesionFilter.currentText())=="Roundness"):
                self.label_lesionFilterMin.setText(str("{0:.2f}".format(min(self.lesionRoundness))))
                self.label_lesionFilterMax.setText(str("{0:.2f}".format(max(self.lesionRoundness))))
                self.horizontalSliderLesionFilter.setValue(self.lesionFilterParamSettings.lesionRoundness)
            OldRange = 999
        
    def closeEvent(self, event):
        print("Exiting program...")
        event.accept() # let the window close

    # define function to clear the terminal
    def clear(self): 
        # for windows 
        if name == 'nt': 
            _ = system('cls') 
        # for mac and linux(here, os.name is 'posix') 
        else: 
            _ = system('clear')

###########################################
# QApplication ############################
###########################################
app = QtWidgets.QApplication(sys.argv)
window = Ui()
sys.exit(app.exec_())