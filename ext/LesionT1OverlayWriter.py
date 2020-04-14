# This program reads T1 data and corresponding consensus. The calculated intensity difference is burned back in T1 and saved as a new file.
# Purpose: Have an overlay of lesions on top of MPRs.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
subjectString = "01016SACH_DATA"
fileNameT1 = "D:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\structural\\T1.nii"
fileNameMask = "D:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\lesionMask\\ConsensusResampled cropped.nii"
fileNameOutput = "D:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\structural\\LesionT1Overlay.nii"

# Read T1 data.
readerT1 = sitk.ImageFileReader()
readerT1.SetFileName(fileNameT1)
readerT1.LoadPrivateTagsOn()
readerT1.ReadImageInformation()
readerT1.LoadPrivateTagsOn()
imageT1 = sitk.ReadImage(fileNameT1)

# Read Mask data.
readerMask = sitk.ImageFileReader()
readerMask.SetFileName(fileNameMask)
readerMask.LoadPrivateTagsOn()
readerMask.ReadImageInformation()
imageMask = sitk.ReadImage(fileNameMask)

l = readerT1.GetSize()[0]
w = readerT1.GetSize()[1]
h = readerT1.GetSize()[2]
# windowSize = 3
# padding = math.floor(windowSize/2)

for i in range(l):
    for j in range(w):
        for k in range(h):
            physicalLocation = imageMask.TransformIndexToPhysicalPoint((i, j, k))
            indexLocation = imageT1.TransformPhysicalPointToIndex(physicalLocation)
            if(imageMask.GetPixel(i,j,k)>0.01):
                imageT1[indexLocation[0], indexLocation[1], indexLocation[2]] = 255
                
                

# for i in range(padding,l-padding+1):
#     print("COMPLETED:"+str(i)+"/"+str(l-padding+1))
#     for j in range(padding,w-padding+1):
#         for k in range(padding,h-padding+1):
#             if(imageMask.GetPixel(i, j, k)>0.01):
#                 sumLesion = 0
#                 lesionCount = 0
#                 sumNormal = 0
#                 normalCount = 0
#                 for p in range(i-padding, i+padding+1):
#                     for q in range(j-padding, j+padding+1):
#                         for r in range(k-padding, k+padding+1):
#                             physicalLocation = imageMask.TransformIndexToPhysicalPoint((p, q, r))
#                             indexLocation = imageT1.TransformPhysicalPointToIndex(physicalLocation)
#                             if(imageMask.GetPixel(p, q, r) > 0.01):
#                                 lesionCount = lesionCount + 1
#                                 sumLesion = sumLesion + imageT1.GetPixel(indexLocation[0], indexLocation[1], indexLocation[2])
#                             else:
#                                 normalCount = normalCount + 1
#                                 sumNormal = sumNormal + imageT1.GetPixel(indexLocation[0], indexLocation[1], indexLocation[2])
#                 if(normalCount!=0 and lesionCount!=0): # Avoiding divide by zero error
#                     physicalLocation = imageMask.TransformIndexToPhysicalPoint((i, j, k))
#                     indexLocation = imageT1.TransformPhysicalPointToIndex(physicalLocation)
#                     avgNormal = sumNormal / normalCount
#                     avgLesion = sumLesion / lesionCount
#                     pixelDifference = abs(avgLesion - avgNormal)
#                     #print(np.int16(round(pixelDifference)))
#                     n = np.int(round(pixelDifference))
#                     #imageT1.SetPixelAsFloat(indexLocation[0], indexLocation[1], indexLocation[2], pixelDifference)
#                     imageT1[indexLocation[0], indexLocation[1], indexLocation[2]] = n
                    
                    

sitk.WriteImage(imageT1, fileNameOutput)
print("WRITE - " + fileNameOutput)
print("FINISHED")