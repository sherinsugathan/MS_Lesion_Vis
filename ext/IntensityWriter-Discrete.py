# This program reads connected component mask output along with T1 and T2. This is followed by computing intensity difference by considering the whole lesion.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json


#subjectString = "07003SATH_DATA"
listOfSubjects = ["01040VANE_DATA"]
rootPath = "D:\\OneDrive-MyDatasets\\OneDrive - ODMAIL\\Datasets\\ModifiedDataSet\\MS_SegmentationChallengeDataset\\"
modalityFileNames = ["T1.nii", "T2.nii", "3DFLAIR.nii"]
    #fileNameT1 = "C:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\structural\\T1.nii"
    #fileNameT2 = "C:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\structural\\T2.nii"
    #fileNameConnectedComponentMask = "C:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\lesionMask\\ConnectedComponents.nii"
    #fileNameOutput = "D:\\ConnectedDilated.nii"
for subject in listOfSubjects:
    subjectFolder = rootPath + subject
    fileNameConnectedComponentMask = rootPath + subject + "\\lesionMask\\ConnectedComponents.nii"
    for modalityFileName in modalityFileNames:
        # Read T1 data.
        fileNameVolume = rootPath + subject + "\\structural\\" + modalityFileName
        imageT1 = sitk.ReadImage(fileNameVolume)

        # Read Connected comoponent labelled mask data.
        readerMask = sitk.ImageFileReader()
        readerMask.SetFileName(fileNameConnectedComponentMask)
        readerMask.LoadPrivateTagsOn()
        readerMask.ReadImageInformation()
        imageMask = sitk.ReadImage(fileNameConnectedComponentMask)

        print(imageT1.GetSize())
        print(imageMask.GetSize())
        quit()

        # Binary threshold filter for all lesions.
        binaryThresholdFilterAll = sitk.BinaryThresholdImageFilter()
        binaryThresholdFilterAll.SetOutsideValue(0)
        binaryThresholdFilterAll.SetInsideValue(1)
        binaryThresholdFilterAll.SetLowerThreshold(1)
        binaryThresholdFilterAll.SetUpperThreshold(276) # Set to high. must be higher than total number of lesions.
        binaryImageAll = binaryThresholdFilterAll.Execute(imageMask)

        # load precomputed lesion properties
        data = {}
        structureInfo = None
        with open(subjectFolder + "\\structure-def4.json") as fp: 
            structureInfo = json.load(fp)
        numberOfLesionElements = len(structureInfo)

        for jsonElementIndex in (range(1,numberOfLesionElements+1)):
            # Dilated all image
            dilateFilter = sitk.BinaryDilateImageFilter()
            dilateFilter.SetForegroundValue(jsonElementIndex)
            dilateFilter.SetKernelRadius(1)
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


            if("T1" in modalityFileName):
                for p in structureInfo[str(jsonElementIndex)]:
                    lesionDataDict = p
                    lesionDataDict['AverageLesionIntensity'] = averageLesion
                    lesionDataDict['AverageSurroundingIntensity'] = averageSurrounding
                    data[jsonElementIndex]=[]
                    data[jsonElementIndex].append(lesionDataDict) 
            if("T2" in modalityFileName):
                for p in structureInfo[str(jsonElementIndex)]:
                    lesionDataDict = p
                    lesionDataDict['AverageLesionIntensityT2'] = averageLesion
                    lesionDataDict['AverageSurroundingIntensityT2'] = averageSurrounding
                    data[jsonElementIndex]=[]
                    data[jsonElementIndex].append(lesionDataDict) 
            if("FLAIR" in modalityFileName):
                for p in structureInfo[str(jsonElementIndex)]:
                    lesionDataDict = p
                    lesionDataDict['AverageLesionIntensityFLAIR'] = averageLesion
                    lesionDataDict['AverageSurroundingIntensityFLAIR'] = averageSurrounding
                    data[jsonElementIndex]=[]
                    data[jsonElementIndex].append(lesionDataDict) 

            print(modalityFileName, "Finished processing lesion " + str(jsonElementIndex))  
            
        with open(subjectFolder + '\\structure-def4.json', 'w') as fp:
            json.dump(data, fp, indent=4)

        #sitk.WriteImage(XoredImage, fileNameOutput)

print("FINISHED - SUCCESS")