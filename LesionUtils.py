import os
import vtk
import numpy as np
import time
import SimpleITK as sitk

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
    Perform probe filtering after applying necessary transformations.
    Returns: 1. A mapper object representing the probe filter output.
             2. A probeFilter object containing the volume colored lesion vertices.
##########################################################################
'''
def probeSurfaceWithVolume(subjectFolder):
    if(os.path.isfile(subjectFolder + "\\meta\\mrmlMask.txt") and os.path.isfile(subjectFolder + "\\meta\\mrmlMask.txt")):
        mrmlDataFileLesion = open ( subjectFolder + "\\meta\\mrmlMask.txt" , 'r') # Corrected transformation data for lesion. Used when there is mismatch with volume nifti.
    else:
        mrmlDataFileLesion = open ( subjectFolder + "\\meta\\mrml.txt" , 'r') # Normal transformation data for lesion. Used when there is a match with nifti.

    mrmlDataFileVolume = open ( subjectFolder + "\\meta\\mrml.txt" , 'r') # Transformation for volume data

    volumeTransform = vtk.vtkTransform()
    surfaceTransform = vtk.vtkTransform()
    arrayListLesion = list(np.asfarray(np.array(mrmlDataFileLesion.readline().split(",")),float))
    arrayListVolume = list(np.asfarray(np.array(mrmlDataFileVolume.readline().split(",")),float))

    surfaceTransform.SetMatrix(arrayListLesion)
    volumeTransform.SetMatrix(arrayListVolume)
    surfaceTransform.Update()
    volumeTransform.Update()

    #Load volume data.  
    niftiReader = vtk.vtkNIFTIImageReader()
    niftiReader.SetFileName(subjectFolder + "\\structural\\T1.nii")
    niftiReader.Update()

    # Load Lesion Data
    lesionReader = vtk.vtkOBJReader()
    lesionReader.SetFileName(subjectFolder + "\\surfaces\\lesions.obj")
    lesionReader.Update()

    # Set transformation for volume data.
    transformVolume = vtk.vtkTransformFilter()
    transformVolume.SetInputData(niftiReader.GetOutput())
    transformVolume.SetTransform(volumeTransform)
    transformVolume.Update()

    # Set transformation for surface data.
    transformLesion = vtk.vtkTransformPolyDataFilter()
    transformLesion.SetInputData(lesionReader.GetOutput())
    transformLesion.SetTransform(surfaceTransform)
    transformLesion.Update()

    # Apply probeFilter
    probeFilter = vtk.vtkProbeFilter()
    probeFilter.SetSourceConnection(transformVolume.GetOutputPort())
    probeFilter.SetInputData(transformLesion.GetOutput())
    probeFilter.Update()

    lesionMapper = vtk.vtkOpenGLPolyDataMapper()
    lesionMapper.SetInputConnection(probeFilter.GetOutputPort())
    lookupTable = vtk.vtkLookupTable()
    lookupTable.SetNumberOfTableValues(256)
    lookupTable.Build()
    lesionMapper.SetScalarRange(probeFilter.GetOutput().GetScalarRange())
                
    return lesionMapper, probeFilter

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
def updateOverlayText(renderWindow, overlayDictionary, overlayTextActor): 
    overlayText =""
    for key in overlayDictionary.keys():
        overlayText = overlayText + str(key) + ": " + str(overlayDictionary[key]) + "\n"
    overlayTextActor.SetInput(overlayText)

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
 
    def __init__(self,parent=None,iren=None, overlayDataMain=None, textActorLesionStatistics=None, informationKey = None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)

        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.iren = iren
        self.overlayDataMain = overlayDataMain
        self.textActorLesionStatistics = textActorLesionStatistics
        self.informationKey = informationKey
 
    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        
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
            # Highlight the picked actor by changing its properties
            self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)
            self.NewPickedActor.GetProperty().SetOpacity(0.1)

            lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationKey)
            centerOfMassFilter = vtk.vtkCenterOfMass()
            centerOfMassFilter.SetInputData(self.NewPickedActor.GetMapper().GetInput())
            #print(self.NewPickedActor.GetMapper().GetInput())
            centerOfMassFilter.SetUseScalarsAsWeights(False)
            centerOfMassFilter.Update()

            self.centerOfMass = centerOfMassFilter.GetCenter()
            #print(self.centerOfMass)
            #self.overlayDataMain["Lesion Load"] = str(self.centerOfMass[0]) + str(self.centerOfMass[1]) + str(self.centerOfMass[2])
            self.overlayDataMain["Lesion ID"] = str(lesionID)
            updateOverlayText(self.iren, self.overlayDataMain, self.textActorLesionStatistics)
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
def computeStreamlines(subjectFolder):
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

    # CRAS translation for gradient data.
    crasDataFile = open(subjectFolder + "\\meta\\crasGradient.txt" , 'r')
    cras_t_vector = []
    for t in crasDataFile:
        cras_t_vector.append(t)
    cras_t_vector = list(map(float, cras_t_vector))
    transform2 = vtk.vtkTransform()
    transform2.PostMultiply()
    transform2.Translate(cras_t_vector[0], cras_t_vector[1], cras_t_vector[2])

    # Transform for temperature data
    transformGradient = vtk.vtkTransform()
    mrmlDataFileGradient = open (subjectFolder + "\\meta\\mrmlGradient.txt" , 'r')
    mrmlDataFileGradient2 = open (subjectFolder + "\\meta\\mrmlGradient2.txt" , 'r')
    arrayListGradient = list(np.asfarray(np.array(mrmlDataFileGradient.readline().split(",")),float))
    arrayListGradient2 = list(np.asfarray(np.array(mrmlDataFileGradient2.readline().split(",")),float))
    transformGradient.PostMultiply()
    transformGradient.SetMatrix(arrayListGradient)
    transformGradient.Concatenate(arrayListGradient2)
    transformGradient.Concatenate(transform2)
    transformGradient.Update()
    
    # Create point source and actor
    psource = vtk.vtkPointSource()
    psource.SetNumberOfPoints(9500)
    psource.SetCenter(127,80,150)
    psource.SetRadius(80)
    pointSourceMapper = vtk.vtkPolyDataMapper()
    pointSourceMapper.SetInputConnection(psource.GetOutputPort())
    pointSourceActor = vtk.vtkActor()
    pointSourceActor.SetMapper(pointSourceMapper)

    # Perform stream tracing
    streamers = vtk.vtkStreamTracer()
    streamers.SetInputConnection(cellDataToPointData.GetOutputPort())
    streamers.SetIntegrationDirectionToBoth()
    streamers.SetSourceConnection(psource.GetOutputPort())
    streamers.SetMaximumPropagation(100.0)
    streamers.SetInitialIntegrationStep(0.2)
    streamers.SetTerminalSpeed(.01)
    streamers.Update()
    tubes = vtk.vtkTubeFilter()
    tubes.SetInputConnection(streamers.GetOutputPort())
    tubes.SetRadius(0.3)
    tubes.SetNumberOfSides(6)
    tubes.SetVaryRadius(0)
    lut = vtk.vtkLookupTable()
    lut.SetHueRange(.667, 0.0)
    lut.Build()
    streamerMapper = vtk.vtkPolyDataMapper()
    streamerMapper.SetInputConnection(tubes.GetOutputPort())
    streamerMapper.SetLookupTable(lut)
    streamerActor = vtk.vtkActor()
    streamerActor.SetMapper(streamerMapper)
    streamerActor.SetUserTransform(transformGradient)

    return streamerActor

'''
##########################################################################
    Compute transformations required for json data
    Returns: Transform object.
##########################################################################
'''
def computeJsonDataTransform(subjectFolder):
    # Transform for temperature data
    transformGradient = vtk.vtkTransform()
    mrmlDataFileGradient2 = open (subjectFolder + "\\meta\\mrmlGradient2.txt" , 'r')
    arrayListGradient2 = list(np.asfarray(np.array(mrmlDataFileGradient2.readline().split(",")),float))
    arrayListGradient2[0]= arrayListGradient2[0] * -1 # A flip needed.
    transformGradient.PostMultiply()
    transformGradient.Concatenate(arrayListGradient2)
    transformGradient.Update()
    return transformGradient

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