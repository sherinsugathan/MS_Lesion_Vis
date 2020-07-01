import SimpleITK as sitk
import vtk
import numpy as np
import json
import sys
import argparse

subjectRootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\"
listOfSubjects = ["DTIDATA"]
#listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]

for subjectName in listOfSubjects:
    subjectFolder = subjectRootFolder + "\\" + subjectName

    # T1 structural data
    T1_fileName = subjectFolder + '\\structural\\T1.nii'
    imageT1 = sitk.ReadImage(T1_fileName)
    
    # Lesion Mask data
    # lesionMask_FileName = subjectFolder + "\\lesionMask\\ConsensusResampled cropped.nii" # Enable this for non-DTI datasets
    lesionMask_FileName = subjectFolder + "\\lesionMask\\Consensus.nii"
    imageLesionMask = sitk.ReadImage(lesionMask_FileName)

    if("integer" in imageLesionMask.GetPixelIDTypeAsString()):
        print("CONVERSION DONE")
        castImageFilter = sitk.CastImageFilter()
        castImageFilter.SetOutputPixelType(sitk.sitkFloat32)
        imageLesionMask = castImageFilter.Execute(imageLesionMask)

    # Binary threshold filter.
    binaryThresholdFilter = sitk.BinaryThresholdImageFilter()
    binaryThresholdFilter.SetOutsideValue(0)
    binaryThresholdFilter.SetInsideValue(1)
    binaryThresholdFilter.SetLowerThreshold(0.001)
    binaryThresholdFilter.SetUpperThreshold(200)
    binaryImage = binaryThresholdFilter.Execute(imageLesionMask)

    # Connected component filter.
    connectedComponentFilter = sitk.ConnectedComponentImageFilter()
    connectedComponentImage = connectedComponentFilter.Execute(binaryImage)
    objectCount = connectedComponentFilter.GetObjectCount()

    # store the connected components object (one label per voxel), label value will be referenced in structure-def.json as id
    writer = sitk.ImageFileWriter()
    writer.SetFileName(subjectFolder + "\\lesionMask\\ConnectedComponents.nii")
    writer.Execute(connectedComponentImage)

    # Label statistics filter.
    labelShapeStatisticsFilter = sitk.LabelShapeStatisticsImageFilter()
    labelShapeStatisticsFilter.Execute(connectedComponentImage)


    # extract individual values and store in central database (for this participant)
    data = {}
    for u in range(1,labelShapeStatisticsFilter.GetNumberOfLabels()+1):
        properties={}
        properties['Elongation'] = labelShapeStatisticsFilter.GetElongation(u)
        properties['NumberOfPixels'] = labelShapeStatisticsFilter.GetNumberOfPixels(u)
        properties['NumberOfPixelsOnBorder'] = labelShapeStatisticsFilter.GetNumberOfPixelsOnBorder(u)
        properties['Centroid'] = labelShapeStatisticsFilter.GetCentroid(u)
        properties['BoundingBox'] = labelShapeStatisticsFilter.GetBoundingBox(u)
        properties['EllipsoidDiameter'] = labelShapeStatisticsFilter.GetEquivalentEllipsoidDiameter(u)
        properties['SphericalPerimeter'] = labelShapeStatisticsFilter.GetEquivalentSphericalPerimeter(u)        
        properties['SphericalRadius'] = labelShapeStatisticsFilter.GetEquivalentSphericalRadius(u)
        properties['FeretDiameter'] = labelShapeStatisticsFilter.GetFeretDiameter(u)
        properties['Flatness'] = labelShapeStatisticsFilter.GetFlatness(u)
        properties['Perimeter'] = labelShapeStatisticsFilter.GetPerimeter(u)
        properties['PerimeterOnBorder'] = labelShapeStatisticsFilter.GetPerimeterOnBorder(u)
        properties['PerimeterOnBorderRatio'] = labelShapeStatisticsFilter.GetPerimeterOnBorderRatio(u)
        properties['PhysicalSize'] = labelShapeStatisticsFilter.GetPhysicalSize(u)
        properties['PrincipalAxes'] = labelShapeStatisticsFilter.GetPrincipalAxes(u)
        properties['PrincipalMoments'] = labelShapeStatisticsFilter.GetPrincipalMoments(u)
        properties['Region'] = labelShapeStatisticsFilter.GetRegion(u)
        properties['Roundness'] = labelShapeStatisticsFilter.GetRoundness(u)

        data[u]=[]
        data[u].append(properties)
        # store the id of the lesion as a numeric value
        # dataStructure[u] = {}
        # dataStructure[u]['Elongation'] = labelShapeStatisticsFilter.GetElongation(u)
        # dataStructure[u]['NumberOfPixels'] = labelShapeStatisticsFilter.GetNumberOfPixels(u)
        # dataStructure[u]['NumberOfPixelsOnBorder'] = labelShapeStatisticsFilter.GetNumberOfPixelsOnBorder(u)
        # dataStructure[u]['Centroid'] = labelShapeStatisticsFilter.GetCentroid(u)
        # dataStructure[u]['BoundingBox'] = labelShapeStatisticsFilter.GetBoundingBox(u)
        # dataStructure[u]['EllipsoidDiameter'] = labelShapeStatisticsFilter.GetEquivalentEllipsoidDiameter(u)
        # dataStructure[u]['SphericalPerimeter'] = labelShapeStatisticsFilter.GetEquivalentSphericalPerimeter(u)        
        # dataStructure[u]['SphericalRadius'] = labelShapeStatisticsFilter.GetEquivalentSphericalRadius(u)
        # dataStructure[u]['FeretDiameter'] = labelShapeStatisticsFilter.GetFeretDiameter(u)
        # dataStructure[u]['Flatness'] = labelShapeStatisticsFilter.GetFlatness(u)
        # dataStructure[u]['Perimeter'] = labelShapeStatisticsFilter.GetPerimeter(u)
        # dataStructure[u]['PerimeterOnBorder'] = labelShapeStatisticsFilter.GetPerimeterOnBorder(u)
        # dataStructure[u]['PerimeterOnBorderRatio'] = labelShapeStatisticsFilter.GetPerimeterOnBorderRatio(u)
        # dataStructure[u]['PhysicalSize'] = labelShapeStatisticsFilter.GetPhysicalSize(u)
        # dataStructure[u]['PrincipalAxes'] = labelShapeStatisticsFilter.GetPrincipalAxes(u)
        # dataStructure[u]['PrincipalMoments'] = labelShapeStatisticsFilter.GetPrincipalMoments(u)
        # dataStructure[u]['Region'] = labelShapeStatisticsFilter.GetRegion(u)
        # dataStructure[u]['Roundness'] = labelShapeStatisticsFilter.GetRoundness(u)

        # add all the others
    # now store the data structure for the program to use
    with open(subjectFolder + '\\structure-def.json', 'w') as fp:
        json.dump(data, fp, indent=4)
    print("Completed processing " + subjectName + "()"+ imageLesionMask.GetPixelIDTypeAsString() + ". " + str(objectCount) + " lesions found...")
print("Done 100%")