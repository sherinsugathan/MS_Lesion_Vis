#==========================================
# Title:  MS Lesion Visualization Project
# Author: Sherin Sugathan
# Last Modified Date:   14 Oct 2020
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
import TwoDModeMapper
from TwoDModeMapper import TwoDModeMapper
import ReportsMapper
from ReportsMapper import ReportsMapper
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
import nibabel as nib
import numpy as np
import numpy.ma as ma
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

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Pyinstaller exe requirements
#import pkg_resources.py2_warn
import vtkmodules
import vtkmodules.all
import vtkmodules.qt.QVTKRenderWindowInteractor
import vtkmodules.util
import vtkmodules.util.numpy_support

class Ui(Qt.QMainWindow):

    # Main Initialization
    def __init__(self):
        super(Ui, self).__init__()
        # Font initialization
        QtGui.QFontDatabase.addApplicationFont("asset/Google Sans Bold.ttf")
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
        uic.loadUi("asset\\lesionui.ui", self)
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
        vtk.vtkObject.GlobalWarningDisplayOff() # Supress warnings.
        self.pushButton_LoadFolder.clicked.connect(self.on_click_browseFolder) # Attaching button click Handlers
        self.pushButton_LoadData.clicked.connect(self.on_click_LoadData) # Attaching button click Handlers for load surfaces.
        self.pushButton_LoadStructural.clicked.connect(self.on_click_LoadStructural) # Attaching button click Handlers for load structural brain volumes.
        self.dial.setMinimum(0)
        self.dial.setMaximum(500)
        self.dial.setValue(500)
        self.dial.valueChanged.connect(self.on_DialMoved)
        self.pushButton_UnselectAllSubjects.clicked.connect(self.on_click_UnselectAllSubjects) # Attaching button click Handlers
        self.pushButton_DepthPeel.toggled.connect(self.depthpeel_toggled) # Attaching button click Handlers
        self.pushButton_Parcellation.toggled.connect(self.parcellation_toggled) # Attaching button click Handlers
        self.pushButton_PersistSettings.toggled.connect(self.persistSettings_toggled) # Attaching button toggle handlers.
        self.pushButton_EnableFibers.toggled.connect(self.fiberEnable_toggled) # Attaching button toggle handlers.
        self.pushButton_ResetView.clicked.connect(self.on_click_ResetViews) # Attaching button click Handlers
        self.pushButton_UpdateIntensityThreshold.clicked.connect(self.on_click_UpdateIntensityThreshold) # Attaching button click Handlers
        self.pushButton_Screenshot.clicked.connect(self.on_click_CaptureScreeshot) # Attaching button click Handlers
        self.pushButton_MappingTechnique.clicked.connect(self.on_click_MappingTechnique) # Attaching button click Handlers
        self.comboBox_LesionFilter.currentTextChanged.connect(self.on_combobox_changed_LesionFilter) # Attaching handler for lesion filter combobox selection change.

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
        self.horizontalSliderIntensityThreshold.valueChanged.connect(self.on_sliderChangedIntensityThreshold)

        exeRootPath = os.path.dirname(os.path.abspath(__file__))
        demoSubjectFolder = os.path.join(exeRootPath, "demoSubjectData")
        if(os.path.isdir(demoSubjectFolder)):
            self.lineEdit_DatasetFolder.setText(demoSubjectFolder)
            self.comboBox_AvailableSubjects.clear()
            dataFolders = [ name for name in os.listdir(demoSubjectFolder) if os.path.isdir(os.path.join(demoSubjectFolder, name)) ]
            for dataFolderName in dataFolders:
                self.comboBox_AvailableSubjects.addItem(dataFolderName)

        #pm = Qt.QPixmap("icons\\fundAndSupportLogos.png")
        #self.imageLabel.setPixmap(pm.scaled(self.imageLabel.size().width(), self.imageLabel.size().height(), 1,1))
        pmMain = Qt.QPixmap("icons\\AppLogo.png")
        self.logoLabel.setPixmap(pmMain.scaled(self.logoLabel.size().width(), self.logoLabel.size().height(), 1,1))

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
        print("Layout initialized")
        self.vl = Qt.QVBoxLayout()
        self.vl_MPRA = Qt.QVBoxLayout()
        self.vl_MPRB = Qt.QVBoxLayout()
        self.vl_MPRC = Qt.QVBoxLayout()
        self.vl_LesionMapDualLeft = Qt.QVBoxLayout()
        self.vl_LesionMapDualRight = Qt.QVBoxLayout()

        # Frame widgets
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkWidgetLesionMapDualLeft = QVTKRenderWindowInteractor(self.frame_DualLeft)
        self.vtkWidgetLesionMapDualRight = QVTKRenderWindowInteractor(self.frame_DualRight)

        self.figureMPRA = plt.figure(num = 0, frameon=False, clear=True)
        self.figureMPRA.subplots_adjust(bottom=0, top=1, left=0, right=1)
        self.figureMPRB = plt.figure(num = 1, frameon=False, clear=True)
        self.figureMPRB.subplots_adjust(bottom=0, top=1, left=0, right=1)
        self.figureMPRC = plt.figure(num = 2, frameon=False, clear=True)
        self.figureMPRC.subplots_adjust(bottom=0, top=1, left=0, right=1)
        self.canvasMPRA = FigureCanvas(self.figureMPRA)
        self.canvasMPRB = FigureCanvas(self.figureMPRB)
        self.canvasMPRC = FigureCanvas(self.figureMPRC)

        # Orientation cube.
        self.axesActor = vtk.vtkAnnotatedCubeActor()
        self.vl.addWidget(self.vtkWidget)
        self.vl_MPRA.addWidget(self.canvasMPRA)
        self.vl_MPRB.addWidget(self.canvasMPRB)
        self.vl_MPRC.addWidget(self.canvasMPRC)
        self.vl_LesionMapDualLeft.addWidget(self.vtkWidgetLesionMapDualLeft)
        self.vl_LesionMapDualRight.addWidget(self.vtkWidgetLesionMapDualRight)

        self.ren = vtk.vtkRenderer() # Renderer for volume
        self.renMapOutcome = vtk.vtkRenderer() # Renderer for displaying mapping outcomes.
        self.renDualLeft = vtk.vtkRenderer() # Renderer for dual view lesion map left
        self.renDualRight = vtk.vtkRenderer() # Renderer for dual view lesion map right

        self.renOrientationCube = vtk.vtkRenderer()
        self.ren.SetBackground(0.0039,0.0196,0.0078)
        
        #self.ren.SetViewport(self.VR_Viewport[0], self.VR_Viewport[1], self.VR_Viewport[2], self.VR_Viewport[3])
        self.renMapOutcome.SetViewport(self.parcellation_Viewport[0], self.parcellation_Viewport[1], self.parcellation_Viewport[2], self.parcellation_Viewport[3])
        self.renDualLeft.SetBackground(0.0039,0.0196,0.0078)
        self.renDualRight.SetBackground(0.0039,0.0196,0.0078)

        if self.pushButton_DepthPeel.isChecked():
            self.ren.SetUseDepthPeeling(True)
            self.ren.SetMaximumNumberOfPeels(4)

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

        self.vtkWidgetLesionMapDualLeft.GetRenderWindow().AddRenderer(self.renDualLeft)
        self.iren_LesionMapDualLeft = self.vtkWidgetLesionMapDualLeft.GetRenderWindow().GetInteractor()
        self.vtkWidgetLesionMapDualRight.GetRenderWindow().AddRenderer(self.renDualRight)
        self.iren_LesionMapDualRight = self.vtkWidgetLesionMapDualRight.GetRenderWindow().GetInteractor()

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
        #self.renMPRA.AddActor2D(self.sliceNumberTextMPRA)
        self.sliceNumberTextMPRB.UseBorderAlignOff()
        self.sliceNumberTextMPRB.SetPosition(0,0)
        self.sliceNumberTextMPRB.GetTextProperty().SetFontFamily(4)
        self.sliceNumberTextMPRB.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
        self.sliceNumberTextMPRB.GetTextProperty().SetFontSize(14)
        self.sliceNumberTextMPRB.GetTextProperty().ShadowOn()
        self.sliceNumberTextMPRB.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
        #self.renMPRB.AddActor2D(self.sliceNumberTextMPRB)
        self.sliceNumberTextMPRC.UseBorderAlignOff()
        self.sliceNumberTextMPRC.SetPosition(0,0)
        self.sliceNumberTextMPRC.GetTextProperty().SetFontFamily(4)
        self.sliceNumberTextMPRC.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
        self.sliceNumberTextMPRC.GetTextProperty().SetFontSize(14)
        self.sliceNumberTextMPRC.GetTextProperty().ShadowOn()
        self.sliceNumberTextMPRC.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
        #self.renMPRC.AddActor2D(self.sliceNumberTextMPRC)

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

        self.style = LesionUtils.MouseInteractorHighLightActor(self, None, self.iren, self.overlayDataMain, self.textActorLesionStatistics, self.overlayDataGlobal, self.textActorGlobal, self.informationKey, self.informationUniqueKey, self.lesionSeededFiberTracts, self.mprA_Slice_Slider, self.mprB_Slice_Slider, self.mprC_Slice_Slider)
        self.style.SetDefaultRenderer(self.ren)
        self.style.brodmannTextActor = self.brodmannTextActor
        self.style.vtkWidget = self.vtkWidget
        self.style.lesionvis = self
        self.style.renMapOutcome = self.renMapOutcome
        self.renMapOutcome.AddActor2D(self.brodmannTextActor)
        self.iren.SetInteractorStyle(self.style)

        self.ren.ResetCamera() # Main Renderer Camera Reset
        self.frame.setLayout(self.vl)
        #self.renMPRA.ResetCamera() # MPRA Camera Reset
        self.frame_MPRA.setLayout(self.vl_MPRA)
        #self.renMPRB.ResetCamera() # MPRB Camera Reset
        self.frame_MPRB.setLayout(self.vl_MPRB)
        #self.renMPRC.ResetCamera() # MPRC Camera Reset
        self.frame_MPRC.setLayout(self.vl_MPRC)
        self.renDualLeft.ResetCamera() # Lesion Mapping Dual Camera Left Reset
        self.frame_DualLeft.setLayout(self.vl_LesionMapDualLeft)
        self.renDualRight.ResetCamera() # Lesion Mapping Dual Camera Right Reset
        self.frame_DualRight.setLayout(self.vl_LesionMapDualRight)
        # self.ren2x2.ResetCamera() # 2x2 view camera reset
        # self.frame_2x2.setLayout(self.vl_lesion2x2)

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
        self.buttonGroupModes.addButton(self.pushButton_ReportsMode)
        self.buttonGroupModes.setExclusive(True)
        self.buttonGroupModes.buttonClicked.connect(self.on_buttonGroupModesChanged)

        # self.overlayPlaneMPRA = vtk.vtkPlane()
        # #self.overlayPlaneMPRA.SetOrigin(0,0,self.resliceImageViewerMPRA.GetSlice()+.75)
        # self.overlayPlaneMPRA.SetNormal(0, 0, 1)
        # self.mcfMPRA = vtk.vtkMarchingContourFilter()
        
        # self.overlayPlaneMPRB = vtk.vtkPlane()
        # #self.overlayPlaneMPRB.SetOrigin(0,0,self.resliceImageViewerMPRB.GetSlice()+.75)
        # self.overlayPlaneMPRB.SetNormal(0, 1, 0)
        # self.mcfMPRB = vtk.vtkMarchingContourFilter()

        # self.overlayPlaneMPRC = vtk.vtkPlane()
        # #self.overlayPlaneMPRC.SetOrigin(0,0,self.resliceImageViewerMPRC.GetSlice()+.75)
        # self.overlayPlaneMPRC.SetNormal(1, 0, 0)
        # self.mcfMPRC = vtk.vtkMarchingContourFilter()

        self.lesionMapperDual = None
        self.twoDModeMapper = None
        self.activeMode = -2
        self.streamlineComputed = False
        self.dtiDataActive = True

        self.figureMPRA.canvas.mpl_connect('scroll_event', self.onScrollMPRA)
        self.figureMPRB.canvas.mpl_connect('scroll_event', self.onScrollMPRB)
        self.figureMPRC.canvas.mpl_connect('scroll_event', self.onScrollMPRC)
        # self.iren_MPRA.AddObserver('MouseWheelForwardEvent', self.select_sliceMPRA, 1)
        # self.iren_MPRA.AddObserver('MouseWheelBackwardEvent', self.select_sliceMPRA, 1)
        # self.iren_MPRB.AddObserver('MouseWheelForwardEvent', self.select_sliceMPRB, 1)
        # self.iren_MPRB.AddObserver('MouseWheelBackwardEvent', self.select_sliceMPRB, 1)
        # self.iren_MPRC.AddObserver('MouseWheelForwardEvent', self.select_sliceMPRC, 1)
        # self.iren_MPRC.AddObserver('MouseWheelBackwardEvent', self.select_sliceMPRC, 1)

        self.show()
        self.iren.Initialize()
        # self.iren_MPRA.Initialize()
        # self.iren_MPRB.Initialize()
        # self.iren_MPRC.Initialize()
        self.iren_LesionMapDualLeft.Initialize()
        self.iren_LesionMapDualRight.Initialize()

        # Initialize 2d mapping mode
        self.twoDModeMapper = TwoDModeMapper(self)

        # Initialize reports mapping mode
        self.reportsMapper = ReportsMapper(self)

        self.imageLabel.hide()

        openglRendererInUse = self.ren.GetRenderWindow().ReportCapabilities().splitlines()[1].split(":")[1].strip()
        self.overlayDataGlobal["OpenGL Renderer"] = openglRendererInUse


    # Actvate controls after dataset is loaded.
    def activateControls(self):
        self.mprA_Slice_Slider.setEnabled(True)
        self.mprB_Slice_Slider.setEnabled(True)
        self.mprC_Slice_Slider.setEnabled(True)

    def onScrollMPRA(self, event):
        currentSlide = self.midSliceX
        if(event.button == 'up'):
            if(currentSlide + 1 <= self.data_dims[0]):
                self.midSliceX = self.midSliceX + 1
        if(event.button == 'down'):
            if(currentSlide - 1 > 0):
                self.midSliceX = self.midSliceX - 1
        self.mprA_Slice_Slider.setValue(self.midSliceX)

    def onScrollMPRB(self, event):
        currentSlide = self.midSliceY
        if(event.button == 'up'):
            if(currentSlide + 1 <= self.data_dims[1]):
                self.midSliceY = self.midSliceY + 1
        if(event.button == 'down'):
            if(currentSlide - 1 > 0):
                self.midSliceY = self.midSliceY - 1
        self.mprB_Slice_Slider.setValue(self.midSliceY)

    def onScrollMPRC(self, event):
        currentSlide = self.midSliceZ
        if(event.button == 'up'):
            if(currentSlide + 1 <= self.data_dims[2]):
                self.midSliceZ = self.midSliceZ + 1
        if(event.button == 'down'):
            if(currentSlide - 1 > 0):
                self.midSliceZ = self.midSliceZ - 1
        self.mprC_Slice_Slider.setValue(self.midSliceZ)

    # def select_sliceMPRA(self, caller, event):
    #     """
    #     This synchronizes our overlay plane
    #     """
    #     #self.overlayPlaneMPRA.SetOrigin(0, 0, self.resliceImageViewerMPRA.GetSlice()*self.spacing[2])
    #     #self.sliceNumberTextMPRA.SetInput(str(self.resliceImageViewerMPRA.GetSlice()))
    #     self.mprA_Slice_Slider.setValue(self.resliceImageViewerMPRA.GetSlice())

    # def select_sliceMPRB(self, caller, event):
    #     """
    #     This synchronizes our overlay plane
    #     """
    #     #self.overlayPlaneMPRB.SetOrigin(0, self.resliceImageViewerMPRB.GetSlice()*self.spacing[1], 0)
    #     self.mprB_Slice_Slider.setValue(self.resliceImageViewerMPRB.GetSlice())

    # def select_sliceMPRC(self, caller, event):
    #     """
    #     This synchronizes our overlay plane
    #     """
    #     #self.overlayPlaneMPRC.SetOrigin(self.resliceImageViewerMPRC.GetSlice()*self.spacing[0], 0, 0)
    #     self.mprC_Slice_Slider.setValue(self.resliceImageViewerMPRC.GetSlice())

    # def ScrollSlice(self, obj, ev):
    #     #print("Before Event")
    #     obj.OnMouseWheelForward()

    # action called by thte push button 
    def plotMPRs(self): 
        print("Calling plot")
        # clearing old figures
        self.figureMPRA.clear()
        plt.figure(0)
        # create an axis
        axMPRA = self.figureMPRA.add_subplot(111)
        plt.axis('off')
        plt.subplots_adjust(wspace=None, hspace=None)
        self.slice_MPRA = np.rot90(self.slice_MPRA)
        self.sliceMask_MPRA = np.rot90(self.sliceMask_MPRA)
        self.MPRA = plt.imshow(self.slice_MPRA, cmap='Greys_r', aspect='auto')
        self.MPRAMask = plt.imshow(self.sliceMask_MPRA, cmap='jet', alpha=0.5, aspect='auto',  interpolation='none')

        self.figureMPRB.clear()
        plt.figure(1)
        axMPRB = self.figureMPRB.add_subplot(111)
        plt.axis('off')
        plt.subplots_adjust(wspace=None, hspace=None)
        self.slice_MPRB = np.rot90(self.slice_MPRB)
        self.sliceMask_MPRB = np.rot90(self.sliceMask_MPRB)
        self.MPRB = plt.imshow(self.slice_MPRB, cmap='Greys_r', aspect='auto')
        self.MPRBMask = plt.imshow(self.sliceMask_MPRB, cmap='jet', alpha=0.5, aspect='auto',  interpolation='none')

        self.figureMPRC.clear()
        plt.figure(2)
        axMPRC = self.figureMPRC.add_subplot(111) 
        plt.axis('off')
        plt.subplots_adjust(wspace=None, hspace=None)
        self.slice_MPRC = np.rot90(self.slice_MPRC)
        self.sliceMask_MPRC = np.rot90(self.sliceMask_MPRC)
        self.MPRC = plt.imshow(self.slice_MPRC, cmap='Greys_r', aspect='auto')
        self.MPRCMask = plt.imshow(self.sliceMask_MPRC, cmap='jet', alpha=0.5, aspect='auto',  interpolation='none')


    # Load and Render Structural data as image slices.
    def LoadStructuralSlices(self, subjectFolder, modality, IsOverlayEnabled = False):
        if(True):
            fileName = subjectFolder + "\\structural\\"+modality+".nii"
            fileNameOverlay = subjectFolder + "\\lesionMask\\ConnectedComponents"+modality+"VoxelSpaceCorrected.nii"
            
            self.epi_img = nib.load(fileName)
            self.mask_img = nib.load(fileNameOverlay)
            self.epi_img_data = self.epi_img.get_fdata() # Read structural
            self.mask_data = self.mask_img.get_fdata() # Read mask data
            # Creating mask
            self.alpha_mask = ma.masked_where(self.mask_data <= 0, self.mask_data)
            self.alpha_mask[self.alpha_mask>0] = 255

            self.data_dims = self.epi_img_data.shape
            self.midSliceX = int(self.data_dims[0]/2)
            self.midSliceY = int(self.data_dims[1]/2)
            self.midSliceZ = int(self.data_dims[2]/2)
            ################################
            # MPR SLICES    ################
            ################################
            self.slice_MPRA = self.epi_img_data[self.midSliceX, :, :]
            self.slice_MPRB = self.epi_img_data[:, self.midSliceY, :]
            self.slice_MPRC = self.epi_img_data[:, :, self.midSliceZ]

            self.sliceMask_MPRA = self.alpha_mask[self.midSliceX, :, :]
            self.sliceMask_MPRB = self.alpha_mask[:, self.midSliceY, :]
            self.sliceMask_MPRC = self.alpha_mask[:, :, self.midSliceZ]

            # Plot the MPRs
            self.plotMPRs()

            self.mprA_Slice_Slider.setMaximum(self.data_dims[0]-1)
            self.mprB_Slice_Slider.setMaximum(self.data_dims[1]-1)
            self.mprC_Slice_Slider.setMaximum(self.data_dims[2]-1)

            self.mprA_Slice_Slider.setValue(self.midSliceX)
            self.mprB_Slice_Slider.setValue(self.midSliceY)
            self.mprC_Slice_Slider.setValue(self.midSliceZ)
        
    #####################################
    # MAIN LOADER: Load and Render Data #
    #####################################
    def renderData(self, fileNames, settings=None):
        # Performance log
        start_time = time.time()
        
        # Load data for MPRs.
        self.LoadStructuralSlices(self.subjectFolder, "T1", True)
        #self.comboBox_MPRModality.setCurrentIndex(0) # Default is T1   # TODO : Remove this old UI element

        # Clear combobox (mapping techniques)
        self.comboBox_MappingTechnique.clear()

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
        self.lesionAffectedPointIdsLhDTI = []
        self.lesionAffectedPointIdsRhDTI = []
        self.lesionAffectedPointIdsLhDanielsson = []
        self.lesionAffectedPointIdsRhDanielsson = []
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
                #center = p["Centroid"]
                npixels = p["NumberOfPixels"]
                #center.append(1)
                #transformedCenter = list(np.matmul(center, jsonTransformationMatrix))
                #transformedCenter.pop()
                #self.lesionCentroids.append(transformedCenter)
                self.lesionCentroids.append(p["Centroid"])
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
                self.lesionAffectedPointIdsLhDanielsson.append(p["AffectedPointIdsLhDanielsson"])
                self.lesionAffectedPointIdsRhDanielsson.append(p["AffectedPointIdsRhDanielsson"])

                self.lesionAverageLesionIntensityT1.append(p["AverageLesionIntensity"])
                self.lesionAverageSuroundingIntensityT1.append(p["AverageSurroundingIntensity"])
                if(self.dtiDataActive == False):
                    self.lesionAverageLesionIntensityT2.append(p["AverageLesionIntensityT2"])
                    self.lesionAverageSuroundingIntensityT2.append(p["AverageSurroundingIntensityT2"])
                    self.lesionAverageLesionIntensityFLAIR.append(p["AverageLesionIntensityFLAIR"])
                    self.lesionAverageSuroundingIntensityFLAIR.append(p["AverageSurroundingIntensityFLAIR"])
                else:
                    self.lesionAffectedPointIdsLhDTI.append(p["AffectedPointIdsLhDTI"])
                    self.lesionAffectedPointIdsRhDTI.append(p["AffectedPointIdsRhDTI"])
        
        self.LhMappingPolyData, self.RhMappingPolyData = LesionUtils.readDistanceMapPolyData(self.subjectFolder + "\\surfaces\\ProjectionSDM\\")
        self.streamActorsHE = LesionUtils.extractStreamlines(self.subjectFolder, self.informationKey, 1)
        self.streamActorsDanielsson = LesionUtils.extractStreamlines(self.subjectFolder, self.informationKey, 2)
        # print(len(self.streamActorsHE))
        # print(len(self.streamActorsDanielsson))
        self.streamActors = self.streamActorsHE
        if(self.dtiDataActive == True):
            self.comboBox_MappingTechnique.addItem("Diffusion")
            self.mappingType = "Diffusion"
            self.streamActorsDTI = LesionUtils.extractStreamlines(self.subjectFolder, self.informationKey, 0)
            self.streamActors = self.streamActorsDTI
        #else:
            #self.mappingType = "Heat Equation"
        self.comboBox_MappingTechnique.addItem("Heat Equation")  
        self.comboBox_MappingTechnique.addItem("Signed Distance Map")
        self.comboBox_MappingTechnique.addItem("Danielsson Distance")

        self.style.addLesionData(self.subjectFolder, self.lesionCentroids, self.lesionNumberOfPixels, self.lesionElongation, self.lesionPerimeter, self.lesionSphericalRadius, self.lesionSphericalPerimeter, self.lesionFlatness, self.lesionRoundness, self.lesionSeededFiberTracts)

        #self.requestedVisualizationType = str(self.comboBox_VisType.currentText())
        #self.lesionActors = LesionUtils.extractLesions(self.subjectFolder,self.numberOfLesionElements, self.informationKey,self.informationUniqueKey, self.requestedVisualizationType, self.lesionAverageIntensity, self.lesionAverageSurroundingIntensity, self.lesionRegionNumberQuantized, True)
        self.lesionActors = LesionUtils.extractLesions2(self.subjectFolder, self.informationUniqueKey)
        LesionUtils.lesionColorMapping(self.subjectFolder, self.lesionActors)

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
                #print(fileNames[i])
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

                if(fileNames[i].endswith("ventricleMesh.obj") == True):
                    LesionUtils.smoothSurface(actor)
                    actor.GetMapper().ScalarVisibilityOff()
                    actor.GetProperty().SetColor(0.5608, 0.7059, 0.5725)

                if(fileNames[i].endswith("lesions.obj")==False):
                    actor.GetProperty().SetInformation(information)
                    #actor.GetProperty().SetColor(1, 0.964, 0.878)
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
        self.overlayDataGlobal["Depth Peeling"] = "Enabled" if self.pushButton_DepthPeel.isChecked() else "Disabled"
        LesionUtils.updateOverlayText(self.iren, self.overlayDataMain, self.overlayDataGlobal, self.textActorLesionStatistics, self.textActorGlobal)
        self.ren.AddActor2D(self.textActorLesionStatistics)
                        
        frameHeight = self.frame.frameRect().height()
        self.textActorGlobal.SetPosition(10, frameHeight-100)
        self.ren.AddActor2D(self.textActorGlobal)

        # Check if full streamline computation is requested.
        if(False): # Enable to invoke streamline computation
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

        # Add legend
        self.legend = vtk.vtkLegendBoxActor()
        self.legend.SetNumberOfEntries(3)
        self.legendDistance = vtk.vtkLegendBoxActor()
        self.legendDistance.SetNumberOfEntries(4)
        self.overlayLegendTextProperty = vtk.vtkTextProperty()
        self.overlayLegendTextProperty.SetFontFamily(4)
        self.overlayLegendTextProperty.SetFontFile("fonts\\RobotoMono-Medium.ttf")
        self.overlayLegendTextProperty.SetFontSize(12)
        self.overlayLegendTextProperty.SetJustificationToLeft()
        self.legend.SetEntryTextProperty(self.overlayLegendTextProperty)
        self.legendDistance.SetEntryTextProperty(self.overlayLegendTextProperty)
        self.legendBox = vtk.vtkCubeSource()
        self.legendBox.Update()

        LesionUtils.setLegend(self.legendBox, self.legend, self.legendDistance, "continuous")
        self.ren.AddActor(self.legend)
        #legend.UseBackgroundOn()
        #egend.SetBackgroundColor(colors.GetColor3d("warm_grey"))

        self.ren.ResetCamera()
        self.iren.Render()


        # End of performance log. Print elapsed time.
        print("--- %s seconds ---" % (time.time() - start_time))

    def updateLesionColorsContinuous(self):   
        modality = None
        if(self.buttonGroupModality.checkedButton().text() == "T1 DATA"):
            modality = "T1"
        if(self.buttonGroupModality.checkedButton().text() == "T2 DATA"):
            modality = "T2"
        if(self.buttonGroupModality.checkedButton().text() == "T2 FLAIR DATA"):
            modality = "FLAIR"

        colorFilePath = self.subjectFolder + "\\surfaces\\colorArrayCont" + modality + ".pkl"
        LesionUtils.loadColorFileAndAssignToLesions(colorFilePath, self.lesionActors)

        self.ren.RemoveActor(self.legendDistance)
        self.ren.AddActor(self.legend)

        LesionUtils.setLegend(self.legendBox, self.legend, self.legendDistance, "continuous")
        self.iren.Render()

    def updateLesionColorsDiscrete(self):
        thresholdMin = -10
        thresholdMax = 10
        numberOfLesions = len(self.lesionActors)
        for dataIndex in range(numberOfLesions):
            self.lesionActors[dataIndex].GetMapper().ScalarVisibilityOff()
            if(self.buttonGroupModality.checkedButton().text() == "T1 DATA"):
                intensityDifference = self.lesionAverageLesionIntensityT1[dataIndex] - self.lesionAverageSuroundingIntensityT1[dataIndex]
            if(self.buttonGroupModality.checkedButton().text() == "T2 DATA"):
                intensityDifference = self.lesionAverageLesionIntensityT2[dataIndex] - self.lesionAverageSuroundingIntensityT2[dataIndex]
            if(self.buttonGroupModality.checkedButton().text() == "T2 FLAIR DATA"):
                intensityDifference = self.lesionAverageLesionIntensityFLAIR[dataIndex] - self.lesionAverageSuroundingIntensityFLAIR[dataIndex]

            if(intensityDifference < thresholdMin):
                self.lesionActors[dataIndex].GetProperty().SetColor(103/255.0, 169/255.0, 207/255.0)
            if(intensityDifference >= thresholdMin and intensityDifference <=thresholdMax):
                self.lesionActors[dataIndex].GetProperty().SetColor(247/255.0, 247/255.0, 247/255.0)
            if(intensityDifference >= thresholdMax):
                self.lesionActors[dataIndex].GetProperty().SetColor(239/255.0, 138/255.0, 98/255.0)
        
        self.ren.RemoveActor(self.legendDistance)
        self.ren.AddActor(self.legend)

        LesionUtils.setLegend(self.legendBox, self.legend, self.legendDistance, "discrete")
        self.iren.Render()

    def updateLesionColorsDistance(self):
        colorFilePath = self.subjectFolder + "\\surfaces\\colorArrayDistMRI2.pkl"
        LesionUtils.loadColorFileAndAssignToLesions(colorFilePath, self.lesionActors)
        
        LesionUtils.setLegend(self.legendBox, self.legend, self.legendDistance, "distance")
        self.ren.RemoveActor(self.legend)
        self.ren.AddActor(self.legendDistance)
        # self.legend.SetNumberOfEntries(4)
        # self.legend.SetEntryString(0, "REGION 0")
        # self.legend.SetEntryString(1, "REGION 1")
        # self.legend.SetEntryString(2, "REGION 2")
        # self.legend.SetEntryString(3, "REGION 3")
        # self.legend.SetEntryColor(0, [166/255,206/255,227/255])
        # self.legend.SetEntryColor(1, [27/255,158/255,119/255])
        # self.legend.SetEntryColor(2, [217/255,95/255,2/255])
        # self.legend.SetEntryColor(3, [117/255,112/255,179/255])        
        # self.legend.SetPosition2(0.1,0.1)
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
        self.subjectFolder = os.path.join(self.lineEdit_DatasetFolder.text(), str(self.comboBox_AvailableSubjects.currentText()))
        if(self.comboBox_AvailableSubjects.count() == 0):
            return
        if(self.volumeDataLoaded==True):
            self.ren.RemoveVolume(self.volume) # Remove existing volume from scene.
            self.model_structural.removeRows(0,self.model_structural.rowCount())
        self.volumeDataLoaded=False # Initialize volume load status to false.
        self.initializeModeButtons()
        self.stackedWidget_MainRenderers.setCurrentIndex(0) # Set current widget = large renderer
        self.dualLoadedOnce = False # Initialize Boolean indicating whether dual mode initialized atleast once.
        self.mainLoadedOnce = False # Initialize Boolean indicating whether main mode initialized atleast once.
        self.twoDModeLoadedOnce = False # Initialize Boolean indicating whether 2D mode initialized atleast once.
        self.reportsModeLoadedOnce = False # Initialize Boolean indicating whether reports mode initialized atleast once.
        self.ren.RemoveAllViewProps() # Remove all actors from the list of actors before loading new subject data.
        self.modelListBoxSurfaces.removeRows(0, self.modelListBoxSurfaces.rowCount()) # Clear all elements in the surface listView.

        # Fetch required display settings.
        if(self.dataFolderInitialized==False or self.pushButton_PersistSettings.isChecked() == False):
            self.settings = Settings.getSettings(Settings.visMapping("Lesion Colored - Continuous"))
            self.lesionFilterParamSettings = Settings.LesionFilterParamSettings(1000,1000,1000,1000,1000,1000,1000)

        subjectFolder = os.path.join(self.lineEdit_DatasetFolder.text(), str(self.comboBox_AvailableSubjects.currentText()))
        if subjectFolder:
            if(LesionUtils.checkForDTIData(subjectFolder)):
                self.dtiDataActive = True
            else:
                self.dtiDataActive = False
            subjectFiles = [f for f in LesionUtils.getListOfFiles(subjectFolder) if os.path.isfile(os.path.join(subjectFolder, f))]
            self.renderData(subjectFiles, self.settings)  # Render the actual data
            # Initialize annotation data
            self.colorsRh, self.colorsLh, self.labelsRh, self.labelsLh, self.regionsRh, self.regionsLh, self.metaRh, self.metaLh, self.uniqueLabelsRh, self.uniqueLabelsLh, self.areaRh, self.areaLh, self.polyDataRh, self.polyDataLh = LesionUtils.initializeSurfaceAnnotationColors(subjectFolder, self.rhwhiteMapper, self.lhwhiteMapper)
            #self.colorsRh, self.colorsLh, self.labelsRh, self.labelsLh, self.regionsRh, self.regionsLh, self.metaRh, self.metaLh, self.uniqueLabelsRh, self.uniqueLabelsLh, self.areaRh, self.areaLh, self.polyDataRh, self.polyDataLh = LesionUtils.initializeSurfaceAnnotationColors(subjectFolder, self.rhpialMapper, self.lhpialMapper)
            # If parcellation enabled
            if self.pushButton_Parcellation.isChecked():
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

        self.streamlineComputed = False
        self.pushButton_EnableFibers.setChecked(True) # default when data loaded.
        self.activateControls() # Activate applicable UI controls.
        self.dataFolderInitialized=True
   
    # Handler for load structural data
    @pyqtSlot()
    def on_click_LoadStructural(self):
        if(self.dataFolderInitialized==True and self.volumeDataLoaded==False):
            subjectFolder = os.path.join(self.lineEdit_DatasetFolder.text(), str(self.comboBox_AvailableSubjects.currentText()))

            t1StructuralNiftyFileName = subjectFolder + "\\structural\\T1.nii"
            niftiReader = vtk.vtkNIFTIImageReader()
            niftiReader.SetFileName(t1StructuralNiftyFileName)
            niftiReader.Update()
            QFormMatrixT1 = niftiReader.GetQFormMatrix()
            qFormListT1 = [0] * 16 #the matrix is 4x4
            QFormMatrixT1.DeepCopy(qFormListT1, QFormMatrixT1)

            ijkras_transform = vtk.vtkTransform()
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
        plt.figure(0)
        self.midSliceX = self.mprA_Slice_Slider.value()
        self.slice_MPRA = np.rot90(self.epi_img_data[self.midSliceX, :, :])
        self.sliceMask_MPRA = np.rot90(self.alpha_mask[self.midSliceX, :, :])
        self.MPRA.set_data(self.slice_MPRA)
        self.MPRAMask.set_data(self.sliceMask_MPRA)
        self.canvasMPRA.draw()

    # Handler for MPRB Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRB(self):
        plt.figure(1)
        self.midSliceY = self.mprB_Slice_Slider.value()
        self.slice_MPRB = np.rot90(self.epi_img_data[:, self.midSliceY, :])
        self.sliceMask_MPRB = np.rot90(self.alpha_mask[:, self.midSliceY, :])
        self.MPRB.set_data(self.slice_MPRB)
        self.MPRBMask.set_data(self.sliceMask_MPRB)
        
        self.canvasMPRB.draw()

    # Handler for MPRC Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRC(self):
        plt.figure(2)
        self.midSliceZ = self.mprC_Slice_Slider.value()
        self.slice_MPRC = np.rot90(self.epi_img_data[:, :, self.midSliceZ])
        self.sliceMask_MPRC = np.rot90(self.alpha_mask[:, :, self.midSliceZ])
        self.MPRC.set_data(self.slice_MPRC)
        self.MPRCMask.set_data(self.sliceMask_MPRC)
        self.canvasMPRC.draw()

    # Handler for Intensity Threshold Slider change.
    @pyqtSlot()
    def on_sliderChangedIntensityThreshold(self):
        if(self.dataFolderInitialized == True):
            sliderValue = self.horizontalSliderIntensityThreshold.value()
            self.label_IntensityThreshold.setText(str(sliderValue))

    # Handler for Lesion Filter Slider change.
    @pyqtSlot()
    def on_sliderChangedLesionFilter(self):
        if(self.comboBox_LesionFilter.currentIndex()==0):
            return
        if(self.dataFolderInitialized == True):
            sliderValue = self.horizontalSliderLesionFilter.value()
            if (str(self.comboBox_LesionFilter.currentText())=="Voxel Count"):
                NewMax = max(self.lesionNumberOfPixels)
                NewMin = min(self.lesionNumberOfPixels)
                self.lesionFilterParamSettings.lesionNumberOfPixels = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionNumberOfPixels, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Elongation"):
                NewMax = max(self.lesionElongation)
                NewMin = min(self.lesionElongation)
                self.lesionFilterParamSettings.lesionElongation = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionElongation, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Perimeter"):
                NewMax = max(self.lesionPerimeter)
                NewMin = min(self.lesionPerimeter)
                self.lesionFilterParamSettings.lesionPerimeter = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionPerimeter, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Spherical Radius"):
                NewMax = max(self.lesionSphericalRadius)
                NewMin = min(self.lesionSphericalRadius)
                self.lesionFilterParamSettings.lesionSphericalRadius = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionSphericalRadius, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Spherical Perimeter"):
                NewMax = max(self.lesionSphericalPerimeter)
                NewMin = min(self.lesionSphericalPerimeter)
                self.lesionFilterParamSettings.lesionSphericalPerimeter = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionSphericalPerimeter, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Flatness"):
                NewMax = max(self.lesionFlatness)
                NewMin = min(self.lesionFlatness)
                self.lesionFilterParamSettings.lesionFlatness = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionFlatness, NewMax, NewMin)
            elif (str(self.comboBox_LesionFilter.currentText())=="Roundness"):
                NewMax = max(self.lesionRoundness)
                NewMin = min(self.lesionRoundness)
                self.lesionFilterParamSettings.lesionRoundness = sliderValue
                removeIndices = LesionUtils.getThresholdLesionIndices(sliderValue, self.lesionRoundness, NewMax, NewMin)
            OldMin = 1
            OldMax = 1000
            OldValue = self.horizontalSliderLesionFilter.value()
            NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
            self.label_lesionFilterCurrent.setText(str("{0:.2f}".format(NewValue)))

            # Filter lesions.
            LesionUtils.filterLesionsAndRender(removeIndices, self.actors, self.informationUniqueKey, self.ren)
            self.iren.Render()

    # Handler for modality change(slices and VR) inside button group
    @pyqtSlot(QAbstractButton)
    def on_buttonGroupModalityChanged(self, btn):
        if(self.dataFolderInitialized == True):
            if(btn.text()=="T1 DATA"):
                self.LoadStructuralSlices(self.subjectFolder, "T1")
                if(self.buttonGroupVis.checkedButton().text() == "CONTINUOUS"):
                    self.updateLesionColorsContinuous()
                if(self.buttonGroupVis.checkedButton().text() == "DISCRETE"):
                    self.updateLesionColorsDiscrete()
            if(btn.text()=="T2 DATA"):
                self.LoadStructuralSlices(self.subjectFolder, "T2")
                if(self.buttonGroupVis.checkedButton().text() == "CONTINUOUS"):
                    self.updateLesionColorsContinuous()
                if(self.buttonGroupVis.checkedButton().text() == "DISCRETE"):
                    self.updateLesionColorsDiscrete()
            if(btn.text()=="FLAIR DATA"):
                self.LoadStructuralSlices(self.subjectFolder, "3DFLAIR")
                if(self.buttonGroupVis.checkedButton().text() == "CONTINUOUS"):
                    self.updateLesionColorsContinuous()
                if(self.buttonGroupVis.checkedButton().text() == "DISCRETE"):
                    self.updateLesionColorsDiscrete()

    # Handler for color visualization change inside button group
    @pyqtSlot(QAbstractButton)
    def on_buttonGroupVisChanged(self, btn):
        if(self.dataFolderInitialized == True):
            if(btn.text()=="CONTINUOUS"):
                self.pushButton_T1.setEnabled(True)
                self.pushButton_T2.setEnabled(True)
                self.pushButton_FLAIR.setEnabled(True)
                self.updateLesionColorsContinuous()
            if(btn.text()=="DISCRETE"):
                self.pushButton_T1.setEnabled(True)
                self.pushButton_T2.setEnabled(True)
                self.pushButton_FLAIR.setEnabled(True)
                self.updateLesionColorsDiscrete()
            if(btn.text()=="DISTANCE"):
                self.pushButton_T1.setEnabled(False)
                self.pushButton_T2.setEnabled(False)
                self.pushButton_FLAIR.setEnabled(False)
                self.updateLesionColorsDistance()

    # Handler for mode change inside button group
    @pyqtSlot(QAbstractButton)
    def on_buttonGroupModesChanged(self, btn):
        #print(btn.id())
        #print(self.buttonGroupModes.checkedId())
        if(self.dataFolderInitialized == True):
            if(self.buttonGroupModes.checkedId() == -2): # Normal Mode
                self.stackedWidget_MainRenderers.setCurrentIndex(0)
                self.activateMainMode()
                self.activeMode = -2

            if(self.buttonGroupModes.checkedId() == -3): # Dual Mode
                self.stackedWidget_MainRenderers.setCurrentIndex(1)
                self.activateDualMode()
                self.activeMode = -3

            if(self.buttonGroupModes.checkedId() == -4): # 2D Mode
                self.stackedWidget_MainRenderers.setCurrentIndex(2)
                self.activate2DMode()
                self.activeMode = -4

            if(self.buttonGroupModes.checkedId() == -5): # Reports Mode
                self.activateReportsMode()
                self.stackedWidget_MainRenderers.setCurrentIndex(3)
                self.activeMode = -5

            self.iren.Render()

    # Activate renderers in main mode
    def activateMainMode(self):
        self.mainLoadedOnce = True
        for actor in self.actors:
            itemType = actor.GetProperty().GetInformation().Get(self.informationKey)
            if(itemType == None):
                pass
            else:
                actor.GetMapper().ScalarVisibilityOff() # No color mapping in main mode
                if(actor.GetProperty().GetInformation().Get(self.informationKey) in ["lh.pial"]):
                    actor.GetProperty().SetOpacity(self.settings.lh_pial_transparency)
                if(actor.GetProperty().GetInformation().Get(self.informationKey) in ["lh.white"]):
                    actor.GetProperty().SetOpacity(self.settings.lh_white_transparency)
                if(actor.GetProperty().GetInformation().Get(self.informationKey) in ["rh.pial"]):
                    actor.GetProperty().SetOpacity(self.settings.rh_pial_transparency)               
                if(actor.GetProperty().GetInformation().Get(self.informationKey) in ["rh.white"]):
                    actor.GetProperty().SetOpacity(self.settings.rh_white_transparency)
                #self.lesionvis.renDualRight.AddActor(actor)
            # Reset legend positions
            self.legend.SetPosition(0.9, 0.01)
            self.legend.SetPosition2(0.1,0.1)

        if(self.activeMode == -3 and self.style != None):
            self.style.LastPickedActor = self.lesionMapperDual.interactionStyleLeft.LastPickedActor
            self.style.LastPickedProperty = self.lesionMapperDual.interactionStyleLeft.LastPickedProperty
        if(self.activeMode == -4 and self.style != None):
            self.style.LastPickedActor = self.twoDModeMapper.customInteractorStyle.LastPickedActor
            self.style.LastPickedProperty = self.twoDModeMapper.customInteractorStyle.LastPickedProperty        
        #print("Loaded Main Mode")

    # Activate renderers in dual mode
    def activateDualMode(self):
        #self.actorPropertiesMain = LesionUtils.saveActorProperties(self.actors) # Save actor properties of main.
        #self.actorScalarPropertiesMain, self.actorScalarDataMain = LesionUtils.saveActorScalarDataProperties(self.actors)
        #print("Activating dual mode")
        if(self.dualLoadedOnce==False):
            self.lesionMapperDual = LesionMapper(self)
            self.lesionMapperDual.ClearData()
            self.lesionMapperDual.AddData()
            self.dualLoadedOnce = True
            return

        for actor in self.actors:
            itemType = actor.GetProperty().GetInformation().Get(self.informationKey)
            if(itemType == None):
                pass
            else:
                actor.GetProperty().SetOpacity(1)
                actor.GetMapper().ScalarVisibilityOn() # Color mapping enabled for dual mode      
        # Reset legend positions
        self.legend.SetPosition(0.8, 0.01)
        self.legend.SetPosition2(0.2,0.1) 

        if(self.activeMode == -2 and self.lesionMapperDual != None):
            self.lesionMapperDual.interactionStyleLeft.LastPickedActor = self.style.LastPickedActor
            self.lesionMapperDual.interactionStyleLeft.LastPickedProperty = self.style.LastPickedProperty
        if(self.activeMode == -4 and self.lesionMapperDual != None):
            self.lesionMapperDual.interactionStyleLeft.LastPickedActor = self.twoDModeMapper.customInteractorStyle.LastPickedActor
            self.lesionMapperDual.interactionStyleLeft.LastPickedProperty = self.twoDModeMapper.customInteractorStyle.LastPickedProperty         

    # Activate renderers in 2D mode
    def activate2DMode(self):
        #print(self.twoDModeLoadedOnce)
        if(self.twoDModeLoadedOnce == False):
            #self.twoDModeMapper = TwoDModeMapper(self)
            self.twoDModeMapper.ClearData()
            self.twoDModeMapper.AddData()
            self.twoDModeLoadedOnce = True

        if(self.activeMode == -2 and self.twoDModeMapper != None):
            self.twoDModeMapper.customInteractorStyle.LastPickedActor = self.style.LastPickedActor
            self.twoDModeMapper.customInteractorStyle.LastPickedProperty = self.style.LastPickedProperty
        if(self.activeMode == -3 and self.twoDModeMapper != None):
            self.twoDModeMapper.customInteractorStyle.LastPickedActor = self.lesionMapperDual.interactionStyleLeft.LastPickedActor
            self.twoDModeMapper.customInteractorStyle.LastPickedProperty = self.lesionMapperDual.interactionStyleLeft.LastPickedProperty

    # Activate renderers in Reports mode
    def activateReportsMode(self):
        print("Activated reports mode")
        if(self.reportsModeLoadedOnce == False):
            self.reportsMapper.AddData()
            self.reportsModeLoadedOnce = True


    # Initialize mode buttons.
    def initializeModeButtons(self):
        modalityButtons = self.buttonGroupModality.buttons()
        visButtons = self.buttonGroupVis.buttons()
        modeButtons = self.buttonGroupModes.buttons()
        if(os.path.isfile(self.subjectFolder + "\\structural\\T1.nii")):
            modalityButtons[0].setEnabled(True)
        else:
            modalityButtons[0].setEnabled(False)
        if(os.path.isfile(self.subjectFolder + "\\structural\\T2.nii")):
            modalityButtons[1].setEnabled(True)
        else:
            modalityButtons[1].setEnabled(False)
        if(os.path.isfile(self.subjectFolder + "\\structural\\FLAIR.nii")):
            modalityButtons[2].setEnabled(True)
        else:
            modalityButtons[2].setEnabled(False)

        for btn in modalityButtons:
            if(btn.isEnabled):
                btn.setChecked(True)
                break
        for btn in visButtons:
            btn.setChecked(True)
            break
        for btn in modeButtons:
            btn.setChecked(True)
            break

    # Handler for Dial moved.
    @pyqtSlot()
    def on_DialMoved(self):
        if(self.dataFolderInitialized == True):
            self.opacityValueLabel.setText(str('{0:.2f}'.format(self.dial.value()/float(500))))
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
        if(self.activeMode == -2):
            LesionUtils.captureScreenshot(self.ren.GetRenderWindow())
        if(self.activeMode == -3):
            LesionUtils.captureScreenshot(self.renDualLeft.GetRenderWindow())
            LesionUtils.captureScreenshot(self.renDualRight.GetRenderWindow())
        if(self.activeMode == -4):
            LesionUtils.captureScreenshot(self.twoDModeMapper.rendererLesion.GetRenderWindow())
            LesionUtils.captureScreenshot(self.twoDModeMapper.rendererUnfoldedRh.GetRenderWindow())
            LesionUtils.captureScreenshot(self.twoDModeMapper.rendererUnfoldedLh.GetRenderWindow())

    # Handler for changing the mapping technique.
    @pyqtSlot()
    def on_click_MappingTechnique(self):
        self.mappingType = str(self.comboBox_MappingTechnique.currentText())
        if(self.mappingType == "Diffusion"):
            self.streamActors = self.streamActorsDTI
        if(self.mappingType == "Heat Equation"):
            self.streamActors = self.streamActorsHE
        if(self.mappingType == "Signed Distance Map"):
            self.streamActors = None
        if(self.mappingType == "Danielsson Distance"):
            self.streamActors = self.streamActorsDanielsson

        if(self.dualLoadedOnce == True):
            self.lesionMapperDual.updateMappingDisplay()
        if(self.twoDModeLoadedOnce == True):
            self.twoDModeMapper.updateMappingDisplay()

    # Handler for depth peeling pushbutton 
    @pyqtSlot(bool)
    def depthpeel_toggled(self, checkStatus):
        if (checkStatus == True):
            self.ren.SetUseDepthPeeling(True)
            self.ren.SetMaximumNumberOfPeels(4)
        else:
            self.ren.SetUseDepthPeeling(False)
        self.overlayDataGlobal["Depth Peeling"] = "Enabled" if checkStatus else "Disabled"
        LesionUtils.updateOverlayText(self.iren, self.overlayDataMain, self.overlayDataGlobal, self.textActorLesionStatistics, self.textActorGlobal)
        self.iren.Render()

    # Handler for persist settings
    @pyqtSlot(bool)
    def persistSettings_toggled(self, checkStatus):
        if (checkStatus == True):
            print("TODO: Handle persist settings")

    # Handler for updating intensity threshold.
    @pyqtSlot()
    def on_click_UpdateIntensityThreshold(self):
        sliderValue = self.horizontalSliderIntensityThreshold.value()
        LesionUtils.updateContinuousColorData(self.subjectFolder, int(sliderValue))
        self.updateLesionColorsContinuous()

    # Handler for reset camera pushbutton 
    @pyqtSlot()
    def on_click_ResetViews(self):
        self.ren.ResetCamera()
        self.iren.Render()

    # Handler for per lesion analysis.
    @pyqtSlot(bool)
    def fiberEnable_toggled(self, checkStatus):
        if(checkStatus == True):
            self.streamActors = self.streamActorsDTI
        else:
            if self.dualLoadedOnce: self.lesionMapperDual.ClearStreamlines() 

    # Handler for parcellation display
    @pyqtSlot(bool)
    def parcellation_toggled(self, checkStatus):
        if(self.dataFolderInitialized == True):
            if (checkStatus == True):
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
                            actorItem.GetProperty().SetColor([161/255,217/255,155/255])

            if(self.dualLoadedOnce == True): # Update dual view also.
                self.lesionMapperDual.Refresh()
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