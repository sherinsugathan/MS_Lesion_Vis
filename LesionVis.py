#==========================================
# Title:  MS Lesion Visualization Project
# Author: Sherin Sugathan
# Last Modified Date:   15 Nov 2019
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
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
import nibabel as nib
import numpy as np
import json

from PyQt5 import QtWidgets, uic
from itkwidgets import view
from PyQt5.QtWidgets import QFileDialog, QCheckBox
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt
from os import system, name
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from freesurfer_surface import Surface, Vertex, Triangle
from enum import Enum

class Ui(Qt.QMainWindow):

    # Main Initialization
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("lesionui.ui", self)
        logging.info('UI file loaded successfully.')
        #self.showMaximized()
        self.initUI()
        self.clear()
        logging.info('UI initialized successfully.')
        self.initVTK()
        self.dataFolderInitialized = False # Flag to indicate that the dataset folder is properly set.
        self.volumeDataLoaded = False # Flag to indicate that volume data is initialized and loaded.
        self.showMaximized()
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
        self.pushButton_Screenshot.clicked.connect(self.on_click_CaptureScreeshot) # Attaching button click Handlers
        self.comboBox_LesionFilter.currentTextChanged.connect(self.on_combobox_changed_LesionFilter) # Attaching handler for lesion filter combobox selection change.
        self.comboBox_VisType.addItem("Default View")
        self.comboBox_VisType.addItem("Transparent Surfaces")
        self.comboBox_VisType.addItem("Lesion Intensity Raw Vis.")
        self.comboBox_VisType.addItem("Lesion Difference With NAWM")
        self.comboBox_VisType.addItem("Lesion Classification View")
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

    # Initialize vtk
    def initVTK(self):
        # Define viewport ranges (3 MPRS and 1 volume rendering)
        #self.mprA_Viewport=[0.0, 0.667, 0.333, 1.0]
        #self.mprB_Viewport=[0.0, 0.334, 0.333, 0.665]
        #self.mprC_Viewport=[0.0, 0.0, 0.1, 0.1]
        #self.VR_Viewport=[0.335, 0, 1.0, 1.0]

        self.vl = Qt.QVBoxLayout()
        self.vl_MPRA = Qt.QVBoxLayout()
        self.vl_MPRB = Qt.QVBoxLayout()
        self.vl_MPRC = Qt.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkWidgetMPRA = QVTKRenderWindowInteractor(self.frame_MPRA)
        self.vtkWidgetMPRB = QVTKRenderWindowInteractor(self.frame_MPRB)
        self.vtkWidgetMPRC = QVTKRenderWindowInteractor(self.frame_MPRC)
        # Orientation cube.
        self.axesActor = vtk.vtkAnnotatedCubeActor()
        self.vl.addWidget(self.vtkWidget)
        self.vl_MPRA.addWidget(self.vtkWidgetMPRA)
        self.vl_MPRB.addWidget(self.vtkWidgetMPRB)
        self.vl_MPRC.addWidget(self.vtkWidgetMPRC)
        self.vtkWidget.Initialize()
        self.vtkWidgetMPRA.Initialize()
        self.vtkWidgetMPRB.Initialize()
        self.vtkWidgetMPRC.Initialize()

        self.ren = vtk.vtkRenderer() # Renderer for volume
        self.renMPRA = vtk.vtkRenderer() # Renderer for MPR A
        self.renMPRB = vtk.vtkRenderer() # Renderer for MPR B
        self.renMPRC = vtk.vtkRenderer() # Renderer for MPR C
        self.renOrientationCube = vtk.vtkRenderer()
        self.ren.SetBackground(0, 0, 0)
        self.renMPRA.SetBackground(0, 0, 0)
        self.renMPRB.SetBackground(0, 0, 0)
        self.renMPRC.SetBackground(0, 0, 0)
        #self.ren.SetViewport(self.VR_Viewport[0], self.VR_Viewport[1], self.VR_Viewport[2], self.VR_Viewport[3])
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

        self.resliceImageViewerMPRA = vtk.vtkResliceImageViewer()
        self.resliceImageViewerMPRB = vtk.vtkResliceImageViewer()
        self.resliceImageViewerMPRC = vtk.vtkResliceImageViewer()
        #self.resliceImageViewerMPRB.GetImageActor().RotateY(90)  # Apply 90 degree rotation once to fix the viewer's nature to display data with wrong rotation (against convention).
        #self.resliceImageViewerMPRC.GetImageActor().RotateX(90)  # Apply 90 degree rotation once to fix the viewer's nature to display data with wrong rotation (against convention).
        #self.renMPRB.ResetCamera() # Needed for making the camera look at the slice properly.
        #self.renMPRC.ResetCamera() # Needed for making the camera look at the slice properly.

        self.informationKey = vtk.vtkInformationStringKey.MakeKey("ID", "vtkActor")
        self.informationUniqueKey = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")

        self.niftyReaderT1 = vtk.vtkNIFTIImageReader() # Common niftyReader.
        self.modelListBoxSurfaces = QtGui.QStandardItemModel() # List box for showing loaded surfaces.
        self.listView.setModel(self.modelListBoxSurfaces)
        self.listView.selectionModel().selectionChanged.connect(self.onSurfaceListSelectionChanged) # Event handler for surface list view selection changed.

        self.sliceNumberTextMPRA = vtk.vtkTextActor() # MPRA Slice number
        self.sliceNumberTextMPRB = vtk.vtkTextActor() # MPRB Slice number
        self.sliceNumberTextMPRC = vtk.vtkTextActor() # MPRC Slice number

        # Text overlay support in main renderer.
        self.overlayDataMain = {"Lesion ID":"NA", "Lesion Load":"0", "Voxel Count":"NA", "Centroid":"NA", "Elongation":"NA", "Lesion Perimeter":"NA", "Lesion Spherical Radius":"NA", "Lesion Spherical Perimeter":"NA", "Lesion Flatness":"NA", "Lesion Roundness":"NA", "Depth Peeling":"Disabled", "OpenGL Renderer":"Unknown"}
        self.textActorLesionStatistics = vtk.vtkTextActor()
        self.depthPeelingStatus = "Depth Peeling : Enabled"
        self.numberOfLesions = 0
        self.textActorLesionStatistics.UseBorderAlignOff()
        self.textActorLesionStatistics.SetPosition(10,0)
        self.textActorLesionStatistics.GetTextProperty().SetFontFamilyToCourier()
        self.textActorLesionStatistics.GetTextProperty().SetFontSize(16)
        self.textActorLesionStatistics.GetTextProperty().SetColor( 0.227, 0.969, 0.192 )

        self.style = LesionUtils.MouseInteractorHighLightActor(None, self.iren, self.overlayDataMain, self.textActorLesionStatistics, self.informationKey, self.informationUniqueKey)
        self.style.SetDefaultRenderer(self.ren)
        self.iren.SetInteractorStyle(self.style)

        self.ren.ResetCamera()
        self.frame.setLayout(self.vl)

        self.renMPRA.ResetCamera()
        self.frame_MPRA.setLayout(self.vl_MPRA)
        self.renMPRB.ResetCamera()
        self.frame_MPRB.setLayout(self.vl_MPRB)
        self.renMPRC.ResetCamera()
        self.frame_MPRC.setLayout(self.vl_MPRC)

        self.show()
        self.iren.Initialize()
        #self.iren.Start()
        self.iren_MPRA.Initialize()
        self.iren_MPRB.Initialize()
        self.iren_MPRC.Initialize()

        openglRendererInUse = self.ren.GetRenderWindow().ReportCapabilities().splitlines()[1].split(":")[1].strip()
        self.overlayDataMain["OpenGL Renderer"] = openglRendererInUse

    # # add entries to the structure table in the interface
    # def populateStructureInterface(self, structureInfo ):
    #     # clear previous entries

    #     for lesion in structureInfo:
    #         # add row in table
    #         pass


    # Load and Render Structural data as image slices.
    def LoadStructuralSlices(self, fileName, isNiftyReadRequired=True):
        if(isNiftyReadRequired==True):
            self.niftyReaderT1.SetFileName(fileName)
            self.niftyReaderT1.Update()
            ################################
            # MPR A    #####################
            ################################
            self.resliceImageViewerMPRA.SetInputData(self.niftyReaderT1.GetOutput())
            self.resliceImageViewerMPRA.SetRenderWindow(self.vtkWidgetMPRA.GetRenderWindow())
            self.resliceImageViewerMPRA.SetRenderer(self.renMPRA)
            self.resliceImageViewerMPRA.SetSliceOrientation(2)
            self.resliceImageViewerMPRA.SliceScrollOnMouseWheelOn()
            self.resliceImageViewerMPRA.SetColorLevel(255)
            self.mprA_Slice_Slider.setMaximum(self.resliceImageViewerMPRA.GetSliceMax())
            self.resliceImageViewerMPRA.SetSlice(math.ceil((self.resliceImageViewerMPRA.GetSliceMin()+self.resliceImageViewerMPRA.GetSliceMax())/2))
            self.mprA_Slice_Slider.setValue(math.ceil((self.resliceImageViewerMPRA.GetSliceMin()+self.resliceImageViewerMPRA.GetSliceMax())/2))
            # Define Interactor
            interactorMPRA = vtk.vtkInteractorStyleImage()
            self.iren_MPRA.SetInteractorStyle(interactorMPRA)
            
            ################################
            # MPR B    #####################
            ################################
            self.resliceImageViewerMPRB.SetInputData(self.niftyReaderT1.GetOutput())
            self.resliceImageViewerMPRB.SetRenderWindow(self.vtkWidgetMPRB.GetRenderWindow())
            self.resliceImageViewerMPRB.SetRenderer(self.renMPRB)
            self.resliceImageViewerMPRB.SetSliceOrientation(1)
            self.resliceImageViewerMPRB.SetColorLevel(255)
            
            self.resliceImageViewerMPRB.SetResliceModeToAxisAligned()
            self.mprB_Slice_Slider.setMaximum(self.resliceImageViewerMPRB.GetSliceMax())
            self.resliceImageViewerMPRB.SetSlice(math.ceil((self.resliceImageViewerMPRB.GetSliceMin() + self.resliceImageViewerMPRB.GetSliceMax())/2))
            self.mprB_Slice_Slider.setValue(math.ceil((self.resliceImageViewerMPRB.GetSliceMin() + self.resliceImageViewerMPRB.GetSliceMax())/2))
            # Define Interactor
            interactorMPRB = vtk.vtkInteractorStyleImage()
            self.iren_MPRB.SetInteractorStyle(interactorMPRB)

            ################################
            # MPR C    #####################
            ################################
            self.resliceImageViewerMPRC.SetResliceModeToAxisAligned()
            self.resliceImageViewerMPRC.SetInputData(self.niftyReaderT1.GetOutput())
            self.resliceImageViewerMPRC.SetRenderWindow(self.vtkWidgetMPRC.GetRenderWindow())
            self.resliceImageViewerMPRC.SetRenderer(self.renMPRC)
            self.resliceImageViewerMPRC.SetSliceOrientation(0)
            self.resliceImageViewerMPRC.SetColorLevel(255)
            self.mprC_Slice_Slider.setMaximum(self.resliceImageViewerMPRC.GetSliceMax())
            self.resliceImageViewerMPRC.SliceScrollOnMouseWheelOn()
            self.resliceImageViewerMPRC.SetSlice(math.ceil((self.resliceImageViewerMPRC.GetSliceMin()+self.resliceImageViewerMPRC.GetSliceMax())/2))
            self.mprC_Slice_Slider.setValue(math.ceil((self.resliceImageViewerMPRC.GetSliceMin()+self.resliceImageViewerMPRC.GetSliceMax())/2))
            # Define Interactor
            interactorMPRC = vtk.vtkInteractorStyleImage()
            self.iren_MPRC.SetInteractorStyle(interactorMPRC)

            self.renMPRA.ResetCamera()
            self.renMPRB.ResetCamera()
            self.renMPRC.ResetCamera()
            self.renMPRA.GetActiveCamera().Zoom(1.5)
            self.renMPRB.GetActiveCamera().Zoom(1.5)
            self.renMPRC.GetActiveCamera().Zoom(1.5)

            self.iren_MPRA.Render()
            self.iren_MPRB.Render()
            self.iren_MPRC.Render()
        else:
            self.resliceImageViewerMPRA.SetSlice(self.mprA_Slice_Slider.value())
            self.resliceImageViewerMPRB.SetSlice(self.mprB_Slice_Slider.value())
            self.resliceImageViewerMPRC.SetSlice(self.mprC_Slice_Slider.value())
        
    #####################################
    # MAIN LOADER: Load and Render Data #
    #####################################
    def renderData(self, fileNames, settings=None):
        self.actors = []
        self.lesionCentroids = []
        self.lesionNumberOfPixels = []
        self.lesionElongation = []
        self.lesionPerimeter = []
        self.lesionSphericalRadius = []
        self.lesionSphericalPerimeter = []
        self.lesionFlatness = []
        self.lesionRoundness = []
        subjectFolder = os.path.join(self.lineEdit_DatasetFolder.text(), str(self.comboBox_AvailableSubjects.currentText()))
        # load precomputed lesion properties
        structureInfo = None
        with open(subjectFolder + "\\structure-def.json") as fp: 
            structureInfo = json.load(fp)
        self.numberOfLesionElements = len(structureInfo)

        self.lesionActors = LesionUtils.extractLesions(subjectFolder,self.numberOfLesionElements, self.informationKey,self.informationUniqueKey, True)

        for actor in self.lesionActors:
            self.actors.append(actor)

        jsonTransformationMatrix = LesionUtils.getJsonDataTransformMatrix(subjectFolder)
        
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

                # lesionSphere = vtk.vtkSphereSource()
                # lesionSphere.SetCenter(transformedCenter[0],transformedCenter[1],transformedCenter[2])
                # lesionSphere.SetRadius(5)
                # lesionSphereMapper = vtk.vtkPolyDataMapper()
                # lesionSphereMapper.SetInputConnection(lesionSphere.GetOutputPort())
                # lesionSphereactor = vtk.vtkActor()
                # lesionSphereactor.SetMapper(lesionSphereMapper)
                # lesionSphereactor.GetProperty().SetColor(1.0, 0.0, 0.0)

                # assign actor to the renderer
                #self.actors.append(lesionSphereactor)

        self.style.addLesionData(self.lesionCentroids, self.lesionNumberOfPixels, self.lesionElongation, self.lesionPerimeter, self.lesionSphericalRadius, self.lesionSphericalPerimeter, self.lesionFlatness, self.lesionRoundness)

        # populate the user interface with the structure values
        #self.populateStructureInterface(structureInfo)

        # Compute lesion properties
        connectedComponentImage, connectedComponentFilter = LesionUtils.computeLesionProperties(subjectFolder)
        for i in range(len(fileNames)):

            # Check if files are wavefront OBJ and in the whitelist according to settings.
            if fileNames[i].endswith(".obj") and os.path.basename(fileNames[i]) in settings.getSurfaceWhiteList():
                loadFilePath = os.path.join(subjectFolder, fileNames[i])      
                reader = vtk.vtkOBJReader()
                reader.SetFileName(loadFilePath)
                reader.Update()
                mapper = vtk.vtkOpenGLPolyDataMapper()
                mapper.SetInputConnection(reader.GetOutputPort())
                transform = vtk.vtkTransform()
                transform.Identity()
                mrmlDataFileName = open ( subjectFolder + "\\meta\\mrml.txt" , 'r')
                arrayList = list(np.asfarray(np.array(mrmlDataFileName.readline().split(",")),float))
                transform.SetMatrix(arrayList)


                # isLesionTransformNeeded = False
                # if fileNames[i].endswith("lesions.obj"): # Check if surface is a lesion.
                #     if(os.path.isfile(subjectFolder + "\\meta\\mrmlMask.txt") and os.path.isfile(subjectFolder + "\\meta\\crasMask.txt")):
                #         mrmlDataFileName = open ( subjectFolder + "\\meta\\mrmlMask.txt" , 'r')
                #     else:
                #         mrmlDataFileName = open ( subjectFolder + "\\meta\\mrml.txt" , 'r')

                #     arrayList = list(np.asfarray(np.array(mrmlDataFileName.readline().split(",")),float))
                #     transform.SetMatrix(arrayList)
                #     isLesionTransformNeeded = True

                #     # Probe the lesion surface with the volume data.
                #     mapper, probeFilter = LesionUtils.probeSurfaceWithVolume(subjectFolder)

                #     # Run connectivity filter to extract lesions into separate polydata objects.
                #     lesionComponentMappers, self.numberOfLesions = LesionUtils.runLesionConnectivityAnalysis(probeFilter)

                #     # Update overlay text and add it to the renderer
                #     self.overlayDataMain["Lesion Load"] = self.numberOfLesions
                #     self.overlayDataMain["Depth Peeling"] = "Enabled" if self.checkBox_DepthPeeling.isChecked() else "Disabled"
                #     LesionUtils.updateOverlayText(self.iren, self.overlayDataMain, self.textActorLesionStatistics)
                #     self.ren.AddActor2D(self.textActorLesionStatistics)
                    
                #     mrmlDataFileName.close()

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                # if(isLesionTransformNeeded == True): # Apply special transform to lesions.
                #     print("Special transform applied")
                #     # Non need to apply transform here because it is already applied in the mapper using LesionUtils.
                # else: # This is not a lesion. Do not disturb with a transformation.
                transform.Identity()
                actor.SetUserTransform(transform)

                information = vtk.vtkInformation()
                # Apply transparency settings and add information.
                if "lh.pial" in fileNames[i]:
                    actor.GetProperty().SetOpacity(settings.lh_pial_transparency)
                    information.Set(self.informationKey,"lh.pial")
                if "rh.pial" in fileNames[i]:
                    actor.GetProperty().SetOpacity(settings.rh_pial_transparency)
                    information.Set(self.informationKey,"rh.pial")
                if "lh.white" in fileNames[i]:
                    actor.GetProperty().SetOpacity(settings.lh_white_transparency)
                    information.Set(self.informationKey,"lh.white")
                if "rh.white" in fileNames[i]:
                    actor.GetProperty().SetOpacity(settings.rh_white_transparency)
                    information.Set(self.informationKey,"rh.white")

                if "pial" in fileNames[i] or "white" in fileNames[i]:
                    translationFilePath = os.path.join(subjectFolder, "meta\\cras.txt")
                    f = open(translationFilePath, "r")
                    t_vector = []
                    for t in f:
                        t_vector.append(t)
                    t_vector = list(map(float, t_vector))
                    transform = vtk.vtkTransform()
                    transform.PostMultiply()
                    transform.Translate(t_vector[0], t_vector[1], t_vector[2])
                    actor.SetUserTransform(transform)
                    f.close()

                if(fileNames[i].endswith("lesions.obj")==False):
                    actor.GetProperty().SetInformation(information)
                    actor.GetProperty().SetColor(1, 0.964, 0.878)
                    self.actors.append(actor)
                #else:
                    # lesionIndex = 1
                    # for mapperIndex in range(len(lesionComponentMappers)):
                    #     information = vtk.vtkInformation()
                    #     #information.Set(self.informationKey,"lesions" + str(lesionIndex))
                    #     information.Set(self.informationKey,"lesions")
                    #     lesionActor = vtk.vtkActor()
                    #     lesionActor.SetMapper(lesionComponentMappers[mapperIndex])
                    #     lesionActor.GetProperty().SetInformation(information)
                    #     self.actors.append(lesionActor)
                    #     lesionIndex = lesionIndex + 1
   
                # Also add to the listBox showing loaded surfaces.
                item = QtGui.QStandardItem(os.path.basename(fileNames[i]))
                item.setCheckable(True)
                item.setCheckState(2)      
                self.modelListBoxSurfaces.appendRow(item)
                self.listView.setSelectionRectVisible(True)
                self.modelListBoxSurfaces.itemChanged.connect(self.on_itemChanged)


        # Update overlay text and add it to the renderer
        self.overlayDataMain["Lesion Load"] = self.numberOfLesionElements
        self.overlayDataMain["Depth Peeling"] = "Enabled" if self.checkBox_DepthPeeling.isChecked() else "Disabled"
        LesionUtils.updateOverlayText(self.iren, self.overlayDataMain, self.textActorLesionStatistics)
        self.ren.AddActor2D(self.textActorLesionStatistics)
        # Check if streamline computation is requested.
        if(str(self.comboBox_VisType.currentText())=='Lesion Surface Mapping'):
            fiberActor = LesionUtils.computeStreamlines(subjectFolder)
            information = vtk.vtkInformation()
            information.Set(self.informationKey,"fiber")
            fiberActor.GetProperty().SetInformation(information)
            self.actors.append(fiberActor)
        for a in self.actors:
            self.ren.AddActor(a)
            #print(a.GetMapper().GetInput())

        # Relate JSON with surfaces.

        # selectEnclosedPoints = vtk.vtkSelectEnclosedPoints()
        
        # count = 0
        # print("Number of lesion centroids:" + str(len(self.lesionCentroids)))


        # for centroidIndex in range(len(self.lesionCentroids)):
        #     point = vtk.vtkPoints()
        #     point.InsertNextPoint(self.lesionCentroids[centroidIndex])
        #     ug = vtk.vtkUnstructuredGrid()
        #     ug.SetPoints(point)
        #     sphereSource = vtk.vtkSphereSource()
        #     sphereSource.SetCenter(self.lesionCentroids[centroidIndex])
        #     sphereSource.SetRadius(1)
        #     sphereSource.SetPhiResolution(3)
        #     sphereSource.SetThetaResolution(3)
        #     sphereSource.Update()
        #     for a in self.actors:
        #         if(a.GetProperty().GetInformation().Get(self.informationKey) != None):
        #             if a.GetProperty().GetInformation().Get(self.informationKey) in "lesions":
        #                 selectEnclosedPoints.SetInputData(ug)
        #                 selectEnclosedPoints.SetSurfaceData(a.GetMapper().GetInput())
        #                 selectEnclosedPoints.SetTolerance(0.001)
        #                 selectEnclosedPoints.Update()           
        #                 #intersectionPolyDataFilter = vtk.vtkIntersectionPolyDataFilter()
        #                 #intersectionPolyDataFilter.AddInputDataObject(0,sphereSource.GetOutput())
        #                 #intersectionPolyDataFilter.AddInputDataObject(1,a.GetMapper().GetInput())   
        #                 #intersectionPolyDataFilter.SetInputConnection(0,sphereSource.GetOutputPort())
        #                 #intersectionPolyData Filter.SetInputConnection(1,a.GetMapper().GetOutputPort())
        #                 #intersectionPolyDataFilter.Update()
        #                 #if(intersectionPolyDataFilter.GetOutput()!=None):
        #                  #   print("Valid output detected")
        #                 #print(selectEnclosedPoints.IsInside(0))
        #                 print(selectEnclosedPoints.IsInside(0))
        #                 if(selectEnclosedPoints.IsInside(0)==1):
        #                     count= count+1
        #                 selectEnclosedPoints.Complete()
        #     print("Pixel count is " + str(self.numberOfPixels[centroidIndex]))
        #     print("loop done")
        # print("detect count is:"+str(count))

        self.ren.ResetCamera()
        self.iren.Render()

        # Load data for MPRs.
        self.LoadStructuralSlices(subjectFolder + "\\structural\\T1.nii")

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
            mrmlDataFileName = open ( subjectFolder + "\\meta\\mrml.txt" , 'r')
            crasDataFileName = open ( subjectFolder + "\\meta\\cras.txt" , 'r')
            niftiReader = vtk.vtkNIFTIImageReader()
            niftiReader.SetFileName(t1StructuralNiftyFileName)
            niftiReader.Update()

            ijkras_transform = vtk.vtkTransform()
            arrayList = list(np.asfarray(np.array(mrmlDataFileName.readline().split(",")),float))
            ijkras_transform.SetMatrix(arrayList)
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

            mrmlDataFileName.close()
            crasDataFileName.close()

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
            self.frame.setLayout(self.vl)
            self.iren.Render()
        else:
            for actorItem in self.actors:
                if(actorItem.GetProperty().GetInformation().Get(self.informationKey) != None):
                    if actorItem.GetProperty().GetInformation().Get(self.informationKey) in item.text():
                        self.ren.AddActor(actorItem)
            self.frame.setLayout(self.vl)
            self.iren.Render()

    # Handler for checkbox check status change for structural data.
    @pyqtSlot(QtGui.QStandardItem)
    def on_itemChanged_Structural(self,  item):
        state = ['UNCHECKED', 'TRISTATE',  'CHECKED'][item.checkState()]
        if(state == 'UNCHECKED'):
            removeIndex = item.index()
            self.ren.RemoveVolume(self.volume)
            #self.ren.ResetCamera()
            self.frame.setLayout(self.vl)
            self.iren.Render()
        else:
            addIndex = item.index()
            self.ren.AddVolume(self.volume)
            #self.ren.ResetCamera()
            self.frame.setLayout(self.vl)
            self.iren.Render()

    # Handler for MPRA Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRA(self):
        # Setup the slide number text and add it to the renderer
        self.sliceNumberTextMPRA.SetInput(str(self.mprA_Slice_Slider.value()))
        self.sliceNumberTextMPRA.UseBorderAlignOff()
        self.sliceNumberTextMPRA.SetPosition(5,5)
        self.sliceNumberTextMPRA.GetTextProperty().SetFontFamilyToCourier()
        self.sliceNumberTextMPRA.GetTextProperty().SetFontSize(16)
        self.sliceNumberTextMPRA.GetTextProperty().SetColor( 0.227, 0.969, 0.192 )
        self.renMPRA.AddActor2D(self.sliceNumberTextMPRA)
        self.LoadStructuralSlices("dummy", False)

    # Handler for MPRB Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRB(self):
        # Setup the slide number text and add it to the renderer
        self.sliceNumberTextMPRB.SetInput(str(self.mprB_Slice_Slider.value()))
        self.sliceNumberTextMPRB.UseBorderAlignOff()
        self.sliceNumberTextMPRB.SetPosition(5,5)
        self.sliceNumberTextMPRB.GetTextProperty().SetFontFamilyToCourier()
        self.sliceNumberTextMPRB.GetTextProperty().SetFontSize(16)
        self.sliceNumberTextMPRB.GetTextProperty().SetColor( 0.227, 0.969, 0.192 )
        self.renMPRB.AddActor2D(self.sliceNumberTextMPRB)
        self.LoadStructuralSlices("dummy", False)

    # Handler for MPRC Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRC(self):
        # Setup the slide number text and add it to the renderer
        self.sliceNumberTextMPRC.SetInput(str(self.mprC_Slice_Slider.value()))
        self.sliceNumberTextMPRC.UseBorderAlignOff()
        self.sliceNumberTextMPRC.SetPosition(5,5)
        self.sliceNumberTextMPRC.GetTextProperty().SetFontFamilyToCourier()
        self.sliceNumberTextMPRC.GetTextProperty().SetFontSize(16)
        self.sliceNumberTextMPRC.GetTextProperty().SetColor( 0.227, 0.969, 0.192 )
        self.renMPRC.AddActor2D(self.sliceNumberTextMPRC)
        self.LoadStructuralSlices("dummy", False)

    # Handler for Lesion Filter Slider change.
    @pyqtSlot()
    def on_sliderChangedLesionFilter(self):
        #self.label_lesionFilterCurrent.setText(str("{0:.2f}".format(self.horizontalSliderLesionFilter.value())))
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
        
    # Handler for Dial moved.
    @pyqtSlot()
    def on_DialMoved(self):
        self.opacityValueLabel.setText(str(self.dial.value()/float(500)))
        for actorItem in self.actors:
            if(actorItem.GetProperty().GetInformation().Get(self.informationKey) != None):
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
        self.overlayDataMain["Lesion Load"] = self.numberOfLesions
        self.overlayDataMain["Depth Peeling"] = "Enabled" if self.checkBox_DepthPeeling.isChecked() else "Disabled"
        LesionUtils.updateOverlayText(self.iren, self.overlayDataMain, self.textActorLesionStatistics)
        self.iren.Render()

    # Handler for lesion filtering selected text changed.
    @pyqtSlot()
    def on_combobox_changed_LesionFilter(self): 
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