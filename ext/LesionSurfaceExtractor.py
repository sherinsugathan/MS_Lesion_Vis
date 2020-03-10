# This program extract and separate lesion surfaces based on connectivity and dumps the data as vtp files.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json
import cv2
from nibabel import freesurfer

# def MakeDummyScalarData(colors, polyDataObject):
#     '''
#     :param: colors - A reference to a vtkUnsignedCharArray().
#     '''
#     pointCount = polyDataObject.GetNumberOfPoints()
#     for i in range(pointCount):
#         colors.InsertNextTuple3(255,0,0) # Set RED as default color for lesion.


rootPath = "D:\\OneDrive-MyDatasets\\OneDrive - ODMAIL\\Datasets\\ModifiedDataSet\\MS_SegmentationChallengeDataset\\"
#listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]
listOfSubjects = ["01016SACH_DATA"]

for subject in listOfSubjects:
    structureInfo = None
    with open(rootPath + subject + "\\structure-def4.json") as fp: 
        structureInfo = json.load(fp)
    numberOfLesionElements = len(structureInfo)

    connectedComponentsMaskFile = rootPath + subject + "\\lesionMask\\ConnectedComponents.nii"
    # Load lesion mask
    niftiReaderLesionMask = vtk.vtkNIFTIImageReader()
    niftiReaderLesionMask.SetFileName(connectedComponentsMaskFile)
    niftiReaderLesionMask.Update()

    # Read QForm matrix from mask data.
    QFormMatrixMask = niftiReaderLesionMask.GetQFormMatrix()
    qFormListMask = [0] * 16 #the matrix is 4x4
    QFormMatrixMask.DeepCopy(qFormListMask, QFormMatrixMask)

    surface = vtk.vtkDiscreteMarchingCubes()
    surface.SetInputConnection(niftiReaderLesionMask.GetOutputPort())
    for i in range(numberOfLesionElements):
        surface.SetValue(i,i+1)
    surface.Update()

    transform = vtk.vtkTransform()
    transform.Identity()
    transform.SetMatrix(qFormListMask)
    transform.Update()
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(surface.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    multiBlockDataset = vtk.vtkMultiBlockDataSet()

    for i in range(numberOfLesionElements):
        colorData = vtk.vtkUnsignedCharArray()
        colorData.SetName('Colors') # Any name will work here.
        colorData.SetNumberOfComponents(3)

        threshold = vtk.vtkThreshold()
        threshold.SetInputData(transformFilter.GetOutput())
        threshold.ThresholdBetween(i+1,i+1)
        threshold.Update()

        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputData(threshold.GetOutput())
        geometryFilter.Update()

        #MakeDummyScalarData(colorData, geometryFilter.GetOutput())

        lesionMapper = vtk.vtkOpenGLPolyDataMapper()
        lesionMapper.SetInputConnection(geometryFilter.GetOutputPort())
        #lesionMapper.GetInput().GetPointData().SetScalars(colorData)
        lesionMapper.Update()

        

        multiBlockDataset.SetBlock(i,lesionMapper.GetInput())
        print(subject, "PROCESSING LESION", i,"/",numberOfLesionElements)
    

    
    # Write lesions to file.
    mbw = vtk.vtkXMLMultiBlockDataWriter()
    mbw.SetFileName(rootPath + subject + "\\surfaces\\lesions.vtm")
    mbw.SetDataModeToAscii()
    mbw.SetInputData(multiBlockDataset)
    mbw.Write()
    print("FILE WRITTEN SUCCESSFULLY")
