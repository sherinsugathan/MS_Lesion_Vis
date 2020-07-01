# This program reads connected component mask output along with T1 and T2. This is followed by computing intensity difference by considering the whole lesion.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json




rootPath = "D:\\OneDrive - University of Bergen\Datasets\\MS_SegmentationChallengeDataset\\"

listOfSubjects = ["DTIDATA"]
#listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]
modalityFileNames = ["T1.nii"]
#modalityFileNames = ["T1.nii", "T2.nii", "3DFLAIR.nii"]
for subjectName in listOfSubjects:
    jsonProcessedOnce = False
    for modality in modalityFileNames:
        subjectFolder = rootPath + subjectName
        connectedComponentsFilePath = subjectFolder + "\\lesionMask\\ConnectedComponents.nii"
        volumeFilePath = subjectFolder + "\\structural\\"+modality
        imageMask = sitk.ReadImage(connectedComponentsFilePath)
        imageVolumeData = sitk.ReadImage(volumeFilePath)

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

        #print("#### DIMS VOLUME", resampled_volume.GetWidth(), resampled_volume.GetHeight(), resampled_volume.GetDepth(), " #### DIMS MASK", imageMask.GetWidth(), imageMask.GetHeight(), imageMask.GetDepth())
        #print("ORIGIN VOLUME", resampled_volume.GetOrigin(), "ORIGIN MASK", imageMask.GetOrigin())
        #print("SPACING VOLUME", resampled_volume.GetSpacing(), "SPACING MASK", imageMask.GetSpacing())
        #print("PIXELTYPE VOLUME", resampled_volume.GetPixelIDTypeAsString(), "PIXELTYPE MASK", imageMask.GetPixelIDTypeAsString())

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
        if(jsonProcessedOnce == False):
            with open(subjectFolder + "\\structure-def.json") as fp: 
                structureInfo = json.load(fp)
                jsonProcessedOnce = True
        else:
            with open(subjectFolder + "\\structure-def2.json") as fp: 
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

            if(numberOfLesionVoxels <= 0):
                print("CRTICAL ERROR: NUMBER OF LESION VOXELS = 0 ")
                quit()

            sumOfNormalVoxels = np.sum(ndArrayNormalVolumeData)
            numberOfNormalVoxels = (ndArrayNormalMask>0).sum()
            averageNormalVoxelIntensity = sumOfNormalVoxels/numberOfNormalVoxels

            if(numberOfNormalVoxels <= 0):
                print("CRTICAL ERROR: NUMBER OF NORMAL VOXELS = 0 ")
                quit()

            print(subjectName, modality, "Average intensity lesion", jsonElementIndex , "/" , numberOfLesionElements, ":", averageLesionVoxelIntensity)
            print(subjectName, modality, "Average intensity normal", jsonElementIndex , "/" , numberOfLesionElements, ":", averageNormalVoxelIntensity)

            if(math.isnan(averageLesionVoxelIntensity)==True or math.isnan(averageNormalVoxelIntensity)==True):
                print("CRITICAL ERROR")
                quit()

            if("T1" in modality):
                for p in structureInfo[str(jsonElementIndex)]:
                    lesionDataDict = p
                    lesionDataDict['AverageLesionIntensity'] = averageLesionVoxelIntensity
                    lesionDataDict['AverageSurroundingIntensity'] = averageNormalVoxelIntensity
                    data[jsonElementIndex]=[]
                    data[jsonElementIndex].append(lesionDataDict) 
            if("T2" in modality):
                for p in structureInfo[str(jsonElementIndex)]:
                    lesionDataDict = p
                    lesionDataDict['AverageLesionIntensityT2'] = averageLesionVoxelIntensity
                    lesionDataDict['AverageSurroundingIntensityT2'] = averageNormalVoxelIntensity
                    data[jsonElementIndex]=[]
                    data[jsonElementIndex].append(lesionDataDict) 
            if("FLAIR" in modality):
                for p in structureInfo[str(jsonElementIndex)]:
                    lesionDataDict = p
                    lesionDataDict['AverageLesionIntensityFLAIR'] = averageLesionVoxelIntensity
                    lesionDataDict['AverageSurroundingIntensityFLAIR'] = averageNormalVoxelIntensity
                    data[jsonElementIndex]=[]
                    data[jsonElementIndex].append(lesionDataDict) 

        #sitk.WriteImage(resampled_volume, "D:\\temp\\newT1.nii")


        with open(subjectFolder + '\\structure-def2.json', 'w') as fp:
            json.dump(data, fp, indent=4)

print("FINISHED - SUCCESS")