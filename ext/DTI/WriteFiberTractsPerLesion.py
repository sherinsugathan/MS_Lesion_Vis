# This program reads lesions and fiber tract data. The fiber tracts bundles are extracted per lesion and saved as separate files. 
import vtk
import numpy as np
import math
import json


def extractAffectedFibers(probeFilter):
    fiberCount =0
    polydata = probeFilter.GetOutput()
    #pointDataArray = probeFilter.GetOutput().GetPointData().GetArray("ImageScalars")
    #numberOfPointsInArray = pointDataArray.GetNumberOfValues()
    polydata_collection = []

    conn = vtk.vtkPolyDataConnectivityFilter()
    conn.SetInputData(polydata)
    conn.SetExtractionModeToAllRegions()
    conn.Update()
    nregions = conn.GetNumberOfExtractedRegions()
    conn.SetExtractionModeToSpecifiedRegions()
    print("NUMBER OF REGIONS IN PROBED DATA", nregions)
    conn.AddSpecifiedRegion(0)
    conn.Update()
    index = 0
    appendFilter = vtk.vtkAppendPolyData()

    for region in range(0,nregions):
        #print(index, "/", nregions)
        conn.InitializeSpecifiedRegionList()
        conn.AddSpecifiedRegion(region)
        conn.Update()

        cleanPolyData = vtk.vtkCleanPolyData()
        cleanPolyData.SetInputData(conn.GetOutput())
        cleanPolyData.Update()

        p = vtk.vtkPolyData()
        p.DeepCopy(cleanPolyData.GetOutput())
        polydata_collection.append(cleanPolyData.GetOutput())
        
        index=index+1
        pointDataArray = p.GetPointData().GetArray("ImageScalars")
        for index in range(p.GetNumberOfPoints()):
            if(pointDataArray.GetValue(index)>0):
                fiberCount = fiberCount +1
                appendFilter.AddInputData(cleanPolyData.GetOutput())
            #else:
                #foundBlack = 1
    if(fiberCount!=0):
        appendFilter.Update()
    return appendFilter, fiberCount


'''
##########################################################################
    Read lesion data and create actors.
    Returns: Lesion actors.
##########################################################################
'''
def extractLesions2(subjectFolder):
    lesionSurfaceDataFilePath = subjectFolder + "\\surfaces\\lesions.vtm"
    mbr = vtk.vtkXMLMultiBlockDataReader()
    mbr.SetFileName(lesionSurfaceDataFilePath)
    mbr.Update()

    lesionActors = []
    mb = mbr.GetOutput()
    # print("DATACOUNT" , mb.GetNumberOfBlocks())
    for i in range(mb.GetNumberOfBlocks()):
        polyData = vtk.vtkPolyData.SafeDownCast(mb.GetBlock(i))
        if polyData and polyData.GetNumberOfPoints():

            # smoothFilter = vtk.vtkSmoothPolyDataFilter()
            # smoothFilter.SetInputData(polyData)
            # smoothFilter.SetNumberOfIterations(5)
            # smoothFilter.SetRelaxationFactor(0.1)
            # smoothFilter.FeatureEdgeSmoothingOff()
            # smoothFilter.BoundarySmoothingOn()
            # smoothFilter.Update()

            # smoothFilter = vtk.vtkSmoothPolyDataFilter()
            # smoothFilter.SetInputData(polyData)
            # smoothFilter.SetNumberOfIterations(80)
            # smoothFilter.SetRelaxationFactor(0.1)
            # smoothFilter.FeatureEdgeSmoothingOn()
            # #smoothFilter.SetEdgeAngle(90)
            # smoothFilter.BoundarySmoothingOn()
            # smoothFilter.Update()

            smoother = vtk.vtkWindowedSincPolyDataFilter()
            #smoother.SetInputConnection(sphereSource->GetOutputPort())
            smoother.SetInputData(polyData)
            smoother.SetNumberOfIterations(7)
            smoother.BoundarySmoothingOff()
            smoother.FeatureEdgeSmoothingOff()
            smoother.SetFeatureAngle(120.0)
            smoother.SetPassBand(.001)
            smoother.NonManifoldSmoothingOn()
            smoother.NormalizeCoordinatesOn()
            smoother.Update()

            normalGenerator = vtk.vtkPolyDataNormals()
            normalGenerator.SetInputData(smoother.GetOutput())
            normalGenerator.ComputePointNormalsOn()
            normalGenerator.ComputeCellNormalsOff()
            normalGenerator.AutoOrientNormalsOn()
            normalGenerator.ConsistencyOn()
            normalGenerator.SplittingOff()
            normalGenerator.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputData(normalGenerator.GetOutput())
            #lesionMapper.SetInputData(polyData)
            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(lesionMapper)
            lesionActor.GetMapper().ScalarVisibilityOff()
            # informationID = vtk.vtkInformation()
            # informationID.Set(informationKeyID,str(i+1))
            # lesionActor.GetProperty().SetInformation(informationID)
            lesionActor.GetProperty().SetInterpolationToGouraud()
            #lesionActor.GetProperty().SetInterpolationToPhong()
            lesionActors.append(lesionActor)

    return lesionActors


rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\"
listOfSubjects = ["DTIDATA"]
crasFileName = rootFolder + "DTIDATA\\meta\\cras.txt"

# Read necessary cras transform.
f = open(crasFileName, "r")
t_vector = []
for t in f:
    t_vector.append(t)
t_vector = list(map(float, t_vector))
transform = vtk.vtkTransform()
transform.PostMultiply()
transform.Translate(t_vector[0], t_vector[1], t_vector[2])
f.close()



for subject in listOfSubjects:    
    subjectFolder = rootFolder + subject
    # Fetch extracted Lesion actors
    lesionActors = extractLesions2(subjectFolder)
    # Read fiber tract data
    fiberTractFileName = subjectFolder + "\\fibertracts\\mynewfiberdata10000.vtk"
    readerFiberTract = vtk.vtkPolyDataReader()
    readerFiberTract.SetFileName(fiberTractFileName)
    readerFiberTract.Update()

    # fibertract polydata
    polydata = readerFiberTract.GetOutput()

    # Mapper, Actor for fiber data
    mapperFiberTract = vtk.vtkOpenGLPolyDataMapper()
    mapperFiberTract.SetInputData(polydata)
    actorFiberTract = vtk.vtkActor()
    actorFiberTract.SetMapper(mapperFiberTract)

    # Writer for fiber bundles.
    mb = vtk.vtkMultiBlockDataSet()
    mb.SetNumberOfBlocks(len(lesionActors))
    bundleIndex = 0

    for lesionActor in lesionActors:
        spacing = [0] * 3  # desired volume spacing
        spacing[0] = 0.5
        spacing[1] = 0.5
        spacing[2] = 0.5
        bounds = [0]*6
        lesionActor.GetBounds(bounds)
        #print(bounds)
        lesionVolumeImage = vtk.vtkImageData()
        lesionVolumeImage.SetSpacing(spacing)
        sphereDims = [0]*3
        for i in range(3):
            sphereDims[i] = int(math.ceil((bounds[i * 2 + 1] - bounds[i * 2]) / spacing[i]))
        lesionVolumeImage.SetDimensions(sphereDims)
        lesionVolumeImage.SetExtent(0, sphereDims[0] - 1, 0, sphereDims[1] - 1, 0, sphereDims[2] - 1)
        streamOrigin = [0]*3
        streamOrigin[0] = bounds[0] + spacing[0] / 2
        streamOrigin[1] = bounds[2] + spacing[1] / 2
        streamOrigin[2] = bounds[4] + spacing[2] / 2
        lesionVolumeImage.SetOrigin(streamOrigin)
        lesionVolumeImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
        inVal = 255
        outVal = 0
        count = lesionVolumeImage.GetNumberOfPoints()
        for i in range(count):
            lesionVolumeImage.GetPointData().GetScalars().SetTuple1(i, inVal)
        pol2stencil = vtk.vtkPolyDataToImageStencil()   
        pol2stencil.SetInputData(lesionActor.GetMapper().GetInput())
        pol2stencil.SetOutputOrigin(streamOrigin)
        pol2stencil.SetOutputSpacing(spacing)
        pol2stencil.SetOutputWholeExtent(lesionVolumeImage.GetExtent())
        pol2stencil.Update()
        imgStencil = vtk.vtkImageStencil()
        imgStencil.SetInputData(lesionVolumeImage)
        imgStencil.SetStencilConnection(pol2stencil.GetOutputPort())
        imgStencil.ReverseStencilOff()
        imgStencil.SetBackgroundValue(outVal)
        imgStencil.Update()

        probeFilter = vtk.vtkProbeFilter()
        probeFilter.SetSourceConnection(imgStencil.GetOutputPort())
        probeFilter.SetInputData(polydata)
        probeFilter.Update()

        lesionFibers, fCount = extractAffectedFibers(probeFilter)
        print("FINAL FIBER COUNT", fCount)
        if(fCount==0):
            mb.SetBlock(bundleIndex, None)
            bundleIndex = bundleIndex + 1
            continue

        mb.SetBlock(bundleIndex, lesionFibers.GetOutput())
        bundleIndex = bundleIndex + 1
    
    writer = vtk.vtkXMLMultiBlockDataWriter()
    writer.SetFileName(subjectFolder + '\\surfaces\\streamlinesMultiBlockDatasetDTI.xml')
    writer.SetInputData(mb)
    writer.Write()
    print("Processed:", "BLOCKDATASET WRITE SUCCESS")