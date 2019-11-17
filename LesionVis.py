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

from PyQt5 import QtWidgets, uic
from itkwidgets import view
from PyQt5.QtWidgets import QFileDialog, QCheckBox
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt
from os import system, name
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from enum import Enum

class Ui(Qt.QMainWindow):

    # Main Initialization
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("lesionui.ui", self)
        logging.info('UI file loaded successfully.')
        self.showMaximized()
        self.initUI()
        self.clear()
        logging.info('UI initialized successfully.')
        self.initVTK()
        self.dataFolderInitialized = False # Flag to indicate that the dataset folder is properly set.
        self.volumeDataLoaded = False # Flag to indicate that volume data is initialized and loaded.
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
        self.comboBox_VisType.addItem("Default View")
        self.comboBox_VisType.addItem("Transparent Surfaces")
        self.comboBox_VisType.addItem("Lesion Intensity Raw Vis.")
        self.comboBox_VisType.addItem("Lesion Difference With NAWM")
        self.comboBox_VisType.addItem("Lesion Classification View")
        self.comboBox_VisType.addItem("Lesion Surface Mapping")
        self.mprA_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRA)
        self.mprB_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRB)
        self.mprC_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRC)

    # Initialize vtk
    def initVTK(self):
        # Define viewport ranges (3 MPRS and 1 volume rendering)
        #self.mprA_Viewport=[0.0, 0.667, 0.333, 1.0]
        #self.mprB_Viewport=[0.0, 0.334, 0.333, 0.665]
        self.mprC_Viewport=[0.0, 0.0, 0.1, 0.1]
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
        
        #self.vtkWidget.setStyleSheet("background-color:black;")
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
        #self.renOrientationCube.SetViewport(self.mprC_Viewport[0], self.mprC_Viewport[1], self.mprC_Viewport[2], self.mprC_Viewport[3])
        if self.checkBox_DepthPeeling.isChecked():
            self.ren.SetUseDepthPeeling(True)
            self.ren.SetMaximumNumberOfPeels(4)
        
        #self.renMPRA.SetViewport(self.mprA_Viewport[0], self.mprA_Viewport[1], self.mprA_Viewport[2], self.mprA_Viewport[3])
        #self.renMPRB.SetViewport(self.mprB_Viewport[0], self.mprB_Viewport[1], self.mprB_Viewport[2], self.mprB_Viewport[3])
        #self.renMPRC.SetViewport(self.mprC_Viewport[0], self.mprC_Viewport[1], self.mprC_Viewport[2], self.mprC_Viewport[3])

        #self.renMPRA.InteractiveOff() # disable interaction in MPRA
        #self.renMPRB.InteractiveOff() # disable interaction in MPRB

        self.vtkWidget.GetRenderWindow().SetAlphaBitPlanes(True)
        self.vtkWidget.GetRenderWindow().SetMultiSamples(0)

        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        #self.vtkWidget.GetRenderWindow().AddRenderer(self.renOrientationCube)
        #self.vtkWidget.GetRenderWindow().AddRenderer(self.renMPRB)
        #self.vtkWidget.GetRenderWindow().AddRenderer(self.renMPRC)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        #self.iren = vtk.vtkRenderWindowInteractor()
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
        self.niftyReaderT1 = vtk.vtkNIFTIImageReader() # Common niftyReader.

        cone = vtk.vtkConeSource()
        cone.SetResolution(8)
        coneMapper = vtk.vtkPolyDataMapper()
        coneMapper.SetInputConnection(cone.GetOutputPort())
        coneActor = vtk.vtkActor()
        coneActor.SetMapper(coneMapper)

        #self.ren.AddActor(coneActor)   
        self.ren.ResetCamera()
        self.frame.setLayout(self.vl)

        self.renMPRA.AddActor(coneActor)
        self.renMPRA.ResetCamera()
        self.frame_MPRA.setLayout(self.vl_MPRA)
        self.renMPRB.AddActor(coneActor)
        self.renMPRB.ResetCamera()
        self.frame_MPRB.setLayout(self.vl_MPRB)
        self.renMPRC.AddActor(coneActor)
        self.renMPRC.ResetCamera()
        self.frame_MPRC.setLayout(self.vl_MPRC)
        #self.setCentralWidget(self.frame)

        self.show()
        self.iren.Initialize()
        #self.iren.Render()
        self.iren.Start()
        #self.iren.ExitCallback()
        #self.vtkWidget.GetRenderWindow().GetInteractor().Start()

        self.iren_MPRA.Initialize()
        #self.iren_MPRA.Start()

        self.iren_MPRB.Initialize()
        #self.iren_MPRB.Start()

        self.iren_MPRC.Initialize()
        #self.iren_MPRC.Start()


        # Clear all actors from the scene
        #self.ren.RemoveAllViewProps()  
        self.renMPRA.RemoveAllViewProps() 
        self.renMPRB.RemoveAllViewProps() 
        self.renMPRC.RemoveAllViewProps()     

    # Load and Render Structural data
    def renderStructuralData(self, fileName):
        img = nib.load(fileName)
        img_data = img.get_data()
        img_data_shape = img_data.shape

        dataImporter = vtk.vtkImageImport()
        dataImporter.SetDataScalarTypeToShort()
        data_string = img_data.tostring()
        dataImporter.SetNumberOfScalarComponents(1)
        dataImporter.CopyImportVoidPointer(data_string, len(data_string))
        dataImporter.SetDataExtent(0, img_data_shape[2] - 1, 0, img_data_shape[1] - 1, 0, img_data_shape[0] - 1)
        dataImporter.SetWholeExtent(0, img_data_shape[2] - 1, 0, img_data_shape[1] - 1, 0, img_data_shape[0] - 1)
        dataImporter.Update()
        #temp_data = dataImporter.GetOutput()
        #new_data = vtk.vtkImageData() 
        self.ren.ResetCamera()
        #self.frame.setLayout(self.vl)
        # Also render the MPR Views
        self.LoadStructuralSlices(fileName)

        #self.show()
        self.iren.Initialize()
        #self.iren.Start()

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

            self.iren_MPRA.Render()
            self.iren_MPRB.Render()
            self.iren_MPRC.Render()
        else:
            self.resliceImageViewerMPRA.SetSlice(self.mprA_Slice_Slider.value())
            self.resliceImageViewerMPRB.SetSlice(self.mprB_Slice_Slider.value())
            self.resliceImageViewerMPRC.SetSlice(self.mprC_Slice_Slider.value())
        
    # Load and Render Data
    def renderData(self, fileNames):#, translate, x_t=0, y_t=0,z_t=0):
        self.actors = []
        for i in range(len(fileNames)):
            if fileNames[i].endswith(".vtp"):
                subjectFolder = os.path.join(self.lineEdit_DatasetFolder.text(), str(self.comboBox_AvailableSubjects.currentText()))
                loadFilePath = os.path.join(subjectFolder, fileNames[i]) 
                polyDataReader = vtk.vtkXMLPolyDataReader()
                polyDataReader.SetFileName(loadFilePath)
                polyDataReader.Update()
                mapper = vtk.vtkOpenGLPolyDataMapper()
                mapper.SetInputConnection(polyDataReader.GetOutputPort())
                actorL = vtk.vtkActor()
                actorL.SetMapper(mapper)
                self.actors.append(actorL)

            if fileNames[i].endswith(".obj"):
                subjectFolder = os.path.join(self.lineEdit_DatasetFolder.text(), str(self.comboBox_AvailableSubjects.currentText()))
                loadFilePath = os.path.join(subjectFolder, fileNames[i])      
                reader = vtk.vtkOBJReader()
                reader.SetFileName(loadFilePath)
                reader.Update()
                mapper = vtk.vtkOpenGLPolyDataMapper()
                mapper.SetInputConnection(reader.GetOutputPort())

                transform = vtk.vtkTransform()
                transform.Identity()

                
                if fileNames[i].endswith("lesions.obj"):
                    #pgm = vtk.vtkShaderProgram2()
                    mrmlDataFileName = open ( subjectFolder + "\\meta\\mrml.txt" , 'r')
                    crasDataFileName = open ( subjectFolder + "\\meta\\cras.txt" , 'r')
                    arrayList = list(np.asfarray(np.array(mrmlDataFileName.readline().split(",")),float))
                    transform.SetMatrix(arrayList)


                    niftiReader = vtk.vtkNIFTIImageReader()
                    niftiReader.SetFileName(subjectFolder + "\\structural\\T1.nii")
                    niftiReader.Update()
                    probeFilter = vtk.vtkProbeFilter()
                    probeFilter.SetSourceConnection(niftiReader.GetOutputPort())
                    probeFilter.SetInputData(reader.GetOutput())
                    probeFilter.Update()
                    mapper.SetInputConnection(probeFilter.GetOutputPort())


                    lookupTable = vtk.vtkLookupTable()
                    lookupTable.SetNumberOfTableValues(256)
                    #lookupTable.SetHueRange(0,255)
                    lookupTable.Build()

                    #mapper.SetScalarRange(0,255)
                    #mapper.SetLookupTable(lookupTable)
                    mapper.SetScalarRange(probeFilter.GetOutput().GetScalarRange())
                    #mapper.SetScalarRange(0,255)

                    #temp.AssignShadersToLesionMapper(mapper)
                    #math = vtk.vtkMath()
                    #rgbColor = []
                    #math.RandomSeed(8775070)
                    #polyData = vtk.vtkPolyData()
                    polyData = reader.GetOutput()

                    cellData = vtk.vtkUnsignedCharArray()
                    cellData.SetNumberOfComponents(3)
                    numberOfPoints = polyData.GetNumberOfPoints()
                    doubleArray = vtk.vtkDoubleArray()
                    pointArray = doubleArray.SafeDownCast(polyData.GetPointData().GetArray("pointArrayData"))
                    #cellData.SetNumberOfTuples(polyData.GetNumberOfCells())
                    #for pointIndex in range(numberOfPoints):
                    #   value = polyData.GetPoint(pointIndex)
                        #print(value)
                    #for cellIndex in range(int(polyData.GetNumberOfCells())):
                    #    rgbColor.clear()
                    #    rgbColor.append(math.Random(64,255))
                    #    rgbColor.append(math.Random(64,255))
                    #    rgbColor.append(math.Random(64,255))
                    #    cellData.InsertTuple(cellIndex,rgbColor)
                    
                    #polyData.GetCellData().SetScalars(cellData)

                    connectivityFilter = vtk.vtkPolyDataConnectivityFilter()
                    connectivityFilter.SetInputConnection(reader.GetOutputPort())
                    connectivityFilter.SetExtractionModeToAllRegions()
                    connectivityFilter.SetColorRegions(True)
                    connectivityFilter.ColorRegionsOn()
                    connectivityFilter.Update()

                    # Setup the text and add it to the renderer
                    textActorLesionStatistics = vtk.vtkTextActor()
                    depthPeelingStatus = "Depth Peeling: Enabled" if self.checkBox_DepthPeeling.isChecked() else "Depth Peeling: Disabled"
                    textActorLesionStatistics.SetInput("Lesion Load : " + str(connectivityFilter.GetNumberOfExtractedRegions()) + "\n" + depthPeelingStatus)
                    textActorLesionStatistics.UseBorderAlignOff()
                    textActorLesionStatistics.SetPosition2(10,100)
                    textActorLesionStatistics.GetTextProperty().SetFontFamilyAsString("Google Sans")
                    textActorLesionStatistics.GetTextProperty().SetFontSize(12)
                    textActorLesionStatistics.GetTextProperty().SetColor( 0.227, 0.969, 0.192 )
                    self.ren.AddActor2D(textActorLesionStatistics)
                    mrmlDataFileName.close()
                    crasDataFileName.close()

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.SetUserTransform(transform)

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
                self.actors.append(actor)

        for a in self.actors:
            self.ren.AddActor(a)
            self.ren.ResetCamera()
            self.iren.Render()
        self.renderStructuralData(subjectFolder + "\\structural\\T1.nii")

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

        # Fetch required display settings.
        print(self.comboBox_VisType.currentText())
        self.settings = Settings.getSettings(Settings.visMapping(self.comboBox_VisType.currentText())) 
        print(self.settings)
        subjectFolder = os.path.join(self.lineEdit_DatasetFolder.text(), str(self.comboBox_AvailableSubjects.currentText()))
        if subjectFolder:
            subjectFiles = [f for f in LesionUtils.getListOfFiles(subjectFolder) if os.path.isfile(os.path.join(subjectFolder, f))]
            self.renderData(subjectFiles)  # Render the actual data

        self.model = QtGui.QStandardItemModel()
        for i in range(len(subjectFiles)):
            if subjectFiles[i].endswith(".obj"):
                item = QtGui.QStandardItem(os.path.basename(subjectFiles[i]))
                item.setCheckable(True)
                item.setCheckState(2)      
                self.model.appendRow(item)
        self.listView.setModel(self.model)
        self.listView.setSelectionRectVisible(True)
        self.model.itemChanged.connect(self.on_itemChanged)

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
            removeIndex = item.index()
            self.ren.RemoveActor(self.actors[removeIndex.row()])
            #self.ren.ResetCamera()
            self.frame.setLayout(self.vl)
            #self.show()
            #self.iren.Initialize()
            #self.iren.Start()
            self.iren.Render()
        else:
            addIndex = item.index()
            self.ren.AddActor(self.actors[addIndex.row()])
            #self.ren.ResetCamera()
            self.frame.setLayout(self.vl)
            #self.show()
            #self.iren.Initialize()
            #self.iren.Start()
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
            #self.show()
            #self.iren.Initialize()
            #self.iren.Start()
            self.iren.Render()
        else:
            addIndex = item.index()
            self.ren.AddVolume(self.volume)
            #self.ren.ResetCamera()
            self.frame.setLayout(self.vl)
            #self.show()
            #self.iren.Initialize()
            #self.iren.Start()
            self.iren.Render()

    # Handler for MPRA Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRA(self):
        self.mprA_Slice_Number_Label.setText(str(self.mprA_Slice_Slider.value()))
        self.LoadStructuralSlices("dummy", False)

    # Handler for MPRB Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRB(self):
        self.mprB_Slice_Number_Label.setText(str(self.mprB_Slice_Slider.value()))
        self.LoadStructuralSlices("dummy", False)

    # Handler for MPRC Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRC(self):
        self.mprC_Slice_Number_Label.setText(str(self.mprC_Slice_Slider.value()))
        self.LoadStructuralSlices("dummy", False)

    # Handler for Dial moved.
    @pyqtSlot()
    def on_DialMoved(self):
        selectedListIndices = self.listView.selectedIndexes()
        if selectedListIndices:
            self.actors[selectedListIndices[0].row()].GetProperty().SetOpacity(self.dial.value()/float(500))
            #self.show()
            #self.iren.Initialize()
            #self.iren.Start()
            self.iren.Render()

    # Handler for unselecting all subjects at once-
    @pyqtSlot()
    def on_click_UnselectAllSubjects(self):
        #self.ren.RemoveAllViewProps() # Remove all actors from the list of actors before loading new subject data.
        model = self.listView.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.isCheckable() and item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
        #self.show()
        #self.iren.Initialize()
        #self.iren.Start()
        self.iren.Render()

    # Handler for depth peeling checkbox
    @pyqtSlot()
    def depthpeel_state_changed(self):
        if self.checkBox_DepthPeeling.isChecked():
            self.ren.SetUseDepthPeeling(True)
            self.ren.SetMaximumNumberOfPeels(4)
            #self.show()
            #self.iren.Initialize()
            #self.iren.Start()
            self.iren.Render()
        else:
            self.ren.SetUseDepthPeeling(False)
            #self.show()
            #self.iren.Initialize()
            #self.iren.Start()
            self.iren.Render()
    

    def closeEvent(self, event):
        print("Trying to exit")
        self.iren.SetEnableRender(False)
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
###########################################
# QApplication ############################
###########################################
app = QtWidgets.QApplication(sys.argv)
window = Ui()
sys.exit(app.exec_())