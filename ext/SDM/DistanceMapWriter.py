import vtk
import numpy as np
import os
import LesionUtils
import json
import pickle

rootPath = "D:\\OneDrive - University of Bergen\Datasets\\MS_SegmentationChallengeDataset\\"
listOfSubjects = ["DTIDATA"]
#listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]
#listOfSubjects = ["01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]

def ComputeDistanceMapArray(surf1, surf2, hemString):
    distanceFilter = vtk.vtkDistancePolyDataFilter()
    distanceFilter.SetInputData(0, surf2.GetMapper().GetInput())
    distanceFilter.SetInputData(1, surf1.GetMapper().GetInput())
    distanceFilter.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(distanceFilter.GetOutputPort())
    
    mapper.SetScalarRange(distanceFilter.GetOutput().GetPointData().GetScalars().GetRange()[0], distanceFilter.GetOutput().GetPointData().GetScalars().GetRange()[1])
    #print("Range 0", distanceFilter.GetOutput().GetPointData().GetScalars().GetRange())
    
    #print("Range 0", distanceFilter.GetOutput().GetPointData().GetScalars().GetRange()[0])
    #print("Range 1", distanceFilter.GetOutput().GetPointData().GetScalars().GetRange()[1])
    #doubleArray = vtk.vtkDoubleArray()
    #doubleArray.DeepCopy(distanceFilter.GetOutput().GetPointData().GetScalars())
    test = distanceFilter.GetOutput().GetPointData().GetScalars()
    

    #writer = vtk.vtkPolyDataWriter()
    #writer.SetInputData(distanceFilter.GetOutput())
    #writer.SetFileName("D:\\sherin.vtk")
    #writer.Write()

    #print(test)
    #print(distanceFilter.GetOutput())
    #return doubleArray
    return test

for subject in listOfSubjects:
    structureInfo = None
    with open(rootPath + subject + "\\structure-def3.json") as fp: 
        structureInfo = json.load(fp)
    numberOfLesionElements = len(structureInfo)    
    print("Processing ", subject, "...")
    informationUniqueKey = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")
    lesionActors = LesionUtils.extractLesions2(rootPath + subject, informationUniqueKey)
    translationFilePath = rootPath + subject + "\\meta\\cras.txt"
    f = open(translationFilePath, "r")
    t_vector = []
    for t in f:
        t_vector.append(t)
    t_vector = list(map(float, t_vector))
    transform = vtk.vtkTransform()
    transform.PostMultiply()
    transform.Translate(t_vector[0], t_vector[1], t_vector[2])
    f.close()

    fileNameLh = rootPath + subject + "\\surfaces\\lh.white.obj"
    fileNameRh = rootPath + subject + "\\surfaces\\rh.white.obj"
    # Lh Surface Reader
    LhReader = vtk.vtkOBJReader()
    LhReader.SetFileName(fileNameLh)
    LhReader.Update()
    Lh_mapper = vtk.vtkOpenGLPolyDataMapper()
    Lh_mapper.SetInputConnection(LhReader.GetOutputPort())
    Lh_actor = vtk.vtkActor()
    Lh_actor.SetMapper(Lh_mapper)
    Lh_actor.SetUserTransform(transform)

    # Rh Surface Reader
    RhReader = vtk.vtkOBJReader()
    RhReader.SetFileName(fileNameRh)
    RhReader.Update()
    Rh_mapper = vtk.vtkOpenGLPolyDataMapper()
    Rh_mapper.SetInputConnection(RhReader.GetOutputPort())
    Rh_actor = vtk.vtkActor()
    Rh_actor.SetMapper(Rh_mapper)
    Rh_actor.SetUserTransform(transform)

    lh_polyData = LhReader.GetOutput()
    rh_polyData = RhReader.GetOutput()
    
    arrayIndex = 0

    for lesionActor in lesionActors:
        # Compute distance map and write arrays to files.
        distanceArrayLh = ComputeDistanceMapArray(lesionActor, Lh_actor, "Lh")
        distanceArrayLh.SetName("Distance" + str(arrayIndex))
        lh_polyData.GetPointData().AddArray(distanceArrayLh)

        distanceArrayRh = ComputeDistanceMapArray(lesionActor, Rh_actor, "Rh")
        distanceArrayRh.SetName("Distance" + str(arrayIndex))
        rh_polyData.GetPointData().AddArray(distanceArrayRh)

        arrayIndex = arrayIndex + 1


    # Write location for output.
    outputFolder = rootPath + subject + "\\surfaces\\ProjectionSDM\\"
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    outputFilePathLh = outputFolder + "mappingLh.vtk"
    outputFilePathRh = outputFolder + "mappingRh.vtk"

    writer = vtk.vtkPolyDataWriter()
    # sorry about this, but the files get REALLY big if we write them
    # in ASCII - I'll make this a gui option later.
    writer.SetFileTypeToBinary()
    writer.SetFileName(outputFilePathLh)
    writer.SetInputData(lh_polyData)
    writer.Write()

    writer.SetFileName(outputFilePathRh)
    writer.SetInputData(rh_polyData)
    writer.Write()
    print("COMPLETED PROCESSING SUBJECT", subject)

print("ALL SUBJECTS COMPLETED PROCESSING...")





