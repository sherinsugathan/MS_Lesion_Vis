# This program reads connected component mask output along with T1 and T2. This is followed by computing intensity difference by considering the whole lesion.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json

subjectString = "07003SATH_DATA"
fileNameT1 = "C:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\structural\\T1.nii"
fileNameT2 = "C:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\structural\\T2.nii"
fileNameConnectedComponentMask = "C:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\lesionMask\\ConnectedComponents.nii"
#fileNameOutput = "D:\\ConnectedDilated.nii"
subjectFolder = "C:\\DATASET\\MS_SegmentationChallengeDataset\\" + subjectString

# Read T1 data.
readerT1 = sitk.ImageFileReader()
readerT1.SetFileName(fileNameT1)
readerT1.LoadPrivateTagsOn()
readerT1.ReadImageInformation()
readerT1.LoadPrivateTagsOn()
imageT1 = sitk.ReadImage(fileNameT1)

# Read Connected comoponent labelled mask data.
readerMask = sitk.ImageFileReader()
readerMask.SetFileName(fileNameConnectedComponentMask)
readerMask.LoadPrivateTagsOn()
readerMask.ReadImageInformation()
imageMask = sitk.ReadImage(fileNameConnectedComponentMask)

# Binary threshold filter for all lesions.
binaryThresholdFilterAll = sitk.BinaryThresholdImageFilter()
binaryThresholdFilterAll.SetOutsideValue(0)
binaryThresholdFilterAll.SetInsideValue(1)
binaryThresholdFilterAll.SetLowerThreshold(1)
binaryThresholdFilterAll.SetUpperThreshold(276)
binaryImageAll = binaryThresholdFilterAll.Execute(imageMask)

# load precomputed lesion properties
data = {}
structureInfo = None
with open(subjectFolder + "\\structure-def.json") as fp: 
    structureInfo = json.load(fp)
numberOfLesionElements = len(structureInfo)

for jsonElementIndex in (range(1,numberOfLesionElements+1)):
    # Dilated all image
    dilateFilter = sitk.BinaryDilateImageFilter()
    dilateFilter.SetForegroundValue(jsonElementIndex)
    dilateFilter.SetKernelRadius(2)
    dilatedImage = dilateFilter.Execute(imageMask)

    # Binary threshold filter for single original lesion.
    binaryThresholdFilterLesion = sitk.BinaryThresholdImageFilter()
    binaryThresholdFilterLesion.SetOutsideValue(0)
    binaryThresholdFilterLesion.SetInsideValue(1)
    binaryThresholdFilterLesion.SetLowerThreshold(jsonElementIndex)
    binaryThresholdFilterLesion.SetUpperThreshold(jsonElementIndex)
    binaryImageSingleLesion = binaryThresholdFilterLesion.Execute(imageMask)

    # Binary threshold filter for single dilated lesion.
    binaryThresholdFilterLesion = sitk.BinaryThresholdImageFilter()
    binaryThresholdFilterLesion.SetOutsideValue(0)
    binaryThresholdFilterLesion.SetInsideValue(1)
    binaryThresholdFilterLesion.SetLowerThreshold(jsonElementIndex)
    binaryThresholdFilterLesion.SetUpperThreshold(jsonElementIndex)
    binaryImageLesion = binaryThresholdFilterLesion.Execute(dilatedImage)

    andImageFilter = sitk.AndImageFilter()
    andedImage = andImageFilter.Execute(binaryImageLesion, binaryImageAll)
    xorImageFilter = sitk.XorImageFilter()
    XoredImage = xorImageFilter.Execute(andedImage, binaryImageLesion)

    l = binaryImageSingleLesion.GetSize()[0]
    w = binaryImageSingleLesion.GetSize()[1]
    h = binaryImageSingleLesion.GetSize()[2]

    countLesion = 0
    countSurrounding = 0
    sumLesion = 0
    sumSurrounding = 0
    for i in range(l):
        for j in range(w):
            for k in range(h):
                if(binaryImageSingleLesion.GetPixel(i, j, k) == 1):
                    sumLesion = imageT1.GetPixel(i, j, k) + sumLesion
                    countLesion = countLesion +1
                if(XoredImage.GetPixel(i, j , k) == 1):
                    sumSurrounding = imageT1.GetPixel(i, j, k) + sumSurrounding
                    countSurrounding = countSurrounding + 1
    averageLesion = sumLesion / countLesion
    averageSurrounding = sumSurrounding / countSurrounding

    print(averageLesion)
    print(averageSurrounding)



    for p in structureInfo[str(jsonElementIndex)]:
        lesionDataDict = p
        lesionDataDict['AverageLesionIntensity'] = averageLesion
        lesionDataDict['AverageSurroundingIntensity'] = averageSurrounding
        data[jsonElementIndex]=[]
        data[jsonElementIndex].append(lesionDataDict) 

    print("Finished processing lesion " + str(jsonElementIndex))  
    
with open(subjectFolder + '\\structure-def2.json', 'w') as fp:
    json.dump(data, fp, indent=4)

#sitk.WriteImage(XoredImage, fileNameOutput)

print("FINISHED")