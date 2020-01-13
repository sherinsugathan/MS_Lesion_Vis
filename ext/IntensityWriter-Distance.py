# This program reads connected component mask output along with T1 and T2. This is followed by computing intensity difference by considering the whole lesion.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json

subjectString = "08027SYBR_DATA"
fileNameQuantized = "D:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\heatMaps\\aseg.auto_temperature_quantized.nii"
subjectFolder = "D:\\DATASET\\MS_SegmentationChallengeDataset\\" + subjectString

# Read Quantized data.
readerQuantized = sitk.ImageFileReader()
readerQuantized.SetFileName(fileNameQuantized)
readerQuantized.LoadPrivateTagsOn()
readerQuantized.ReadImageInformation()
readerQuantized.LoadPrivateTagsOn()
imageQuantized = sitk.ReadImage(fileNameQuantized)

# Read centroids from JSON file.
data = {}
structureInfo = None
with open(subjectFolder + "\\structure-def2.json") as fp: 
    structureInfo = json.load(fp)
numberOfLesionElements = len(structureInfo)

for jsonElementIndex in (range(1,numberOfLesionElements+1)):
    for p in structureInfo[str(jsonElementIndex)]:
        lesionDataDict = p
        centroid = lesionDataDict['Centroid']
        indexLocation = imageQuantized.TransformPhysicalPointToIndex(centroid)
        regionNumber = imageQuantized.GetPixel(indexLocation[0], indexLocation[1], indexLocation[2])
        lesionDataDict['RegionNumberQuantized'] = regionNumber
        data[jsonElementIndex]=[]
        data[jsonElementIndex].append(lesionDataDict) 
    
    print("Finished processing lesion " + str(jsonElementIndex))

with open(subjectFolder + '\\structure-def3.json', 'w') as fp:
    json.dump(data, fp, indent=4)

#sitk.WriteImage(XoredImage, fileNameOutput)

print("FINISHED")