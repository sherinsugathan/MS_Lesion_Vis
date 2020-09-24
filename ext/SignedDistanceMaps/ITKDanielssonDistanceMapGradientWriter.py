# This program will read aseg brain segmentation file, extract out the ventricles as binary masks and then compute the 
import vtk
import numpy as np
import os
import sys
import json

import os,sys,inspect
current_dir = os.path.dirname(os.path.realpath(__file__))
target_dir = os.path.join(current_dir, '..', '..')
sys.path.insert(0,target_dir) # Mechanism for importing LesionUtils.

import LesionUtils
import pickle
import SimpleITK as sitk
import math

'''
##########################################################################
    Compute streamlines using temperature scalars. (FOR SDM only)
    Returns: tube polydata
##########################################################################
'''
def computeStreamlines(subjectFolder, lesionPointDataSet = None, gradientFilePath = None):
    niftiReaderTemperature = vtk.vtkNIFTIImageReader()
    niftiReaderTemperature.SetFileName(gradientFilePath)
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
    
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(cellDataToPointData.GetOutputPort())
    transformFilter.SetTransform(transformGradient)
    transformFilter.Update()

    # Perform stream tracing
    streamers = vtk.vtkStreamTracer()
    streamers.SetInputConnection(transformFilter.GetOutputPort())

    streamers.SetIntegrationDirectionToForward()
    streamers.SetComputeVorticity(False)
    streamers.SetSourceData(lesionPointDataSet)

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
    tubes.Update()
    return tubes.GetOutput()


rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\"
listOfSubjects = ["DTIDATA"]
#listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]
#listOfSubjects = ["01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]

for subject in listOfSubjects:

    asegSegmentationFile = rootPath + subject + "\\heatMaps\\aseg.auto.nii"
    brainMaskFile = rootPath + subject + "\\heatMaps\\brainmask.nii"
    outputFolder = rootPath + subject + "\\sdm\\sdm_gradient.nii"
    # Read segmentation files and the brain mask file.
    imageAseg = sitk.ReadImage(asegSegmentationFile)
    imageBrainMask = sitk.ReadImage(brainMaskFile)
    # Threshold first ventricle.
    thresholdFilter1 = sitk.BinaryThresholdImageFilter()
    thresholdFilter1.SetLowerThreshold(4)
    thresholdFilter1.SetUpperThreshold(4)
    thresholdedImage1 = thresholdFilter1.Execute(imageAseg)
    # Threshold second ventricle.
    thresholdFilter2 = sitk.BinaryThresholdImageFilter()
    thresholdFilter2.SetLowerThreshold(43)
    thresholdFilter2.SetUpperThreshold(43)
    thresholdedImage2 = thresholdFilter2.Execute(imageAseg)
    # Create a binary mask of brain using thresholding.
    brainMaskThresholdFilter = sitk.BinaryThresholdImageFilter()
    brainMaskThresholdFilter.SetLowerThreshold(0)
    brainMaskThresholdFilter.SetUpperThreshold(0)
    brainMaskThresholdFilter.SetInsideValue(0)
    brainMaskThresholdFilter.SetOutsideValue(1)
    binaryBrainMask = brainMaskThresholdFilter.Execute(imageBrainMask)
    # Combine left and right ventricle mask images into one.
    ORImageFilter = sitk.OrImageFilter()
    ORedImage = ORImageFilter.Execute(thresholdedImage1, thresholdedImage2)
    # Compute distance map using ventricle mask image.
    distanceMapImageFilter = sitk.DanielssonDistanceMapImageFilter()
    distanceMapImageFilter.InputIsBinaryOn()
    gradientImage = distanceMapImageFilter.Execute(ORedImage)
    # Mask the gradient image using the brain mask.
    maskImageFilter = sitk.MaskImageFilter()
    maskedGradientImage = maskImageFilter.Execute(gradientImage, binaryBrainMask)
    sitk.WriteImage(maskedGradientImage, outputFolder)


    surfaceFileLh = rootPath + subject + "\\surfaces\\lh.white.obj"
    surfaceFileRh = rootPath + subject + "\\surfaces\\rh.white.obj"
    translationFilePath = rootPath + subject + "\\meta\\cras.txt"
    f = open(translationFilePath, "r")
    t_vector = []
    for t in f:
        t_vector.append(t)
    t_vector = list(map(float, t_vector))
    transform = vtk.vtkTransform()
    transform.PostMultiply()
    transform.Translate(t_vector[0], t_vector[1], t_vector[2])
    f.close()

    structureInfo = None
    with open(rootPath + subject + "\\structure-def3.json") as fp: 
        structureInfo = json.load(fp)
    numberOfLesionElements = len(structureInfo) 

    informationUniqueKey = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")
    lesionActors = LesionUtils.extractLesions2(rootPath + subject, informationUniqueKey, False)
    numberOfLesionActors = len(lesionActors)

    if(numberOfLesionElements!=numberOfLesionActors):
        print("LESION COUNT MISMATCH. PREMATURE TERMINATION!")

    mb = vtk.vtkMultiBlockDataSet()
    mb.SetNumberOfBlocks(numberOfLesionElements)

    for jsonElementIndex in (range(1,numberOfLesionElements+1)):
        # Compute streamlines.
        print("Processing:", subject, ",", str(jsonElementIndex), "/", str(numberOfLesionActors))
        streamLinePolyData = computeStreamlines(rootPath + subject, lesionActors[jsonElementIndex-1].GetMapper().GetInput(), outputFolder)

        mb.SetBlock(jsonElementIndex-1, streamLinePolyData)
        
        
    writer = vtk.vtkXMLMultiBlockDataWriter()
    writer.SetFileName(rootPath + subject + '\\surfaces\\streamlinesMultiBlockDatasetSDM.xml')
    writer.SetInputData(mb)
    writer.Write()
    print("Processed:", subject, "BLOCKDATASET WRITE SUCCESS")

print("ALL SUBJECTS COMPLETED PROCESSING...")


