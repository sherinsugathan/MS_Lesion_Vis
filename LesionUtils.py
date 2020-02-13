#==========================================
# Title:  MS Lesion Visualization Project: Utils
# Author: Sherin Sugathan
# Last Modified Date:   9 Jan 2020
#==========================================

import os
import vtk
import numpy as np
import time
import SimpleITK as sitk
import time
from nibabel import freesurfer
from PyQt5.QtCore import QTimer

'''
##########################################################################
    For the given path, get the List of all files in the directory tree 
##########################################################################
'''
def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

'''
##########################################################################
    Perform connectivity filter analysis on the algorithm output received from probeFilter.
    Returns: A list of dijoint lesion mappers and the total number of connected components.
##########################################################################
'''
def runLesionConnectivityAnalysis(probeFilterObject):
    connectivityFilter = vtk.vtkPolyDataConnectivityFilter()
    connectivityFilter.SetInputConnection(probeFilterObject.GetOutputPort())
    connectivityFilter.SetExtractionModeToAllRegions()
    connectivityFilter.Update()
    numberOfExtractedRegions = connectivityFilter.GetNumberOfExtractedRegions()
    connectivityFilter.SetExtractionModeToSpecifiedRegions()
    lesionComponentMappers = list()
    idx=0
    while True:
        connectivityFilter.AddSpecifiedRegion(idx)
        connectivityFilter.Update()
        component = vtk.vtkPolyData()
        component.DeepCopy(connectivityFilter.GetOutput())
        if component.GetNumberOfCells() <=0:
            break

        centerOfMassFilter = vtk.vtkCenterOfMass()
        centerOfMassFilter.SetInputData(component)
        centerOfMassFilter.SetUseScalarsAsWeights(False)
        centerOfMassFilter.Update()
        #print(centerOfMassFilter.GetCenter())
        #print(component.GetNumberOfCells())

        mapper = vtk.vtkOpenGLPolyDataMapper()
        mapper.SetInputData(component)
        mapper.SetScalarRange(probeFilterObject.GetOutput().GetScalarRange())
        mapper.Update()
        lesionComponentMappers.append(mapper)
        connectivityFilter.DeleteSpecifiedRegion(idx)
        idx +=1
    return lesionComponentMappers, numberOfExtractedRegions

'''
##########################################################################
    Update overlay text on a specific renderer.
    Returns: Nothing
##########################################################################
'''
def updateOverlayText(renderWindow, overlayDictionary, overlayGlobalDictionary, overlayTextActor, globalTextActor): 
    overlayText =""
    for key in overlayDictionary.keys():
        overlayText = overlayText + str(key) + ": " + str(overlayDictionary[key]) + "\n"
    overlayTextActor.SetInput(overlayText)
    overlayTextGlobal =""
    for key in overlayGlobalDictionary.keys():
        overlayTextGlobal = overlayTextGlobal + str(key) + ": " + str(overlayGlobalDictionary[key]) + "\n"
    globalTextActor.SetInput(overlayTextGlobal)

'''
##########################################################################
    Capture a screenshot from the main renderer. File gets written with timestamp name.
    Returns: Nothing
##########################################################################
'''
def captureScreenshot(renderWindow): 
    windowToImageFilter = vtk.vtkWindowToImageFilter()
    windowToImageFilter.SetInput(renderWindow)
    windowToImageFilter.SetScale(3,3)
    #windowToImageFilter.SetMagnification(3) #set the resolution of the output image (3 times the current resolution of vtk render window)
    windowToImageFilter.SetInputBufferTypeToRGBA() #also record the alpha (transparency) channel
    windowToImageFilter.ReadFrontBufferOff() # read from the back buffer
    windowToImageFilter.Update()
    timestr = time.strftime("%Y%m%d-%H%M%S")
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(timestr + ".png")
    writer.SetInputConnection(windowToImageFilter.GetOutputPort())
    writer.Write()

