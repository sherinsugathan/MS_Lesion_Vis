# This program computes colors based distance(per vertex) and writes to files.
import numpy as np
import sys, os
import math
import ctypes
import json
import cv2
from nibabel import freesurfer
import pickle
import vtk

import os,sys,inspect
current_dir = os.path.dirname(os.path.realpath(__file__))
target_dir = os.path.join(current_dir, '..')
sys.path.insert(0,target_dir) # Mechanism for importing LesionUtils.

import LesionUtils

def MakeCellData(min, max, colors, polyDataObject):#, polyDataObjectAseg):
    '''
    Create the cell data using the colors from the lookup table.
    :param: tableSize - The table size
    :param: lut - The lookup table.
    :param: colors - A reference to a vtkUnsignedCharArray().
    '''
    pointCount = polyDataObject.GetPointData().GetScalars().GetNumberOfTuples()
    for i in range(pointCount):
        val = int(polyDataObject.GetPointData().GetScalars().GetTuple1(i))
        #valBackgroundCheck = int(polyDataObjectAseg.GetPointData().GetScalars().GetTuple1(i))
        entry = 0
        # 43 and 4: ventricles ; 42 and 3 are gray matter ;  2 and 41 are white matter
        # if(val == 3 or valBackgroundCheck ==0 or valBackgroundCheck == 3 or valBackgroundCheck == 42): # If encounterd a background voxel as per aseg data then assign high and return. 42 and 3 are gray matter. 2 and 41 are white matter.
        #     colors.InsertNextTuple3(217,71,1) # Apple extreme red if outside brain surface.
        #     print("hi")
        #     continue
        # if(val == 0):# and (valBackgroundCheck == 43 or valBackgroundCheck == 4 )):# and (valBackgroundCheck == 43 or valBackgroundCheck == 4)): # 43 and 4 are ventricles
        #     colors.InsertNextTuple3(254,237,222) # white
        #     print("fr")
        # # if(val == 1 and (valBackgroundCheck == 43 or valBackgroundCheck == 4)): # 43 and 4 are ventricles
        # #     colors.InsertNextTuple3(254,237,222)
        # #     print("fr2")
        if(val == 0): # periventricular
            colors.InsertNextTuple3(254,237,222)
            entry = entry + 1
            continue
        if(val == 1): # ventricle + 1
            colors.InsertNextTuple3(253,190,133)
            entry = entry + 1 
            continue
        if(val == 2): # outer -1
            colors.InsertNextTuple3(253,141,60)
            entry = entry + 1
            continue
        if(val == 3): # Outer most lesions
            colors.InsertNextTuple3(217,71,1)
            entry = entry + 1
            continue
        if(val == 4): # black background
            colors.InsertNextTuple3(217,71,1)
            entry = entry + 1
            continue

        # if(entry >1):
        #     print("Multiple entries")
        if(entry ==0):
            print(val)
            print("No entries")

#fileNameQuantized = "D:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\heatMaps\\aseg.auto_temperature_quantized.nii"
rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\"
listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]
#listOfSubjects = ["DTIDATA"]
#listOfSubjects = ["01040VANE_DATA"]
#contVolumeFileNames = ["T1IntensityDifference.nii", "T2IntensityDifference.nii", "3DFLAIRIntensityDifference.nii"]
informationUniqueKey = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")

