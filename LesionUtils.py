import os
import vtk
import numpy as np
	
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
    Returns: A mapper object representing the probe filter output.
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
    lesionActor = vtk.vtkActor()
    lesionActor.SetMapper(lesionMapper)
    lookupTable = vtk.vtkLookupTable()
    lookupTable.SetNumberOfTableValues(256)
    lookupTable.Build()
    lesionMapper.SetScalarRange(probeFilter.GetOutput().GetScalarRange())
                
    return lesionMapper

