# This program writes sorted parcellation impact quantification data to structure-def3 for very lesion.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json

rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\"
listOfSubjects = ["DTIDATA"]
applicableDataTypes = ["STRUCTURAL", "DTI", "DANIELSSON"]
#listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]

for subjectName in listOfSubjects:
    subjectFolder = rootPath + subjectName

    labelFileLh = subjectFolder + "\\surfaces\\lh.aparc.annot"
    labelFileRh = subjectFolder + "\\surfaces\\rh.aparc.annot"

    # Read freesurfer annotation data
    # Read annotation file Rh.
    labelsRh, ctabRh, regionsRh = freesurfer.read_annot(labelFileRh, orig_ids=False)
    metaRh = dict(
                    (index, {"region": item[0], "color": item[1][:4].tolist()})
                    for index, item in enumerate(zip(regionsRh, ctabRh)))

    # Read annotation file Lh.
    labelsLh, ctabLh, regionsLh = freesurfer.read_annot(labelFileLh, orig_ids=False)
    metaLh = dict(
                    (index, {"region": item[0], "color": item[1][:4].tolist()})
                    for index, item in enumerate(zip(regionsLh, ctabLh)))    

    # Read affected points from JSON file.
    data = {}
    structureInfo = None
    with open(subjectFolder + "\\structure-def3.json") as fp: 
        structureInfo = json.load(fp)
    numberOfLesionElements = len(structureInfo)

    for jsonElementIndex in (range(1,numberOfLesionElements+1)):
        for p in structureInfo[str(jsonElementIndex)]:
            lesionDataDict = p
            AffectedPointIdsLh = lesionDataDict['AffectedPointIdsLh']
            AffectedPointIdsRh = lesionDataDict['AffectedPointIdsRh']
            AffectedPointIdsLhDTI = lesionDataDict['AffectedPointIdsLhDTI']
            AffectedPointIdsRhDTI = lesionDataDict['AffectedPointIdsRhDTI']
            AffectedPointIdsLhDanielsson = lesionDataDict['AffectedPointIdsLhDanielsson']
            AffectedPointIdsRhDanielsson = lesionDataDict['AffectedPointIdsRhDanielsson']

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