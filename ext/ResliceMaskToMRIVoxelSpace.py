# This program make the voxel space of mask and T1 same. This is done by resampling the mask data by using T1 as a reference.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json
from nibabel import freesurfer

#listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA", "07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]
listOfSubjects = ["07040DORE_DATA", "07043SEME_DATA"]
modalities = ["T1", "T2", "3DFLAIR"]

for subject in listOfSubjects:
    for modality in modalities:
        #subject = "08037ROGU_DATA"
        connectedComponentMaskFile = "D:\\DATASET\\MS_SegmentationChallengeDataset\\" + subject + "\\lesionMask\\ConnectedComponents.nii"
        T1VolumeFile = "D:\\DATASET\\MS_SegmentationChallengeDataset\\" + subject + "\\structural\\" + modality + ".nii"
        voxelSpaceCorrectedFile = "D:\\DATASET\\MS_SegmentationChallengeDataset\\" + subject + "\\lesionMask\\ConnectedComponents"+modality+"VoxelSpaceCorrected.nii"

        imageT1 = sitk.ReadImage(T1VolumeFile)
        imageMask = sitk.ReadImage(connectedComponentMaskFile)

        origin = imageT1.GetOrigin()
        dimension = imageT1.GetDimension()
        size = imageT1.GetSize()
        spacing = imageT1.GetSpacing()
        directionMat = imageT1.GetDirection()
        pixelIDValue = imageT1.GetPixelIDValue()
        pixelIDTypeAsString = imageT1.GetPixelIDTypeAsString()
        componentsPerPixel = imageT1.GetNumberOfComponentsPerPixel()

        originMask = imageMask.GetOrigin()
        dimensionMask = imageMask.GetDimension()
        sizeMask = imageMask.GetSize()
        spacingMask = imageMask.GetSpacing()
        directionMatMask = imageMask.GetDirection()
        pixelIDValueMask = imageMask.GetPixelIDValue()
        pixelIDTypeAsStringMask = imageMask.GetPixelIDTypeAsString()
        componentsPerPixelMask = imageMask.GetNumberOfComponentsPerPixel()
        


        # print("Origin", origin)
        # print("Dimension", dimension)
        # print("Size", size)
        # print("Spacing", spacing)
        # print("DirectionMat", directionMat)
        # print("PixelIDValue", pixelIDValue)
        # print("pixelIDTypeAsString", pixelIDTypeAsString)
        # print("Components Per Pixel", componentsPerPixel)

        # print("Origin", originMask)
        # print("Dimension", dimensionMask)
        # print("Size", sizeMask)
        # print("Spacing", spacingMask)
        # print("DirectionMat", directionMatMask)
        # print("PixelIDValue", pixelIDValueMask)
        # print("pixelIDTypeAsString", pixelIDTypeAsStringMask)
        # print("Components Per Pixel", componentsPerPixelMask)


        resampler = sitk.ResampleImageFilter()
        resampler.SetReferenceImage(imageT1)
        resampler.SetDefaultPixelValue(0.0)
        resampler.SetSize(imageT1.GetSize())
        resampler.SetOutputSpacing(imageT1.GetSpacing())
        resampler.SetOutputOrigin(imageT1.GetOrigin())
        resampler.SetOutputDirection(imageT1.GetDirection())
        resampler.SetInterpolator(sitk.sitkLinear)
        resampled_img = resampler.Execute(imageMask)
        sitk.WriteImage(resampled_img, voxelSpaceCorrectedFile)
        print("PROCESSED", subject, modality)

print("DONE")