'''
##########################################################################
    Class for implementing custom interactor.
##########################################################################
'''
class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,parent=None,iren=None, overlayDataMain=None, textActorLesionStatistics=None, overlayDataGlobal=None, textActorGlobal=None, informationKey = None, informationKeyID = None, lesionSeededFiberTracts=None, sliderA=None, sliderB=None, sliderC=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)

        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.iren = iren
        self.overlayDataMain = overlayDataMain
        self.textActorLesionStatistics = textActorLesionStatistics
        self.overlayDataGlobal = overlayDataGlobal 
        self.textActorGlobal = textActorGlobal
        self.informationKey = informationKey
        self.informationKeyID = informationKeyID
        self.lesionSeededFiberTracts = lesionSeededFiberTracts
        self.sliderA = sliderA
        self.sliderB = sliderB
        self.sliderC = sliderC
        self.message = "tick"
        self.timer = QTimer()
        self.timer.timeout.connect(self.onTimerEvent)
        

    def addLesionData(self, subjectFolder, lesionCentroids, lesionNumberOfPixels, lesionElongation, lesionPerimeter, lesionSphericalRadius, lesionSphericalPerimeter, lesionFlatness, lesionRoundness, lesionSeededFiberTracts):
        self.lesionCentroids = lesionCentroids
        self.lesionNumberOfPixels = lesionNumberOfPixels
        self.lesionElongation = lesionElongation
        self.lesionPerimeter = lesionPerimeter
        self.lesionSphericalRadius = lesionSphericalRadius
        self.lesionSphericalPerimeter = lesionSphericalPerimeter
        self.lesionFlatness = lesionFlatness
        self.lesionRoundness = lesionRoundness
        self.subjectFolder = subjectFolder
        self.lesionSeededFiberTracts = lesionSeededFiberTracts

    def onTimerEvent(self):
        self.parcellationCurrentActor.RotateY(1)
        self.iren.Render()

        # if self.message == "tick":
        #     self.message = "tock"
        #     #self.brodmannTextActor.SetInput("Hello")
        #     #print(self.message)
        #     #self.iren.Render()
        # else:
        #     self.message = "tick"
        #     #self.brodmannTextActor.SetInput("Sherin")
        #     #print(self.message)
        #     #self.iren.Render()
        

    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        # pointPicker = vtk.vtkPointPicker()
        # pointPicker.SetTolerance(0.0005)
        # pointPicker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        # worldPosition = pointPicker.GetPickPosition()
        # print(pointPicker.GetPointId())
        cellPicker = vtk.vtkCellPicker()
        cellPicker.SetTolerance(0.0005)
        cellPicker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        #worldPosition = cellPicker.GetPickPosition()
        #print(cellPicker.GetPointId())
        
        # get the new
        self.NewPickedActor = picker.GetActor()
        # If something was selected
        if self.NewPickedActor:
            # If we picked something before, reset its property
            if self.LastPickedActor:
                self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
            
            # Save the property of the picked actor so that we can
            # restore it next time
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())

            itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationKey)
            lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationKeyID)

            if("lh" in str(itemType)):
                if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == False):
                    self.vtkWidget.GetRenderWindow().AddRenderer(self.renMapOutcome)
                self.renMapOutcome.RemoveAllViewProps()
                #print("Left")
                if(self.labelsLh[cellPicker.GetPointId()] == -1 or cellPicker.GetPointId() == -1):
                    #print("Not a valid point")
                    pass
                else:
                    clr = self.metaLh[self.labelsLh[cellPicker.GetPointId()]]["color"]
                    #print("Point ID is", cellPicker.GetPointId())
                    #print(self.regionsLh[self.uniqueLabelsLh.tolist().index(self.labelsLh[cellPicker.GetPointId()])])
                    #print("Color is", clr)
                    #print("Area is", self.areaLh[self.uniqueLabelsLh.tolist().index(self.labelsLh[cellPicker.GetPointId()])])
                    self.brodmannTextActor.SetInput(str(self.regionsLh[self.uniqueLabelsLh.tolist().index(self.labelsLh[cellPicker.GetPointId()])].decode('utf-8')) + "\n" + "Normal" + "\n" + str("{0:.2f}".format(self.areaLh[self.uniqueLabelsLh.tolist().index(self.labelsLh[cellPicker.GetPointId()])])))
                    polyDataActor = self.polyDataLh[self.uniqueLabelsLh.tolist().index(self.labelsLh[cellPicker.GetPointId()])]
                    parcellationMapperLh = vtk.vtkOpenGLPolyDataMapper()
                    parcellationMapperLh.SetInputData(polyDataActor)
                    parcellationMapperLh.ScalarVisibilityOn()
                    self.parcellationActorLh = vtk.vtkActor()
                    self.parcellationActorLh.SetMapper(parcellationMapperLh)
                    self.parcellationActorLh.GetProperty().SetColor(clr[0]/255.0, clr[1]/255.0, clr[2]/255.0)
                    self.parcellationActorLh.SetOrigin(self.parcellationActorLh.GetCenter())
                    self.parcellationCurrentActor = self.parcellationActorLh
                    self.renMapOutcome.AddViewProp(self.parcellationActorLh)
                    self.renMapOutcome.AddActor(self.brodmannTextActor)
                    self.renMapOutcome.ResetCamera()
                    self.timer.start(200)
            if("rh" in str(itemType)):
                if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == False):
                    self.vtkWidget.GetRenderWindow().AddRenderer(self.renMapOutcome)
                self.renMapOutcome.RemoveAllViewProps()
                #print("Right")
                if(self.labelsRh[cellPicker.GetPointId()] == -1 or cellPicker.GetPointId() == -1):
                    #print("Not a valid point")
                    pass
                else:
                    clr = self.metaRh[self.labelsRh[cellPicker.GetPointId()]]["color"]
                    #print("Point ID is", cellPicker.GetPointId())
                    #print(self.regionsRh[self.uniqueLabelsRh.tolist().index(self.labelsRh[cellPicker.GetPointId()])])
                    #print("Color is", clr)
                    #print("Area is", self.areaRh[self.uniqueLabelsRh.tolist().index(self.labelsRh[cellPicker.GetPointId()])])
                    self.brodmannTextActor.SetInput(str(self.regionsRh[self.uniqueLabelsRh.tolist().index(self.labelsRh[cellPicker.GetPointId()])].decode('utf-8')) + "\n" + "Normal" + "\n" + str("{0:.2f}".format(self.areaRh[self.uniqueLabelsRh.tolist().index(self.labelsRh[cellPicker.GetPointId()])])))
                    polyDataActor = self.polyDataRh[self.uniqueLabelsRh.tolist().index(self.labelsRh[cellPicker.GetPointId()])]
                    parcellationMapperRh = vtk.vtkOpenGLPolyDataMapper()
                    parcellationMapperRh.SetInputData(polyDataActor)
                    parcellationMapperRh.ScalarVisibilityOn()
                    self.parcellationActorRh = vtk.vtkActor()
                    self.parcellationActorRh.SetMapper(parcellationMapperRh)
                    self.parcellationActorRh.GetProperty().SetColor(clr[0]/255.0, clr[1]/255.0, clr[2]/255.0)
                    self.parcellationActorRh.SetOrigin(self.parcellationActorRh.GetCenter())
                    self.parcellationCurrentActor = self.parcellationActorRh
                    self.renMapOutcome.AddViewProp(self.parcellationActorRh)
                    self.renMapOutcome.AddActor(self.brodmannTextActor)
                    self.renMapOutcome.ResetCamera()
                    self.timer.start(200)
            
            if itemType==None: # Itemtype is None for lesions. They only have Ids.
                self.timer.stop()
                if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == True):
                    self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renMapOutcome)
                # Highlight the picked actor by changing its properties
                self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                self.NewPickedActor.GetProperty().SetDiffuse(1.0)
                self.NewPickedActor.GetProperty().SetSpecular(0.0)
                self.NewPickedActor.GetProperty().SetRepresentationToWireframe()
                #self.NewPickedActor.GetProperty().SetOpacity(0.5)
                #print(self.NewPickedActor.GetMapper().GetScalarRange())
                #print(self.NewPickedActor)
                #itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationKey)

                centerOfMassFilter = vtk.vtkCenterOfMass()
                centerOfMassFilter.SetInputData(self.NewPickedActor.GetMapper().GetInput())
                #print(self.NewPickedActor.GetMapper().GetInput())
                centerOfMassFilter.SetUseScalarsAsWeights(False)
                centerOfMassFilter.Update()

                self.centerOfMass = centerOfMassFilter.GetCenter()

                # Get slice numbers for setting the MPRs.
                sliceNumbers = computeSlicePositionFrom3DCoordinates(self.subjectFolder, self.centerOfMass)
                
                self.sliderA.setValue(sliceNumbers[2])
                self.sliderB.setValue(sliceNumbers[1])
                self.sliderC.setValue(sliceNumbers[0])

            if lesionID!=None:
                self.overlayDataMain["Lesion ID"] = str(lesionID)
                self.overlayDataMain["Centroid"] = str("{0:.2f}".format(self.centerOfMass[0])) +", " +  str("{0:.2f}".format(self.centerOfMass[1])) + ", " + str("{0:.2f}".format(self.centerOfMass[2]))
                #self.overlayDataMain["Selection Type"] = str(itemType)
                self.overlayDataMain["Voxel Count"] = self.lesionNumberOfPixels[int(lesionID)-1]
                self.overlayDataMain["Elongation"] = "{0:.2f}".format(self.lesionElongation[int(lesionID)-1])
                self.overlayDataMain["Lesion Perimeter"] = "{0:.2f}".format(self.lesionPerimeter[int(lesionID)-1])
                self.overlayDataMain["Lesion Spherical Radius"] = "{0:.2f}".format(self.lesionSphericalRadius[int(lesionID)-1])
                self.overlayDataMain["Lesion Spherical Perimeter"] = "{0:.2f}".format(self.lesionSphericalPerimeter[int(lesionID)-1])
                self.overlayDataMain["Lesion Flatness"] = "{0:.2f}".format(self.lesionFlatness[int(lesionID)-1])
                self.overlayDataMain["Lesion Roundness"] = "{0:.2f}".format(self.lesionRoundness[int(lesionID)-1])
                if (self.lesionSeededFiberTracts == True):
                    actorCollection = self.GetDefaultRenderer().GetActors()
                    for actor in actorCollection:
                        actorName = actor.GetProperty().GetInformation().Get(self.informationKey)
                        if(actorName=="structural tracts"):
                            self.GetDefaultRenderer().RemoveActor(actor)

                    #lesionPointDataSet = self.rhactor.GetMapper().GetInput()
                    lesionPointDataSet = self.NewPickedActor.GetMapper().GetInput()
                    streamActor = computeStreamlines(self.subjectFolder, self.centerOfMass, self.lesionSphericalRadius[int(lesionID)-1], lesionPointDataSet)
                    information = vtk.vtkInformation()
                    information.Set(self.informationKey,"structural tracts")
                    streamActor.GetProperty().SetInformation(information)
                    self.GetDefaultRenderer().AddActor(streamActor)
            else:
                self.overlayDataMain["Lesion ID"] = "NA"
                self.overlayDataMain["Centroid"] = "NA"
                self.overlayDataMain["Voxel Count"] = "NA"
                self.overlayDataMain["Elongation"] = "NA"
                self.overlayDataMain["Lesion Perimeter"] = "NA"
                self.overlayDataMain["Lesion Spherical Radius"] = "NA"
                self.overlayDataMain["Lesion Spherical Perimeter"] = "NA"
                self.overlayDataMain["Lesion Flatness"] = "NA"
                self.overlayDataMain["Lesion Roundness"] = "NA"

            updateOverlayText(self.iren, self.overlayDataMain, self.overlayDataGlobal, self.textActorLesionStatistics, self.textActorGlobal)
            self.iren.Render()
            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor
        
        self.OnLeftButtonDown()
        return

