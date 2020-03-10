# This program reads connected component mask output along with T1 and T2. This is followed by computing intensity difference by considering the whole lesion.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json


connectedComponentsFilePath = "D:\\OneDrive-MyDatasets\\OneDrive - ODMAIL\\Datasets\\ModifiedDataSet\\MS_SegmentationChallengeDataset\\01016SACH_DATA\\lesionMask\\ConnectedComponents.nii"
T2FilePath = "D:\\OneDrive-MyDatasets\\OneDrive - ODMAIL\\Datasets\\ModifiedDataSet\\MS_SegmentationChallengeDataset\\01016SACH_DATA\\structural\\T2.nii"
rootPath = "D:\\OneDrive-MyDatasets\\OneDrive - ODMAIL\\Datasets\\ModifiedDataSet\\MS_SegmentationChallengeDataset\\"
subjectName = "01016SACH_DATA"
subjectFolder = rootPath + subjectName

imageMask = sitk.ReadImage(connectedComponentsFilePath)
imageVolumeData = sitk.ReadImage(T2FilePath)

# Resample volume data to match with lesionMask
resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(imageMask)
resampler.SetDefaultPixelValue(0.0)
resampler.SetSize(imageMask.GetSize())
resampler.SetOutputSpacing(imageMask.GetSpacing())
resampler.SetOutputOrigin(imageMask.GetOrigin())
resampler.SetOutputDirection(imageMask.GetDirection())
resampler.SetInterpolator(sitk.sitkLinear)
resampled_volume = resampler.Execute(imageVolumeData)

print("#### DIMS VOLUME", resampled_volume.GetWidth(), resampled_volume.GetHeight(), resampled_volume.GetDepth(), " #### DIMS MASK", imageMask.GetWidth(), imageMask.GetHeight(), imageMask.GetDepth())
print("ORIGIN VOLUME", resampled_volume.GetOrigin(), "ORIGIN MASK", imageMask.GetOrigin())
print("SPACING VOLUME", resampled_volume.GetSpacing(), "SPACING MASK", imageMask.GetSpacing())
print("PIXELTYPE VOLUME", resampled_volume.GetPixelIDTypeAsString(), "PIXELTYPE MASK", imageMask.GetPixelIDTypeAsString())

# quit()

# Binary threshold filter for all lesions.
binaryThresholdFilterAll = sitk.BinaryThresholdImageFilter()
binaryThresholdFilterAll.SetOutsideValue(0)
binaryThresholdFilterAll.SetInsideValue(1)
binaryThresholdFilterAll.SetLowerThreshold(1)
binaryThresholdFilterAll.SetUpperThreshold(276) # Set to high. must be higher than total number of lesions.
binaryImageAll = binaryThresholdFilterAll.Execute(imageMask)

print(binaryImageAll.GetPixelIDTypeAsString())

# load precomputed lesion properties
data = {}
structureInfo = None
with open(subjectFolder + "\\structure-def4.json") as fp: 
    structureInfo = json.load(fp)
numberOfLesionElements = len(structureInfo)

for jsonElementIndex in (range(1,numberOfLesionElements+1)): 
    # Binary threshold filter for single original lesion.
    binaryThresholdFilterSingleLesion = sitk.BinaryThresholdImageFilter()
    binaryThresholdFilterSingleLesion.SetOutsideValue(0)
    binaryThresholdFilterSingleLesion.SetInsideValue(1)
    binaryThresholdFilterSingleLesion.SetLowerThreshold(jsonElementIndex)
    binaryThresholdFilterSingleLesion.SetUpperThreshold(jsonElementIndex)
    binaryImageSingleLesion = binaryThresholdFilterSingleLesion.Execute(imageMask)

    # Create dilated single lesion
    dilatedSingleLesion = sitk.BinaryDilateImageFilter()
    dilatedSingleLesion.SetForegroundValue(1)
    dilatedSingleLesion.SetKernelRadius(1)
    dilatedSingleLesion = dilatedSingleLesion.Execute(binaryImageSingleLesion)

    # Create normal surrounding mask
    normalMaskExtract = sitk.XorImageFilter()
    normalMask = normalMaskExtract.Execute(binaryImageSingleLesion, dilatedSingleLesion)

    # All-lesion-mask AND normalMask (This will find intersection of lesions with normalMask)
    intersectLesionAndNormalMask = sitk.AndImageFilter()
    lesionIntersectionMask = intersectLesionAndNormalMask.Execute(normalMask, binaryImageAll)
    #print("HELLO",np.sum(sitk.GetArrayFromImage(lesionIntersectionMask)))

    # lesionIntersectionMask XOR normalMask (This will remove impact from other lesions in the captured surrounding tissue area mask)
    removeOtherLesionInfluencebyXOR = sitk.XorImageFilter()
    normalMaskPure = removeOtherLesionInfluencebyXOR.Execute(normalMask, lesionIntersectionMask)
    #sitk.WriteImage(normalMaskPure, "D:\\temp\\normalMaskPure.nii")

    maskImageFilterLesion = sitk.MaskImageFilter()
    lesionMaskedVolumeData = maskImageFilterLesion.Execute(resampled_volume, binaryImageSingleLesion)

    maskImageFilterNormal = sitk.MaskImageFilter()
    normalMaskedVolumeData = maskImageFilterNormal.Execute(resampled_volume, normalMaskPure)

    #buffer = lesionMaskedVolumeData.GetBufferAsInt16()
    ndArrayLesionMask = sitk.GetArrayFromImage(binaryImageSingleLesion)
    ndArrayNormalMask = sitk.GetArrayFromImage(normalMaskPure)
    ndArrayLesionVolumeData = sitk.GetArrayFromImage(lesionMaskedVolumeData)
    ndArrayNormalVolumeData = sitk.GetArrayFromImage(normalMaskedVolumeData)

    sumOfLesionVoxels = np.sum(ndArrayLesionVolumeData)
    numberOfLesionVoxels = (ndArrayLesionMask>0).sum()
    averageLesionVoxelIntensity = sumOfLesionVoxels/numberOfLesionVoxels

    sumOfNormalVoxels = np.sum(ndArrayNormalVolumeData)
    numberOfNormalVoxels = (ndArrayNormalMask>0).sum()
    averageNormalVoxelIntensity = sumOfNormalVoxels/numberOfNormalVoxels

    print("Average intensity lesion", averageLesionVoxelIntensity)
    print("Average intensity normal", averageNormalVoxelIntensity)



#sitk.WriteImage(resampled_volume, "D:\\temp\\newT1.nii")

print("FINISHED - SUCCESS")