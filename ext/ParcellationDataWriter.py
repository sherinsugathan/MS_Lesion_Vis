# Write a JSON file that stores parcellation information.
import SimpleITK as sitk
import vtk
import numpy as np
import json
import sys
from nibabel import freesurfer

# mydict = {1: [2,5,6], 23: [8,5,9]}
# print(type(mydict[23]))
# print(mydict[23])
# quit()

subjectName = "01016SACH_DATA"
subjectFolder = "D:\\DATASET\\MS_SegmentationChallengeDataset\\" + subjectName
# Files
parcellationJSONFileNameLh = subjectFolder + "\\" + "parcellationLh.json"
parcellationJSONFileNameRh = subjectFolder + "\\" + "parcellationRh.json"
labelFileLh = subjectFolder + "\\surfaces\\lh.aparc.annot"
labelFileRh = subjectFolder + "\\surfaces\\rh.aparc.annot"

# load precomputed lesion properties
data = {}
structureInfo = None
with open(subjectFolder + "\\structure-def4.json") as fp: 
    structureInfo = json.load(fp)
numberOfLesionElements = len(structureInfo)

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

print("Label count Rh " + str(len(labelsRh)))
print("Label count Lh " + str(len(labelsLh)))

uniqueLabelsRh = np.unique(labelsRh)
print(uniqueLabelsRh)
uniqueLabelsLh = np.unique(labelsLh)
vertexIdsRh = np.arange(len(labelsRh))
vertexIdsLh = np.arange(len(labelsLh))

listOfSegmentedParcellationVerticesRh = []
for val in uniqueLabelsRh:
    vertices = vertexIdsRh[labelsRh == val]
    listOfSegmentedParcellationVerticesRh.append(vertices)

listOfSegmentedParcellationVerticesLh = []
for val in uniqueLabelsLh:
    vertices = vertexIdsLh[labelsLh == val]
    listOfSegmentedParcellationVerticesLh.append(vertices)

print("Parcellation list count Rh ", len(listOfSegmentedParcellationVerticesRh))
print("Parcellation list count Lh ", len(listOfSegmentedParcellationVerticesLh))


# Compute information for Rh hemisphere
data = {}
pElementArrayIndex = 0
for pElementIndex in uniqueLabelsRh: # for every parcellation
    #for pElementIndex in range(len(listOfSegmentedParcellationVerticesRh)): # for every parcellation
    lesionImpactData = {}
    for jsonElementIndex in (range(1,numberOfLesionElements+1)): # for every lesion
        for p in structureInfo[str(jsonElementIndex)]:
            impactRh = np.array(p["AffectedPointIdsRh"])
            #print("Type of impactRh", type(impactRh))
            #print("Type of parcellation verts", type(listOfSegmentedParcellationVerticesRh[pElementIndex]))
            #print("Length of impactRh", len(impactRh))
            #print("Length of parcellation verts", len(listOfSegmentedParcellationVerticesRh[pElementIndex]))
            if impactRh.size>0 and listOfSegmentedParcellationVerticesRh[pElementArrayIndex].size>0:
                intersectionList = np.intersect1d(impactRh, listOfSegmentedParcellationVerticesRh[pElementArrayIndex])
                if(intersectionList.size>0):
                    lesionImpactData[jsonElementIndex] = intersectionList.tolist()
                    #print("Intersection")
                #else:
                    #print("No intersection")
            #if(np.intersect1d(impactRh, ))
            #print(impactLh)
    #print(type(lesionImpactData))
    # Prepare data for writing.
    properties={}
    properties['AssociatedLesions'] = lesionImpactData
    properties['LesionInfluenceCount'] = len(lesionImpactData)
    affectedPoints = []
    for key in lesionImpactData: 
        affectedPoints.extend(lesionImpactData[key])
    uniqueAffectedPoints = np.unique(affectedPoints) 
    properties['PercentageAffected'] = (len(uniqueAffectedPoints)/listOfSegmentedParcellationVerticesRh[pElementArrayIndex].size)*100
    #properties['vertexIdsRh'] = 1
    #properties['NumberOfPixels'] = 2
    data[int(pElementIndex)]=[]
    data[int(pElementIndex)].append(properties)
    pElementArrayIndex = pElementArrayIndex + 1

# Write parcellation information for Rh hemisphere
with open(parcellationJSONFileNameRh, 'w') as fp:
    json.dump(data, fp, indent=4)



# Compute information for Lh hemisphere
data = {}
pElementArrayIndex = 0
for pElementIndex in uniqueLabelsLh: # for every parcellation
    #for pElementIndex in range(len(listOfSegmentedParcellationVerticesLh)): # for every parcellation
    lesionImpactData = {}
    for jsonElementIndex in (range(1,numberOfLesionElements+1)): # for every lesion
        for p in structureInfo[str(jsonElementIndex)]:
            impactLh = np.array(p["AffectedPointIdsLh"])
            #print("Type of impactRh", type(impactRh))
            #print("Type of parcellation verts", type(listOfSegmentedParcellationVerticesRh[pElementIndex]))
            #print("Length of impactRh", len(impactRh))
            #print("Length of parcellation verts", len(listOfSegmentedParcellationVerticesRh[pElementIndex]))
            if impactLh.size>0 and listOfSegmentedParcellationVerticesLh[pElementArrayIndex].size>0:
                intersectionList = np.intersect1d(impactLh, listOfSegmentedParcellationVerticesLh[pElementArrayIndex])
                if(intersectionList.size>0):
                    lesionImpactData[jsonElementIndex] = intersectionList.tolist()
                    #print("Intersection")
                #else:
                    #print("No intersection")
            #if(np.intersect1d(impactRh, ))
            #print(impactLh)
    #print(type(lesionImpactData))
    # Prepare data for writing.
    properties={}
    properties['AssociatedLesions'] = lesionImpactData
    properties['LesionInfluenceCount'] = len(lesionImpactData)
    affectedPoints = []
    for key in lesionImpactData: 
        affectedPoints.extend(lesionImpactData[key])
    uniqueAffectedPoints = np.unique(affectedPoints) 
    properties['PercentageAffected'] = (len(uniqueAffectedPoints)/listOfSegmentedParcellationVerticesLh[pElementArrayIndex].size)*100
    #properties['vertexIdsRh'] = 1
    #properties['NumberOfPixels'] = 2
    data[int(pElementIndex)]=[]
    data[int(pElementIndex)].append(properties)
    pElementArrayIndex = pElementArrayIndex + 1

# Write parcellation info files.
with open(parcellationJSONFileNameLh, 'w') as fp:
    json.dump(data, fp, indent=4)
print("PROCESSING COMPLETE: JSON WRITE SUCCESSFUL")