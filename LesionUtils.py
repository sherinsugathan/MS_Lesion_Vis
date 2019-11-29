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
    components = list()
    idx=0
    while True:
        connectivityFilter.AddSpecifiedRegion(idx)
        connectivityFilter.Update()
        component = vtk.vtkPolyData()
        component.DeepCopy(connectivityFilter.GetOutput())
        if component.GetNumberOfCells() <=0:
            break
        mapper = vtk.vtkOpenGLPolyDataMapper()
        mapper.SetInputDataObject(component)
        mapper.SetScalarRange(probeFilterObject.GetOutput().GetScalarRange())
        mapper.Update()
        components.append(mapper)
        connectivityFilter.DeleteSpecifiedRegion(idx)
        idx +=1
    return components, numberOfExtractedRegions


'''
##########################################################################
    Capture a screnshot from the main renderer.
    Returns: Nothing
##########################################################################
'''
def captureScreenshot(renderWindow): 
    windowToImageFilter = vtk.vtkWindowToImageFilter()
    windowToImageFilter.SetInput(renderWindow)
    #windowToImageFilter.SetMagnification(3) #set the resolution of the output image (3 times the current resolution of vtk render window)
    windowToImageFilter.SetInputBufferTypeToRGBA() #also record the alpha (transparency) channel
    windowToImageFilter.ReadFrontBufferOff() # read from the back buffer
    windowToImageFilter.Update()
    timestr = time.strftime("%Y%m%d-%H%M%S")
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(timestr + ".png")
    writer.SetInputConnection(windowToImageFilter.GetOutputPort())
    writer.Write()


class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,parent=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)

        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
 
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
            self.NewPickedActor.GetProperty().SetOpacity(0.0)

            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor
        
        self.OnLeftButtonDown()
        return

'''
##########################################################################
    Compute Lesion Properties using ITK Connected Component Analysis.
    Returns: 
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