'''
##########################################################################
    Compute Lesion Properties using ITK Connected Component Analysis.
    Returns: Connected Component Output Image, filter object.
##########################################################################
'''
def computeLesionProperties(subjectFolder):
    imageLesionMask = sitk.ReadImage(subjectFolder + "\\lesionMask\\Consensus.nii")
    # Binary threshold filter.
    binaryThresholdFilter = sitk.BinaryThresholdImageFilter()
    binaryThresholdFilter.SetOutsideValue(0)
    binaryThresholdFilter.SetInsideValue(1)
    binaryThresholdFilter.SetLowerThreshold(0.8)
    binaryThresholdFilter.SetUpperThreshold(1)
    binaryImage = binaryThresholdFilter.Execute(imageLesionMask)
    # Connected component filter.
    connectedComponentFilter = sitk.ConnectedComponentImageFilter()
    connectedComponentImage = connectedComponentFilter.Execute(binaryImage)
    return connectedComponentImage, connectedComponentFilter

'''
##########################################################################
    Compute streamlines using temperature scalars.
    Returns: Nothing
##########################################################################
'''
def computeStreamlines(subjectFolder, seedCenter = None, seedRadius = None, lesionPointDataSet = None):
    temperatureDataFileName = subjectFolder + "\\heatMaps\\aseg.auto_temperature.nii"
    niftiReaderTemperature = vtk.vtkNIFTIImageReader()
    niftiReaderTemperature.SetFileName(temperatureDataFileName)
    niftiReaderTemperature.Update()
    cellDerivatives = vtk.vtkCellDerivatives()
    cellDerivatives.SetInputConnection(niftiReaderTemperature.GetOutputPort())
    cellDerivatives.Update()
    cellDataToPointData = vtk.vtkCellDataToPointData()
    cellDataToPointData.SetInputConnection(cellDerivatives.GetOutputPort())
    cellDataToPointData.Update()

    # Transform for temperature/gradient data
    QFormMatrixTemperature = niftiReaderTemperature.GetQFormMatrix()
    qFormListTemperature = [0] * 16 #the matrix is 4x4
    QFormMatrixTemperature.DeepCopy(qFormListTemperature, QFormMatrixTemperature)
    transformGradient = vtk.vtkTransform()
    transformGradient.PostMultiply()
    transformGradient.SetMatrix(qFormListTemperature)
    transformGradient.Update()
    
    # Create point source and actor
    # psource = vtk.vtkPointSource()
    # if(seedCenter!=None):
    #     psource.SetNumberOfPoints(500)
    #     psource.SetCenter(seedCenter)
    #     psource.SetRadius(seedRadius)
    # else:
    #     psource.SetNumberOfPoints(500)
    #     psource.SetCenter(127,80,150)
    #     psource.SetRadius(80)
    #pointSourceMapper = vtk.vtkPolyDataMapper()
    #pointSourceMapper.SetInputConnection(psource.GetOutputPort())
    #pointSourceActor = vtk.vtkActor()
    #pointSourceActor.SetMapper(pointSourceMapper)

    # if(seedCenter!=None):
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(cellDataToPointData.GetOutputPort())
    transformFilter.SetTransform(transformGradient)
    transformFilter.Update()

    # Perform stream tracing
    streamers = vtk.vtkStreamTracer()
    streamers.SetInputConnection(transformFilter.GetOutputPort())
    # if(seedCenter!=None):
    #     streamers.SetInputConnection(transformFilter.GetOutputPort())
    # else:
    #     streamers.SetInputConnection(cellDataToPointData.GetOutputPort())
    streamers.SetIntegrationDirectionToForward()
    streamers.SetComputeVorticity(False)
    #streamers.SetSourceConnection(psource.GetOutputPort())
    streamers.SetSourceData(lesionPointDataSet)
    
    # streamers.SetMaximumPropagation(100.0)
    # streamers.SetInitialIntegrationStep(0.05)
    # streamers.SetTerminalSpeed(.51)

    streamers.SetMaximumPropagation(100.0)
    streamers.SetInitialIntegrationStep(0.2)
    streamers.SetTerminalSpeed(.01)
    streamers.Update()
    tubes = vtk.vtkTubeFilter()
    tubes.SetInputConnection(streamers.GetOutputPort())
    tubes.SetRadius(0.5)
    tubes.SetNumberOfSides(3)
    tubes.CappingOn()
    tubes.SetVaryRadius(0)
    lut = vtk.vtkLookupTable()
    lut.SetHueRange(.667, 0.0)
    lut.Build()
    streamerMapper = vtk.vtkPolyDataMapper()
    streamerMapper.SetInputConnection(tubes.GetOutputPort())
    streamerMapper.SetLookupTable(lut)
    streamerActor = vtk.vtkActor()
    streamerActor.SetMapper(streamerMapper)

    
    # if(seedCenter!=None):
    #     pass
    # else:
    #     streamerActor.SetUserTransform(transformGradient)
    streamerMapper.Update()

    # writer = vtk.vtkXMLPolyDataWriter()
    # writer.SetFileName("D:\\streamlines.vtp")
    # writer.SetInputData(tubes.GetOutput())
    # writer.Write()

    # plyWriter = vtk.vtkPLYWriter()
    # plyWriter.SetFileName("D:\\streamlines.ply")
    # plyWriter.SetInputData(tubes.GetOutput())
    # plyWriter.Write()

    return streamerActor

