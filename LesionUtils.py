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

            itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationKey)
            lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationKeyID)
            if itemType==None: # Itemtype is None for lesions. They only have Ids.
                # Highlight the picked actor by changing its properties
                self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                self.NewPickedActor.GetProperty().SetDiffuse(1.0)
                self.NewPickedActor.GetProperty().SetSpecular(0.0)
                self.NewPickedActor.GetProperty().SetRepresentationToWireframe()
                self.NewPickedActor.GetProperty().SetOpacity(0.5)
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
                currentSliderValueA = self.sliderA.value()
                currentSliderValueB = self.sliderB.value()
                currentSliderValueC = self.sliderC.value()

                self.sliderA.setValue(sliceNumbers[1])
                self.sliderB.setValue(sliceNumbers[2])
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

                    streamActor = computeStreamlines(self.subjectFolder, self.centerOfMass, self.lesionSphericalRadius[int(lesionID)-1])
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
def computeStreamlines(subjectFolder, seedCenter = None, seedRadius = None):
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
    if(seedCenter!=None):
        psource.SetNumberOfPoints(1500)
        psource.SetCenter(seedCenter)
        psource.SetRadius(seedRadius)
    else:
        psource.SetNumberOfPoints(9500)
        psource.SetCenter(127,80,150)
        psource.SetRadius(80)
    #pointSourceMapper = vtk.vtkPolyDataMapper()
    #pointSourceMapper.SetInputConnection(psource.GetOutputPort())
    #pointSourceActor = vtk.vtkActor()
    #pointSourceActor.SetMapper(pointSourceMapper)

    if(seedCenter!=None):
        transformFilter = vtk.vtkTransformFilter()
        transformFilter.SetInputConnection(cellDataToPointData.GetOutputPort())
        transformFilter.SetTransform(transformGradient)
        transformFilter.Update()

    # Perform stream tracing
    streamers = vtk.vtkStreamTracer()
    if(seedCenter!=None):
        streamers.SetInputConnection(transformFilter.GetOutputPort())
    else:
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
    if(seedCenter!=None):
        pass
    else:
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


'''
##########################################################################
    Extract lesions by processing labelled lesion mask data.
    Returns: Lesion actors.
##########################################################################
'''
def extractLesions(subjectFolder, labelCount, informationKey, informationKeyID, probeLesions=False):
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

    # Apply probe filtering also.
    if(probeLesions==True):
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

        # Check if probing lesion surface with intensity volume is requested or not.
        if(probeLesions==False):
            mapper = vtk.vtkOpenGLPolyDataMapper()
            mapper.SetInputData(geometryFilter.GetOutput())
            mapper.Update()
            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(mapper)
            #information = vtk.vtkInformation()
            #information.Set(informationKey,"lesions")
            #lesionActor.GetProperty().SetInformation(information)
            informationID = vtk.vtkInformation()
            informationID.Set(informationKeyID,str(i+1))
            lesionActor.GetProperty().SetInformation(informationID)
            lesionActors.append(lesionActor)
        else:
            # Apply probeFilter
            probeFilter = vtk.vtkProbeFilter()
            probeFilter.SetSourceConnection(transformVolume.GetOutputPort())
            probeFilter.SetInputData(geometryFilter.GetOutput())
            probeFilter.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputConnection(probeFilter.GetOutputPort())
            lookupTable = vtk.vtkLookupTable()
            lookupTable.SetNumberOfTableValues(256)
            lookupTable.Build()
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