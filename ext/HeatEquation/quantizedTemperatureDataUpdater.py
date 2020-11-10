# This program updates the values in aseg.auto_temperature_quantized.nii. The values in ventricles are made non-zero.
import numpy as np
import sys, os
import math
import ctypes
import json
import cv2
from nibabel import freesurfer
import SimpleITK as sitk
import pickle
import vtk

import os,sys,inspect
current_dir = os.path.dirname(os.path.realpath(__file__))
target_dir = os.path.join(current_dir, '..', '..')
sys.path.insert(0,target_dir) # Mechanism for importing LesionUtils.

import LesionUtils

rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\"
#listOfSubjects = ["01040VANE_DATA"]
listOfSubjects = ["DTIDATA", "01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]

# Iterate through all the subjects.
for subject in listOfSubjects:
    outputFileName = rootPath + subject + "\\heatMaps\\aseg.auto_temperature_quantized_ventricle_modified.nii"
    quantizedTemperatureFileName = rootPath + subject + "\\heatMaps\\aseg.auto_temperature_quantized.nii"
    asegSegmentationFileName = rootPath + subject + "\\heatMaps\\aseg.auto.nii"

    imageQuantized = sitk.ReadImage(quantizedTemperatureFileName)
    imageAseg = sitk.ReadImage(asegSegmentationFileName)
    # Lesion voxel values -> 43 and 4 are ventricles

    # Binary threshold filter for first ventricle (43)
    binaryThresholdV1 = sitk.BinaryThresholdImageFilter()
    binaryThresholdV1.SetOutsideValue(0)
    binaryThresholdV1.SetInsideValue(1)
    binaryThresholdV1.SetLowerThreshold(43)
    binaryThresholdV1.SetUpperThreshold(43)
    binaryImageV1 = binaryThresholdV1.Execute(imageAseg)

    # Binary threshold filter for second ventricle (4)
    binaryThresholdV2 = sitk.BinaryThresholdImageFilter()
    binaryThresholdV2.SetOutsideValue(0)
    binaryThresholdV2.SetInsideValue(1)
    binaryThresholdV2.SetLowerThreshold(4)
    binaryThresholdV2.SetUpperThreshold(4)
    binaryImageV2 = binaryThresholdV2.Execute(imageAseg)

    addImage = sitk.AddImageFilter()
    combinedVentricleBinaryImage = addImage.Execute(binaryImageV1, binaryImageV2)

    #sitk.WriteImage(combinedVentricleBinaryImage, tempFileOutName)
    l = combinedVentricleBinaryImage.GetSize()[0]
    w = combinedVentricleBinaryImage.GetSize()[1]
    h = combinedVentricleBinaryImage.GetSize()[2]

    for i in range(l):
        for j in range(w):
            for k in range(h):
                if(combinedVentricleBinaryImage.GetPixel(i, j, k) != 1 and imageQuantized.GetPixel(i, j, k)==0):
                    imageQuantized[i,j,k] = 4

    sitk.WriteImage(imageQuantized, outputFileName)
    print(subject, "SUCCESSFULLY COMPLETED")
print("PROCESSED ALL SUBJECTS")