'''
##########################################################################
    Compute transformation matrix for json data
    Returns: JSON data transformation matrix
##########################################################################
'''
def getJsonDataTransformMatrix(subjectFolder):
    mrmlDataFileGradient2 = open (subjectFolder + "\\meta\\mrmlGradient2.txt" , 'r')
    arrayListGradient2 = list(np.asfarray(np.array(mrmlDataFileGradient2.readline().split(",")),float))
    arrayListGradient2[0]= arrayListGradient2[0] * -1 # A flip needed.
    transformMat = np.array(arrayListGradient2)
    matrix= np.reshape(transformMat, (4, 4))
    return matrix


'''
##########################################################################
    Use a color transfer Function to generate the colors in the lookup table.
    See: http://www.vtk.org/doc/nightly/html/classvtkColorTransferFunction.html
    :param: tableSize - The table size
    :return: The lookup table.
##########################################################################
'''
def MakeLUTFromCTF(tableSize):
    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()
    # Green to tan.
    ctf.AddRGBPoint(0.0, 1, 0, 0)
    ctf.AddRGBPoint(0.5, 0.865, 0.865, 0.865)
    ctf.AddRGBPoint(1.0, 0.677, 0.492, 0.093)

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(tableSize)
    lut.Build()

    for i in range(0, tableSize):
        rgb = list(ctf.GetColor(float(i) / tableSize)) + [1]
        lut.SetTableValue(i, rgb)

    return lut

