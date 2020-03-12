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
import pickle

def MakeCellData(min, max, colors, polyDataObject):
    '''
    Create the cell data using the colors from the lookup table.
    :param: tableSize - The table size
    :param: lut - The lookup table.
    :param: colors - A reference to a vtkUnsignedCharArray().
    '''
    pointCount = polyDataObject.GetPointData().GetScalars().GetNumberOfTuples()
    for i in range(pointCount):
        val = polyDataObject.GetPointData().GetScalars().GetTuple1(i)
        if(val < min): # HYPO sample
            colors.InsertNextTuple3(103,169,207)
        if(val >= min and val <= max): # ISO sample
            colors.InsertNextTuple3(247,247,247)
        if(val > max): # HYPER sample
            colors.InsertNextTuple3(239,138,98)

def MakeCellDataDiscrete(min, max, colors, lesionIntensityDifferences):
    '''
    Create the cell data using the colors from the lookup table.
    :param: tableSize - The table size
    :param: lut - The lookup table.
    :param: colors - A reference to a vtkUnsignedCharArray().
    '''
    for i in range(len(intensityDifferenceDiscrete)):
        val = intensityDifferenceDiscrete[i]
        if(val < min): # HYPO sample
            colors.InsertNextTuple3(103,169,207)
        if(val >= min and val <= max): # ISO sample
            colors.InsertNextTuple3(247,247,247)
        if(val > max): # HYPER sample
            colors.InsertNextTuple3(239,138,98)


rootPath = "D:\\OneDrive-MyDatasets\\OneDrive - ODMAIL\\Datasets\\ModifiedDataSet\\MS_SegmentationChallengeDataset\\"
listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]
#listOfSubjects = ["01040VANE_DATA"]
contVolumeFileNames = ["T1IntensityDifference.nii", "T2IntensityDifference.nii", "3DFLAIRIntensityDifference.nii"]


for subject in listOfSubjects:
    structureInfo = None
    with open(rootPath + subject + "\\structure-def3.json") as fp: 
        structureInfo = json.load(fp)
    numberOfLesionElements = len(structureInfo)
    # lesionAverageIntensity = []
    # lesionAverageSurroundingIntensity = []
    # lesionRegionNumberQuantized = []
    # for jsonElementIndex in (range(1, numberOfLesionElements+1)):
    #     for p in structureInfo[str(jsonElementIndex)]:
    #         lesionAverageIntensity.append(p["AverageLesionIntensity"])
    #         lesionAverageSurroundingIntensity.append(p["AverageSurroundingIntensity"])
    #         lesionRegionNumberQuantized.append(p["RegionNumberQuantized"])

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

    for contVolumeFileName in contVolumeFileNames:
        contVolumeFilePath = rootPath + subject + "\\structural\\" + contVolumeFileName

        # Read continuous Intensity difference volume file
        # Load T1 volume
        niftiReader = vtk.vtkNIFTIImageReader()
        niftiReader.SetFileName(contVolumeFilePath)
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

        colorList = []
        #intensityDifferenceDiscrete = np.subtract(lesionAverageSurroundingIntensity,lesionAverageIntensity)
        #colorDataDiscrete = vtk.vtkUnsignedCharArray()
        #colorDataDiscrete.SetName('Colors') # Any name will work here.
        #colorDataDiscrete.SetNumberOfComponents(3)
        #MakeCellDataDiscrete(-50, 50, colorDataDiscrete, intensityDifferenceDiscrete)
        print("NUMBER OF LESIONS", numberOfLesionElements)
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

            # Apply probeFilter
            probeFilter = vtk.vtkProbeFilter()
            probeFilter.SetSourceConnection(transformVolume.GetOutputPort())
            probeFilter.SetInputData(geometryFilter.GetOutput())
            probeFilter.Update()

            MakeCellData(-50, 50, colorData, probeFilter.GetOutput()) 
            colorList.append(np.array(colorData))
            
            #multiBlockDataset.SetBlock(i,lesionMapper.GetInput())
            #print(subject, "PROCESSING LESION", i,"/",numberOfLesionElements)

            print("COLOR list length", colorData.GetNumberOfTuples())

        writeItem = None
        if("T1" in contVolumeFileName):
            writeItem = "T1"
        if("T2" in contVolumeFileName):
            writeItem = "T2"
        if("FLAIR" in contVolumeFileName):
            writeItem = "FLAIR"
        writeContFileName = rootPath + subject + "\\surfaces\\colorArrayCont" + writeItem + ".pkl"
        with open(writeContFileName, "wb") as f:
            pickle.dump(colorList, f)
        
        # Write lesions to file.
        # mbw = vtk.vtkXMLMultiBlockDataWriter()
        # mbw.SetFileName(rootPath + subject + "\\surfaces\\lesions.vtm")
        # mbw.SetDataModeToAscii()
        # mbw.SetInputData(multiBlockDataset)
        # mbw.Write()
        print(subject, writeItem, "CONTINUOUS FILE WRITTEN SUCCESSFULLY")
