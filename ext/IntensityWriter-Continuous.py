# This program reads T1 data and corresponding consensus. The calculated intensity difference is burned back in T1 and saved as a new file.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes


#pending = 01039VITE_DATA, moel check negIndex (for windowSize 5)
rootPath = "D:\\OneDrive-MyDatasets\\OneDrive - ODMAIL\\Datasets\\ModifiedDataSet\\MS_SegmentationChallengeDataset\\"
listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA", "07040DORE_DATA", "07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]
#listOfSubjects = ["07040DORE_DATA", "07043SEME_DATA"]
modalities = ["T1", "T2", "3DFLAIR"]


for subjectString in listOfSubjects:
    for modality in modalities:

        #subjectString = "08037ROGU_DATA"
        fileNameT1 = rootPath + subjectString+"\\structural\\"+modality+".nii"
        fileNameMask = rootPath + subjectString+"\\lesionMask\\resampledConsensus"+modality+"Cropped.nii"
        fileNameOutput = rootPath + subjectString+"\\structural\\"+modality+"IntensityDifference.nii"

        # Read T1 data.
        readerT1 = sitk.ImageFileReader()
        readerT1.SetFileName(fileNameT1)
        readerT1.LoadPrivateTagsOn()
        readerT1.ReadImageInformation()
        readerT1.LoadPrivateTagsOn()
        imageT1 = sitk.ReadImage(fileNameT1)
        print(imageT1.GetPixelIDTypeAsString())
        if("unsigned" in imageT1.GetPixelIDTypeAsString()):
            print("CONVERSION DONE")
            castImageFilter = sitk.CastImageFilter()
            castImageFilter.SetOutputPixelType(sitk.sitkInt16)
            imageT1 = castImageFilter.Execute(imageT1)
        else:
            pass

        # Read Mask data.
        readerMask = sitk.ImageFileReader()
        readerMask.SetFileName(fileNameMask)
        readerMask.LoadPrivateTagsOn()
        readerMask.ReadImageInformation()
        imageMask = sitk.ReadImage(fileNameMask)

        l = readerT1.GetSize()[0]
        w = readerT1.GetSize()[1]
        h = readerT1.GetSize()[2]

        print(l, w, h)
        windowSize = 3
        padding = math.floor(windowSize/2)

        for i in range(padding,l-padding+1):
            print("COMPLETED:"+str(i)+"/"+str(l-padding+1)+" " + str(subjectString) + " " + str(modality))
            for j in range(padding,w-padding+1):
                for k in range(padding,h-padding+1):
                    if(imageMask.GetPixel(i, j, k)>0.01):
                        sumLesion = 0
                        lesionCount = 0
                        sumNormal = 0
                        normalCount = 0
                        for p in range(i-padding, i+padding+1):
                            for q in range(j-padding, j+padding+1):
                                for r in range(k-padding, k+padding+1):
                                    physicalLocation = imageMask.TransformIndexToPhysicalPoint((p, q, r))
                                    indexLocation = imageT1.TransformPhysicalPointToIndex(physicalLocation)
                                    if(imageMask.GetPixel(p, q, r) > 0.01):
                                        lesionCount = lesionCount + 1
                                        sumLesion = sumLesion + imageT1.GetPixel(indexLocation[0], indexLocation[1], indexLocation[2])
                                    else:
                                        normalCount = normalCount + 1
                                        #print(indexLocation[0], indexLocation[1], indexLocation[2])
                                        #print(type(imageT1.GetPixel(indexLocation[0], indexLocation[1], indexLocation[2])))
                                        #if(indexLocation[0] > -1 and indexLocation[1] > -1 and indexLocation[2] > -1):
                                        sumNormal = sumNormal + imageT1.GetPixel(indexLocation[0], indexLocation[1], indexLocation[2])
                        if(normalCount!=0 and lesionCount!=0): # Avoiding divide by zero error
                            physicalLocation = imageMask.TransformIndexToPhysicalPoint((i, j, k))
                            indexLocation = imageT1.TransformPhysicalPointToIndex(physicalLocation)
                            avgNormal = sumNormal / normalCount
                            avgLesion = sumLesion / lesionCount
                            pixelDifference = avgLesion - avgNormal
                            #print(np.int16(round(pixelDifference)))
                            n = np.int(round(pixelDifference))
                            #imageT1.SetPixelAsFloat(indexLocation[0], indexLocation[1], indexLocation[2], pixelDifference)

                            imageT1[indexLocation[0], indexLocation[1], indexLocation[2]] = n
                            
                            

        sitk.WriteImage(imageT1, fileNameOutput)
        print("WRITE - " + fileNameOutput)
        print("FINISHED")
        