'''
##########################################################################
    Use a color transfer Function to generate the colors in the lookup table.
    See: http://www.vtk.org/doc/nightly/html/classvtkColorTransferFunction.html
    :param: tableSize - The table size
    :return: The lookup table.
##########################################################################
'''
def MakeLUTFromCTFDistance(tableSize):
    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()
    # Green to tan.
    ctf.AddRGBPoint(0.0, 1, 0, 0)
    ctf.AddRGBPoint(0.5, 1, 1, 1)
    ctf.AddRGBPoint(1.0, 0, 1, 0)

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(tableSize)
    lut.Build()

    for i in range(0, tableSize):
        rgb = list(ctf.GetColor(float(i) / tableSize)) + [1]
        lut.SetTableValue(i, rgb)

    return lut

'''
##########################################################################
    Extract lesions by processing labelled lesion mask data.
    Returns: Lesion actors.
##########################################################################
'''
def extractLesions(subjectFolder, labelCount, informationKey, informationKeyID, requestedVisualizationType, lesionAverageIntensity, lesionAverageSurroundingIntensity, lesionRegionNumber, probeLesions=False):
    # Load lesion mask
    niftiReaderLesionMask = vtk.vtkNIFTIImageReader()
    niftiReaderLesionMask.SetFileName(subjectFolder + "\\lesionMask\\ConnectedComponents.nii")
    niftiReaderLesionMask.Update()

    # Read QForm matrix from mask data.
    QFormMatrixMask = niftiReaderLesionMask.GetQFormMatrix()
    qFormListMask = [0] * 16 #the matrix is 4x4
    QFormMatrixMask.DeepCopy(qFormListMask, QFormMatrixMask)

    lesionActors = []
    surface = vtk.vtkDiscreteMarchingCubes()
    surface.SetInputConnection(niftiReaderLesionMask.GetOutputPort())
    for i in range(labelCount):
        surface.SetValue(i,i+1)
    surface.Update()
    component = vtk.vtkPolyData()
    component.DeepCopy(surface.GetOutput())

    transform = vtk.vtkTransform()
    transform.Identity()
    transform.SetMatrix(qFormListMask)
    transform.Update()
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(surface.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    # Have a raw lesion surface view.
    if(requestedVisualizationType == "Full Data View - Raw"):
        for i in range(labelCount):
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(transformFilter.GetOutput())
            threshold.ThresholdBetween(i+1,i+1)
            threshold.Update()

            geometryFilter = vtk.vtkGeometryFilter()
            geometryFilter.SetInputData(threshold.GetOutput())
            geometryFilter.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputConnection(geometryFilter.GetOutputPort())
            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(lesionMapper)
            #information = vtk.vtkInformation()
            #information.Set(informationKey,"lesions")
            #lesionActor.GetProperty().SetInformation(information)
            informationID = vtk.vtkInformation()
            informationID.Set(informationKeyID,str(i+1))
            lesionActor.GetProperty().SetInformation(informationID)
            lesionActors.append(lesionActor)

    # Apply probe filtering also.
    if(requestedVisualizationType == "Lesion Colored - Continuous"):
        niftiReader = vtk.vtkNIFTIImageReader()
        niftiReader.SetFileName(subjectFolder + "\\structural\\T1IntensityDifference.nii")
        niftiReader.Update()
        QFormMatrixT1 = niftiReader.GetQFormMatrix() # Read QForm matrix from T1 data.
        qFormListT1 = [0] * 16 #the matrix is 4x4
        QFormMatrixT1.DeepCopy(qFormListT1, QFormMatrixT1)

        volumeTransform = vtk.vtkTransform()
        volumeTransform.SetMatrix(qFormListT1)
        volumeTransform.Update()
        # Set transformation for volume data.
        transformVolume = vtk.vtkTransformFilter()
        transformVolume.SetInputData(niftiReader.GetOutput())
        transformVolume.SetTransform(volumeTransform)
        transformVolume.Update()

        for i in range(labelCount):
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(transformFilter.GetOutput())
            threshold.ThresholdBetween(i+1,i+1)
            threshold.Update()

            geometryFilter = vtk.vtkGeometryFilter()
            geometryFilter.SetInputData(threshold.GetOutput())
            geometryFilter.Update()

            # Apply probeFilter
            probeFilter = vtk.vtkProbeFilter()
            probeFilter.SetSourceConnection(transformVolume.GetOutputPort())
            probeFilter.SetInputData(geometryFilter.GetOutput())
            probeFilter.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputConnection(probeFilter.GetOutputPort())
            lesionMapper.SetScalarRange(probeFilter.GetOutput().GetScalarRange())
            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(lesionMapper)
            #information = vtk.vtkInformation()
            #information.Set(informationKey,"lesions")
            #lesionActor.GetProperty().SetInformation(information)
            informationID = vtk.vtkInformation()
            informationID.Set(informationKeyID,str(i+1))
            lesionActor.GetProperty().SetInformation(informationID)
            lesionActors.append(lesionActor)

    # Lesion Colored - Discrete visualization.
    if(requestedVisualizationType == "Lesion Colored - Discrete"):
        mylookupTable = MakeLUTFromCTF(labelCount)
        intensityDifferenceDiscrete = np.subtract(lesionAverageSurroundingIntensity,lesionAverageIntensity)
        for i in range(labelCount):
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(transformFilter.GetOutput())
            threshold.ThresholdBetween(i+1,i+1)
            threshold.Update()

            geometryFilter = vtk.vtkGeometryFilter()
            geometryFilter.SetInputData(threshold.GetOutput())
            geometryFilter.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputConnection(geometryFilter.GetOutputPort())
            lesionMapper.ScalarVisibilityOff()

            myrgb = [0,0,0]
            mylookupTable.GetColor(intensityDifferenceDiscrete[i], myrgb)

            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(lesionMapper)
            lesionActor.GetProperty().SetColor(myrgb[0], myrgb[1], myrgb[2])
            #information = vtk.vtkInformation()
            #information.Set(informationKey,"lesions")
            #lesionActor.GetProperty().SetInformation(information)
            informationID = vtk.vtkInformation()
            informationID.Set(informationKeyID,str(i+1))
            lesionActor.GetProperty().SetInformation(informationID)
            lesionActors.append(lesionActor)

    # Lesion Colored - Distance visualization.
    if(requestedVisualizationType == "Lesion Colored - Distance"):
        mylookupTable = MakeLUTFromCTFDistance(labelCount)
        for i in range(labelCount):
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(transformFilter.GetOutput())
            threshold.ThresholdBetween(i+1,i+1)
            threshold.Update()

            geometryFilter = vtk.vtkGeometryFilter()
            geometryFilter.SetInputData(threshold.GetOutput())
            geometryFilter.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputConnection(geometryFilter.GetOutputPort())
            lesionMapper.ScalarVisibilityOff()

            myrgb = [0,0,0]
            mylookupTable.GetColor(lesionRegionNumber[i], myrgb)

            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(lesionMapper)
            lesionActor.GetProperty().SetColor(myrgb[0], myrgb[1], myrgb[2])
            #information = vtk.vtkInformation()
            #information.Set(informationKey,"lesions")
            #lesionActor.GetProperty().SetInformation(information)
            informationID = vtk.vtkInformation()
            informationID.Set(informationKeyID,str(i+1))
            lesionActor.GetProperty().SetInformation(informationID)
            lesionActors.append(lesionActor)

    return lesionActors


'''
##########################################################################
    Get lesion IDs that are falling below or equal to a specific threshold value
    Returns: Lesion actor indices.
##########################################################################
'''
def getThresholdLesionIndices(sliderValue, parameterArray, NewMax, NewMin):
    OldMin = 1
    OldMax = 1000
    OldValue = sliderValue
    OldRange = 999
    thresholdValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    removeIndices = []
    for index in range(1, len(parameterArray)+1):
        if (parameterArray[index-1] > thresholdValue):
            removeIndices.append(index)
    return removeIndices

'''
##########################################################################
    Refresh lesion display based on params.
    Returns: Lesion actor indices.
##########################################################################
'''
def filterLesionsAndRender(removeIndices, actorList, informationKeyID, renderer):
    removeIndicesString = [str(i) for i in removeIndices] 
    for actor in actorList:
        if(actor.GetProperty().GetInformation().Get(informationKeyID)!=None): # Check if this is a lesion.
            if(actor.GetProperty().GetInformation().Get(informationKeyID) in removeIndicesString):
                renderer.RemoveActor(actor)
            else:
                renderer.AddActor(actor)
        

'''
##########################################################################
    Compute slide numbers from 3D world coordinates.
    Returns: IJK coordinates (slice positions).
##########################################################################
'''
def computeSlicePositionFrom3DCoordinates(subjectFolder, pt):
    fileNameT1 = str(subjectFolder + "\\structural\\T1.nii")
    # Read T1 data.
    readerT1 = sitk.ImageFileReader()
    readerT1.SetFileName(fileNameT1)
    readerT1.LoadPrivateTagsOn()
    readerT1.ReadImageInformation()
    readerT1.LoadPrivateTagsOn()
    imageT1 = sitk.ReadImage(fileNameT1)
    return imageT1.TransformPhysicalPointToIndex(pt)

'''
##########################################################################
    Read annotation files from freesurfer.
    Returns: Color arrays for left and right hemispheres.
##########################################################################
'''
def initializeSurfaceAnnotationColors(subjectFolder, rhwhiteMapper, lhwhiteMapper):
    fileNameRhAnnot = str(subjectFolder + "\\surfaces\\rh.aparc.annot")
    fileNameLhAnnot = str(subjectFolder + "\\surfaces\\lh.aparc.annot")
    # Read annotation files.
    labelsRh, ctabRh, regionsRh = freesurfer.read_annot(fileNameRhAnnot, orig_ids=False)
    labelsLh, ctabLh, regionsLh = freesurfer.read_annot(fileNameLhAnnot, orig_ids=False)
    metaRh = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regionsRh, ctabRh)))
    metaLh = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regionsLh, ctabLh)))
    numberOfPointsRh = len(labelsRh)
    numberOfPointsLh = len(labelsLh)
    uniqueLabelsRh = np.unique(labelsRh)
    uniqueLabelsLh = np.unique(labelsLh)

    vertexIdsRh = np.arange(numberOfPointsRh)
    vertexIdsLh = np.arange(numberOfPointsLh)
    listOfSegmentedParcellationVerticesRh = []
    for val in uniqueLabelsRh:
        vertices = vertexIdsRh[labelsRh == val]
        listOfSegmentedParcellationVerticesRh.append(vertices)

    listOfSegmentedParcellationVerticesLh = []
    for val in uniqueLabelsLh:
        vertices = vertexIdsLh[labelsLh == val]
        listOfSegmentedParcellationVerticesLh.append(vertices)

    colorDataRh = vtk.vtkUnsignedCharArray()
    colorDataRh.SetNumberOfComponents(3)
    colorDataLh = vtk.vtkUnsignedCharArray()
    colorDataLh.SetNumberOfComponents(3)

    for index in range(numberOfPointsRh):
        if(labelsRh[index] == -1):
            clr = [25,5,25]
        else:
            clr = metaRh[labelsRh[index]]["color"]
        colorDataRh.InsertNextTuple3(clr[0], clr[1], clr[2])

    for index in range(numberOfPointsLh):
        if(labelsLh[index] == -1):
            clr = [25,5,25]
        else:
            clr = metaLh[labelsLh[index]]["color"]
        colorDataLh.InsertNextTuple3(clr[0], clr[1], clr[2])

    areaRh = {}
    polyDataRh = []
    for i in range(len(listOfSegmentedParcellationVerticesRh)):
        ids = vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        for elem in listOfSegmentedParcellationVerticesRh[i]:
            ids.InsertNextValue(elem)


        selectionNode = vtk.vtkSelectionNode()
        selectionNode.SetFieldType(vtk.vtkSelectionNode.POINT)
        selectionNode.SetContentType(vtk.vtkSelectionNode.INDICES)
        selectionNode.SetSelectionList(ids)
        selectionNode.GetProperties().Set(vtk.vtkSelectionNode.CONTAINING_CELLS(), 1)
        selection = vtk.vtkSelection()
        selection.AddNode(selectionNode)
        extractSelection = vtk.vtkExtractSelection()
        extractSelection.SetInputData(0,rhwhiteMapper.GetInput())
        extractSelection.SetInputData(1, selection)
        extractSelection.Update()

        selected = vtk.vtkUnstructuredGrid()
        selected.ShallowCopy(extractSelection.GetOutput())
        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputData(selected)
        geometryFilter.Update()
        mypolydata = geometryFilter.GetOutput()
        polyDataRh.append(mypolydata)

        measured_polydata = vtk.vtkMassProperties()
        measured_polydata.SetInputData(mypolydata)
        surfaceArea = measured_polydata.GetSurfaceArea()
        areaRh[i] = surfaceArea

    areaLh = {}
    polyDataLh = []
    for i in range(len(listOfSegmentedParcellationVerticesLh)):
        ids = vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        for elem in listOfSegmentedParcellationVerticesLh[i]:
            ids.InsertNextValue(elem)

        selectionNode = vtk.vtkSelectionNode()
        selectionNode.SetFieldType(vtk.vtkSelectionNode.POINT)
        selectionNode.SetContentType(vtk.vtkSelectionNode.INDICES)
        selectionNode.SetSelectionList(ids)
        selectionNode.GetProperties().Set(vtk.vtkSelectionNode.CONTAINING_CELLS(),1)
        selection = vtk.vtkSelection()
        selection.AddNode(selectionNode)
        extractSelection = vtk.vtkExtractSelection()
        extractSelection.SetInputData(0,lhwhiteMapper.GetInput())
        extractSelection.SetInputData(1, selection)
        extractSelection.Update()

        selected = vtk.vtkUnstructuredGrid()
        selected.ShallowCopy(extractSelection.GetOutput())
        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputData(selected)
        geometryFilter.Update()
        mypolydata = geometryFilter.GetOutput()
        polyDataLh.append(mypolydata)

        measured_polydata = vtk.vtkMassProperties()
        measured_polydata.SetInputData(mypolydata)
        surfaceArea = measured_polydata.GetSurfaceArea()
        areaLh[i] = surfaceArea
    
    print("Completed")
    
    return colorDataRh, colorDataLh, labelsRh, labelsLh, regionsRh, regionsLh, metaRh, metaLh, uniqueLabelsRh, uniqueLabelsLh, areaRh, areaLh, polyDataRh, polyDataLh

'''
##########################################################################
    Copy actor properties.
    Returns: propery collection
##########################################################################
'''
def saveActorProperties(actors):
    properties = []
    for actor in actors:
        actorProperty = vtk.vtkProperty()
        actorProperty.DeepCopy(actor.GetProperty())
        properties.append(actorProperty)
    return properties

'''
##########################################################################
    Apply actor properties from saved property.
    Returns: None
##########################################################################
'''
def restoreActorProperties(actors, properties):
    for index in range(len(properties)):
        actors[index].GetProperty().DeepCopy(properties[index])