for subject in listOfSubjects:
    structureInfo = None
    with open(rootPath + subject + "\\structure-def.json") as fp: 
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

    # connectedComponentsMaskFile = rootPath + subject + "\\lesionMask\\ConnectedComponents.nii"
    # # Load lesion mask
    # niftiReaderLesionMask = vtk.vtkNIFTIImageReader()
    # niftiReaderLesionMask.SetFileName(connectedComponentsMaskFile)
    # niftiReaderLesionMask.Update()

    # # Read QForm matrix from mask data.
    # QFormMatrixMask = niftiReaderLesionMask.GetQFormMatrix()
    # qFormListMask = [0] * 16 #the matrix is 4x4
    # QFormMatrixMask.DeepCopy(qFormListMask, QFormMatrixMask)

    # surface = vtk.vtkDiscreteMarchingCubes()
    # surface.SetInputConnection(niftiReaderLesionMask.GetOutputPort())
    # for i in range(numberOfLesionElements):
    #     surface.SetValue(i,i+1)
    # surface.Update()

    # transform = vtk.vtkTransform()
    # transform.Identity()
    # transform.SetMatrix(qFormListMask)
    # transform.Update()
    # transformFilter = vtk.vtkTransformFilter()
    # transformFilter.SetInputConnection(surface.GetOutputPort())
    # transformFilter.SetTransform(transform)
    # transformFilter.Update()

    #asegVolumeFilePath = rootPath + subject + "\\heatMaps\\aseg.auto_temperature_quantized.nii"
    asegVolumeFilePath = rootPath + subject + "\\heatMaps\\aseg.auto_temperature_quantized_ventricle_modified.nii"
    print("Processing file path is", asegVolumeFilePath)
    
    #asegFilePath = rootPath + subject + "\\heatMaps\\aseg.auto.nii"

    # Read continuous Intensity difference volume file
    # Load T1 volume
    niftiReader = vtk.vtkNIFTIImageReader()
    niftiReader.SetFileName(asegVolumeFilePath)
    niftiReader.Update()

    #niftiReaderAseg = vtk.vtkNIFTIImageReader()
    #niftiReaderAseg.SetFileName(asegFilePath)
    #niftiReaderAseg.Update()

    QFormMatrixT1 = niftiReader.GetQFormMatrix() # Read QForm matrix from T1 data.
    qFormListT1 = [0] * 16 #the matrix is 4x4
    QFormMatrixT1.DeepCopy(qFormListT1, QFormMatrixT1)
    volumeTransform = vtk.vtkTransform()
    volumeTransform.SetMatrix(qFormListT1)
    volumeTransform.Update()

    # QFormMatrixT1Aseg = niftiReaderAseg.GetQFormMatrix() # Read QForm matrix from T1 data.
    # qFormListT1Aseg = [0] * 16 #the matrix is 4x4
    # QFormMatrixT1Aseg.DeepCopy(qFormListT1Aseg, QFormMatrixT1Aseg)
    # volumeTransformAseg = vtk.vtkTransform()
    # volumeTransformAseg.SetMatrix(qFormListT1Aseg)
    # volumeTransformAseg.Update()

    # Set transformation for volume data.
    transformVolume = vtk.vtkTransformFilter()
    transformVolume.SetInputData(niftiReader.GetOutput())
    transformVolume.SetTransform(volumeTransform)
    transformVolume.Update()

    # # Set transformation for aseg data.
    # transformVolumeAseg = vtk.vtkTransformFilter()
    # transformVolumeAseg.SetInputData(niftiReaderAseg.GetOutput())
    # transformVolumeAseg.SetTransform(volumeTransformAseg)
    # transformVolumeAseg.Update()

    lesionActors = LesionUtils.extractLesions2(rootPath + subject, informationUniqueKey)

    colorList = []
    #intensityDifferenceDiscrete = np.subtract(lesionAverageSurroundingIntensity,lesionAverageIntensity)
    # colorDataDiscrete = vtk.vtkUnsignedCharArray()
    # colorDataDiscrete.SetName('Colors') # Any name will work here.
    # colorDataDiscrete.SetNumberOfComponents(3)
    # MakeCellDataDiscrete(-50, 50, colorDataDiscrete, intensityDifferenceDiscrete)
    print("NUMBER OF LESIONS", numberOfLesionElements)
    for i in range(numberOfLesionElements):
        colorData = vtk.vtkUnsignedCharArray()
        colorData.SetName('Colors') # Any name will work here.
        colorData.SetNumberOfComponents(3)

        # threshold = vtk.vtkThreshold()
        # threshold.SetInputData(transformFilter.GetOutput())
        # threshold.ThresholdBetween(i+1,i+1)
        # threshold.Update()

        # geometryFilter = vtk.vtkGeometryFilter()
        # geometryFilter.SetInputData(threshold.GetOutput())
        # geometryFilter.Update()

        print("lesion number of points", lesionActors[i].GetMapper().GetInput().GetNumberOfPoints())

        # Apply probeFilter
        probeFilter = vtk.vtkProbeFilter()
        probeFilter.SetSourceConnection(transformVolume.GetOutputPort())
        probeFilter.SetInputData(lesionActors[i].GetMapper().GetInput())
        probeFilter.PassPointArraysOff()
        probeFilter.SpatialMatchOff()
        probeFilter.Update()

        print("probefilter number of points", probeFilter.GetOutput().GetPointData().GetScalars().GetNumberOfTuples())

        # # Apply probeFilter on aseg data (to check if interesecting with background or not)
        # probeFilterAseg = vtk.vtkProbeFilter()
        # probeFilterAseg.SetSourceConnection(transformVolumeAseg.GetOutputPort())
        # probeFilterAseg.SetInputData(geometryFilter.GetOutput())
        # probeFilterAseg.Update()


        MakeCellData(-50, 50, colorData, probeFilter.GetOutput())#, probeFilterAseg.GetOutput()) 
        colorList.append(np.array(colorData))

        lesionActors[i].GetMapper().GetInput().GetPointData().SetScalars(colorData)
        
        #multiBlockDataset.SetBlock(i,lesionMapper.GetInput())
        #print(subject, "PROCESSING LESION", i,"/",numberOfLesionElements)

        #print("COLOR list length", colorData.GetNumberOfTuples())
        #print("PROCESSED LESION", i, "/", numberOfLesionElements)

    writeContFileName = rootPath + subject + "\\surfaces\\colorArrayDistMRI2.pkl"
    with open(writeContFileName, "wb") as f:
        pickle.dump(colorList, f)
    
    # Write lesions to file.
    # mbw = vtk.vtkXMLMultiBlockDataWriter()
    # mbw.SetFileName(rootPath + subject + "\\surfaces\\lesions.vtm")
    # mbw.SetDataModeToAscii()
    # mbw.SetInputData(multiBlockDataset)
    # mbw.Write()
    print(subject, "colorArrayDistMRI2.pkl", "DISTANCE COLOR FILE WRITTEN SUCCESSFULLY")


# TESTING CODE. DO NOT ENABLE WHEN BEING USED FOR PROCESSING DATA. (TESTING PURPOSES ONLY)
# informationUniqueKey = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")
# subjectFolder = rootPath + "01040VANE_DATA"
# lesionActors = LesionUtils.extractLesions2(subjectFolder, informationUniqueKey)

ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
for actor in lesionActors:
    actor.GetMapper().ScalarVisibilityOn()
    ren.AddActor(actor)
ren.SetBackground(0, 0, 0.0)
renWin.SetSize(900, 900)
iren.Initialize()
ren.ResetCamera()
renWin.Render()
iren.Start()