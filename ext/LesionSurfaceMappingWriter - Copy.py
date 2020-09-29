import vtk
import numpy as np
import math
import json

'''
##########################################################################
    Compute streamlines using temperature scalars.
    Returns: Nothing
##########################################################################
'''
def computeStreamlines(subjectFolder, lesionPointDataSet = None):
    temperatureDataFileName = subjectFolder + "\\heatMaps\\aseg.auto_temperature.nii"
    niftiReaderTemperature = vtk.vtkNIFTIImageReader()
    niftiReaderTemperature.SetFileName(temperatureDataFileName)
    niftiReaderTemperature.Update()
    cellDerivatives = vtk.vtkCellDerivatives()
    cellDerivatives.SetInputConnection(niftiReaderTemperature.GetOutputPort())
    cellDerivatives.Update()
    cellDataToPointData = vtk.vtkCellDataToPointData()
    cellDataToPointData.SetInputConnection(cellDerivatives.GetOutputPort())
    cellDataToPointData.Update()

    # Transform for temperature/gradient data
    QFormMatrixTemperature = niftiReaderTemperature.GetQFormMatrix()
    qFormListTemperature = [0] * 16 #the matrix is 4x4
    QFormMatrixTemperature.DeepCopy(qFormListTemperature, QFormMatrixTemperature)
    transformGradient = vtk.vtkTransform()
    transformGradient.PostMultiply()
    transformGradient.SetMatrix(qFormListTemperature)
    transformGradient.Update()
    
    # Create point source and actor
    # psource = vtk.vtkPointSource()
    # if(seedCenter!=None):
    #     psource.SetNumberOfPoints(500)
    #     psource.SetCenter(seedCenter)
    #     psource.SetRadius(seedRadius)
    # else:
    #     psource.SetNumberOfPoints(500)
    #     psource.SetCenter(127,80,150)
    #     psource.SetRadius(80)
    #pointSourceMapper = vtk.vtkPolyDataMapper()
    #pointSourceMapper.SetInputConnection(psource.GetOutputPort())
    #pointSourceActor = vtk.vtkActor()
    #pointSourceActor.SetMapper(pointSourceMapper)

    # if(seedCenter!=None):
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(cellDataToPointData.GetOutputPort())
    transformFilter.SetTransform(transformGradient)
    transformFilter.Update()

    # Perform stream tracing
    streamers = vtk.vtkStreamTracer()
    streamers.SetInputConnection(transformFilter.GetOutputPort())
    # if(seedCenter!=None):
    #     streamers.SetInputConnection(transformFilter.GetOutputPort())
    # else:
    #     streamers.SetInputConnection(cellDataToPointData.GetOutputPort())
    streamers.SetIntegrationDirectionToForward()
    streamers.SetComputeVorticity(False)
    #streamers.SetSourceConnection(psource.GetOutputPort())
    streamers.SetSourceData(lesionPointDataSet)
    
    # streamers.SetMaximumPropagation(100.0)
    # streamers.SetInitialIntegrationStep(0.05)
    # streamers.SetTerminalSpeed(.51)

    streamers.SetMaximumPropagation(100.0)
    streamers.SetInitialIntegrationStep(0.2)
    streamers.SetTerminalSpeed(.01)
    streamers.Update()
    tubes = vtk.vtkTubeFilter()
    tubes.SetInputConnection(streamers.GetOutputPort())
    tubes.SetRadius(0.5)
    tubes.SetNumberOfSides(3)
    tubes.CappingOn()
    tubes.SetVaryRadius(0)
    tubes.Update()
    # lut = vtk.vtkLookupTable()
    # lut.SetHueRange(.667, 0.0)
    # lut.Build()
    # streamerMapper = vtk.vtkPolyDataMapper()
    # streamerMapper.SetInputConnection(tubes.GetOutputPort())
    # streamerMapper.SetLookupTable(lut)
    # streamerActor = vtk.vtkActor()
    # streamerActor.SetMapper(streamerMapper)
    # # if(seedCenter!=None):
    # #     pass
    # # else:
    # #     streamerActor.SetUserTransform(transformGradient)
    # streamerMapper.Update()

    # writer = vtk.vtkXMLPolyDataWriter()
    # writer.SetFileName("D:\\streamlines.vtp")
    # writer.SetInputData(tubes.GetOutput())
    # writer.Write()

    # plyWriter = vtk.vtkPLYWriter()
    # plyWriter.SetFileName("D:\\streamlines.ply")
    # plyWriter.SetInputData(tubes.GetOutput())
    # plyWriter.Write()
    return tubes.GetOutput()


'''
##########################################################################
    Retrieve precomputed streamline bundles (for DTI datasets only)
    Returns: Nothing
##########################################################################
'''
def computeStreamlinesDTI(subjectFolder, lesionID):
    streamlineDataFilePath = subjectFolder + "\\surfaces\\streamlinesMultiBlockDatasetDTI.xml"
    reader = vtk.vtkXMLMultiBlockDataReader()
    reader.SetFileName(streamlineDataFilePath)
    reader.Update()

    mb = reader.GetOutput()
    #print("DATACOUNT" , mb.GetNumberOfBlocks())

    polyData = vtk.vtkPolyData.SafeDownCast(mb.GetBlock(lesionID))
    if polyData and polyData.GetNumberOfPoints():
        tubeFilter = vtk.vtkTubeFilter()
        tubeFilter.SetInputData(polyData)
        tubeFilter.SetRadius(0.5)
        tubeFilter.SetNumberOfSides(50)
        tubeFilter.Update()
        return tubeFilter.GetOutput()
    else:
        return None

'''
##########################################################################
    Extract lesions by processing labelled lesion mask data.
    Returns: Lesion actors.
##########################################################################
'''
def extractLesions(subjectFolder, labelCount):
    # Load lesion mask
    niftiReaderLesionMask = vtk.vtkNIFTIImageReader()
    niftiReaderLesionMask.SetFileName(subjectFolder + "\\lesionMask\\ConnectedComponents.nii")
    niftiReaderLesionMask.Update()

    # Read QForm matrix from mask data.
    QFormMatrixMask = niftiReaderLesionMask.GetQFormMatrix()
    qFormListMask = [0] * 16 #the matrix is 4x4
    QFormMatrixMask.DeepCopy(qFormListMask, QFormMatrixMask)

    lesionActors = []
    surface = vtk.vtkDiscreteMarchingCubes()
    surface.SetInputConnection(niftiReaderLesionMask.GetOutputPort())
    for i in range(labelCount):
        surface.SetValue(i,i+1)
    surface.Update()
    component = vtk.vtkPolyData()
    component.DeepCopy(surface.GetOutput())

    transform = vtk.vtkTransform()
    transform.Identity()
    transform.SetMatrix(qFormListMask)
    transform.Update()
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(surface.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    for i in range(labelCount):
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(transformFilter.GetOutput())
        threshold.ThresholdBetween(i+1,i+1)
        threshold.Update()

        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputData(threshold.GetOutput())
        geometryFilter.Update()

        lesionMapper = vtk.vtkOpenGLPolyDataMapper()
        lesionMapper.SetInputConnection(geometryFilter.GetOutputPort())
        lesionActor = vtk.vtkActor()
        lesionActor.SetMapper(lesionMapper)
        #information = vtk.vtkInformation()
        #information.Set(informationKey,"lesions")
        #lesionActor.GetProperty().SetInformation(information)
        #informationID = vtk.vtkInformation()
        #informationID.Set(informationKeyID,str(i+1))
        #lesionActor.GetProperty().SetInformation(informationID)
        lesionActors.append(lesionActor)

    return lesionActors

'''
##########################################################################
    Compute surface mapping and write to json file
    Returns: none.
##########################################################################
'''
def computeAndWriteMapping(jsonPath, dataType):
    # load precomputed lesion properties
    data = {}
    structureInfo = None
    with open(jsonPath) as fp: # read source json file.
        structureInfo = json.load(fp)
    numberOfLesionElements = len(structureInfo)

    lesionActors = extractLesions(subjectFolder, numberOfLesionElements)
    numberOfLesionActors = len(lesionActors)

    if(numberOfLesionElements!=numberOfLesionElements):
        print("LESION COUNT MISMATCH. PREMATURE TERMINATION!")

    #actorindex = 23
    for jsonElementIndex in (range(1,numberOfLesionElements+1)):
        # Compute streamlines.
        print("Processing:", subjectName, ",", str(jsonElementIndex), "/", str(numberOfLesionActors))
        streamLinePolyData = None
        if(dataType == "STRUCTURAL"):
            streamLinePolyData = computeStreamlines(subjectFolder, lesionActors[jsonElementIndex-1].GetMapper().GetInput())
        if(dataType == "DTI"):
            streamLinePolyData = computeStreamlinesDTI(subjectFolder, jsonElementIndex-1)

        streamerMapper = vtk.vtkPolyDataMapper()
        streamerMapper.SetInputData(streamLinePolyData)
        streamerActor = vtk.vtkActor()
        streamerActor.SetMapper(streamerMapper)
        #Load streamlines data
        #readerStreamlines = vtk.vtkXMLPolyDataReader()
        #readerStreamlines.SetFileName(streamlinesFile)
        #readerStreamlines.Update()

        #streamLinePolyData = readerStreamlines.GetOutput()
        spacing = [0] * 3  # desired volume spacing
        spacing[0] = 0.5
        spacing[1] = 0.5
        spacing[2] = 0.5
        bounds = [0]*6
        streamLinePolyData.GetBounds(bounds)
        #print(bounds)


        streamLineVolumeImage = vtk.vtkImageData()
        streamLineVolumeImage.SetSpacing(spacing)
        streamDims = [0]*3
        for i in range(3):
            streamDims[i] = int(math.ceil((bounds[i * 2 + 1] - bounds[i * 2]) / spacing[i]))
        streamLineVolumeImage.SetDimensions(streamDims)
        streamLineVolumeImage.SetExtent(0, streamDims[0] - 1, 0, streamDims[1] - 1, 0, streamDims[2] - 1)
        streamOrigin = [0]*3
        streamOrigin[0] = bounds[0] + spacing[0] / 2
        streamOrigin[1] = bounds[2] + spacing[1] / 2
        streamOrigin[2] = bounds[4] + spacing[2] / 2
        streamLineVolumeImage.SetOrigin(streamOrigin)
        streamLineVolumeImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

        inVal = 255
        outVal = 0
        count = streamLineVolumeImage.GetNumberOfPoints()
        for i in range(count):
            streamLineVolumeImage.GetPointData().GetScalars().SetTuple1(i, inVal)

        pol2stencil = vtk.vtkPolyDataToImageStencil()
        pol2stencil.SetInputData(streamLinePolyData)
        pol2stencil.SetOutputOrigin(streamOrigin)
        pol2stencil.SetOutputSpacing(spacing)
        pol2stencil.SetOutputWholeExtent(streamLineVolumeImage.GetExtent())
        pol2stencil.Update()

        imgStencil = vtk.vtkImageStencil()
        imgStencil.SetInputData(streamLineVolumeImage)
        imgStencil.SetStencilConnection(pol2stencil.GetOutputPort())
        imgStencil.ReverseStencilOff()
        imgStencil.SetBackgroundValue(outVal)
        imgStencil.Update()

        # writer = vtk.vtkMetaImageWriter()
        # writer.SetFileName("D:\\SphereVolume.mhd")
        # writer.SetInputData(imgStencil.GetOutput())
        # writer.Write()  

        # mapperStreamlines = vtk.vtkPolyDataMapper()
        # mapperStreamlines.SetInputConnection(readerStreamlines.GetOutputPort())
        # actorStreamlines = vtk.vtkActor()
        # actorStreamlines.SetMapper(mapperStreamlines)


        #myImageReader = vtk.vtkMetaImageReader()
        #myImageReader.SetFileName("D:\\SphereVolume.mhd")
        #myImageReader.Update()

        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(imgStencil.GetOutputPort())
        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        opacityTransferFunction = vtk.vtkPiecewiseFunction()
        opacityTransferFunction.AddPoint(0,0.0)
        opacityTransferFunction.AddPoint(255,1)
        volprop = vtk.vtkVolumeProperty()
        volprop.SetScalarOpacity(opacityTransferFunction)
        volume.SetProperty(volprop)
        print("Processing:", subjectName, ",", str(jsonElementIndex), "/", str(numberOfLesionActors), "VOLUME GENERATED")

        #Load surface data Lh
        surfaceReaderLh = vtk.vtkOBJReader()
        surfaceReaderLh.SetFileName(surfaceFileLh)
        surfaceReaderLh.Update()
        mapperLh = vtk.vtkOpenGLPolyDataMapper()
        mapperLh.SetInputConnection(surfaceReaderLh.GetOutputPort())
        actorLh = vtk.vtkActor()
        actorLh.SetMapper(mapperLh)

        #Load surface data Rh
        surfaceReaderRh = vtk.vtkOBJReader()
        surfaceReaderRh.SetFileName(surfaceFileRh)
        surfaceReaderRh.Update()
        mapperRh = vtk.vtkOpenGLPolyDataMapper()
        mapperRh.SetInputConnection(surfaceReaderRh.GetOutputPort())
        actorRh = vtk.vtkActor()
        actorRh.SetMapper(mapperRh)

        # Apply necessary transforms
        actorLh.SetUserTransform(transform)
        actorRh.SetUserTransform(transform)

        # Apply transformations to data Rh. This is needed in addition to previous step which applied only to display data/
        transformFilterRh = vtk.vtkTransformPolyDataFilter()
        transformFilterRh.SetInputData(surfaceReaderRh.GetOutput()) 
        transformFilterRh.SetTransform(transform)
        transformFilterRh.Update()
        # Apply transformations to data Lh. This is needed in addition to previous step which applied only to display data/
        transformFilterLh = vtk.vtkTransformPolyDataFilter()
        transformFilterLh.SetInputData(surfaceReaderLh.GetOutput()) 
        transformFilterLh.SetTransform(transform)
        transformFilterLh.Update()



        mapperRh.Update()
        mapperLh.Update()
        # Probe Filtering
        probeFilterRh = vtk.vtkProbeFilter()
        probeFilterRh.SetSourceConnection(imgStencil.GetOutputPort())
        probeFilterRh.SetInputData(transformFilterRh.GetOutput())
        probeFilterRh.Update()
        probeFilterLh = vtk.vtkProbeFilter()
        probeFilterLh.SetSourceConnection(imgStencil.GetOutputPort())
        probeFilterLh.SetInputData(transformFilterLh.GetOutput())
        probeFilterLh.Update()

        # probedSurfaceMapperRh = vtk.vtkPolyDataMapper()
        # probedSurfaceMapperRh.SetInputConnection(probeFilterRh.GetOutputPort())
        # probedSurfaceMapperRh.SetScalarRange(probeFilterRh.GetOutput().GetScalarRange())
        # probedSurfaceMapperRh.ScalarVisibilityOn()
        # lesionStreamActorRh = vtk.vtkActor()
        # lesionStreamActorRh.SetMapper(probedSurfaceMapperRh)
        # probedSurfaceMapperLh = vtk.vtkPolyDataMapper()
        # probedSurfaceMapperLh.SetInputConnection(probeFilterLh.GetOutputPort())
        # probedSurfaceMapperLh.SetScalarRange(probeFilterLh.GetOutput().GetScalarRange())
        # probedSurfaceMapperLh.ScalarVisibilityOn()
        # lesionStreamActorLh = vtk.vtkActor()
        # lesionStreamActorLh.SetMapper(probedSurfaceMapperLh)

        # Get color/point data array.
        #print(probeFilterLh.GetOutput().GetPointData())
        pointDataArrayRh = probeFilterRh.GetOutput().GetPointData().GetArray("ImageScalars")
        pointDataArrayLh = probeFilterLh.GetOutput().GetPointData().GetArray("ImageScalars")

        # Set Colors for vertices
        vtk_colorsRh = vtk.vtkUnsignedCharArray()
        vtk_colorsRh.SetNumberOfComponents(3)
        vtk_colorsLh = vtk.vtkUnsignedCharArray()
        vtk_colorsLh.SetNumberOfComponents(3)
        clrGreen = [0,255,0] # Red color representing pathology.
        clrRed = [255,0,0] # Green color representing normal areas
        numberOfPointsRh = mapperRh.GetInput().GetNumberOfPoints()
        numberOfPointsLh = mapperLh.GetInput().GetNumberOfPoints()

        mappingIndicesRh = []
        mappingIndicesLh = []
        #Assign colors based on thresholding probed values.
        for index in range(numberOfPointsLh):
            if(pointDataArrayLh.GetValue(index)>0):
                vtk_colorsLh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                mappingIndicesLh.append(index)
            else:
                vtk_colorsLh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
        for index in range(numberOfPointsRh):
            if(pointDataArrayRh.GetValue(index)>0):
                vtk_colorsRh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                mappingIndicesRh.append(index)
            else:
                vtk_colorsRh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
        print("Processing:", subjectName, ",", str(jsonElementIndex), "/", str(numberOfLesionActors), "PROBING COMPLETED")
        #print("Impact on Lh=", len(mappingIndicesLh))
        #print("Impact on Rh=", len(mappingIndicesRh))
        print("Processing:", subjectName, ",", str(jsonElementIndex), "/", str(numberOfLesionActors), "IMPACT_LH :", str(len(mappingIndicesLh)))
        print("Processing:", subjectName, ",", str(jsonElementIndex), "/", str(numberOfLesionActors), "IMPACT_RH :", str(len(mappingIndicesRh)))

        # Set Color Data as scalars on the point data.
        # probedSurfaceMapperRh.GetInput().GetPointData().SetScalars(vtk_colorsRh)
        # probedSurfaceMapperLh.GetInput().GetPointData().SetScalars(vtk_colorsLh)
        # probedSurfaceMapperRh.Update()
        # probedSurfaceMapperLh.Update()

        # Preparing JSON data
        for p in structureInfo[str(jsonElementIndex)]:
            lesionDataDict = p
            if(dataType == "STRUCTURAL"):
                lesionDataDict['AffectedPointIdsLh'] = mappingIndicesLh
                lesionDataDict['AffectedPointIdsRh'] = mappingIndicesRh
            if(dataType == "DTI"):
                lesionDataDict['AffectedPointIdsLhDTI'] = mappingIndicesLh
                lesionDataDict['AffectedPointIdsRhDTI'] = mappingIndicesRh
            data[jsonElementIndex]=[]
            data[jsonElementIndex].append(lesionDataDict) 

    with open(subjectFolder + '\\structure-def3.json', 'w') as fp:
        json.dump(data, fp, indent=4)
    print("Processed:", subjectName, "JSON File FLUSH: ", dataType)
    print("COMPLETED SUCCESSFULLY")

'''
##########################################################################
    MAIN SCRIPT
    Returns: Success :)
##########################################################################
'''
#listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]

listOfSubjects = ["DTIDATA"]
#dataType = "DTI"
#dataType = "STRUCTURAL"

rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\"
for subjectName in listOfSubjects:
    subjectFolder = rootPath + subjectName
    # Files
    #streamlinesFile = "D:\\streamlines.vtp"
    surfaceFileLh = rootPath + subjectName + "\\surfaces\\lh.white.obj"
    surfaceFileRh = rootPath + subjectName + "\\surfaces\\rh.white.obj"
    translationFilePath = rootPath + subjectName + "\\meta\\cras.txt"
    f = open(translationFilePath, "r")
    t_vector = []
    for t in f:
        t_vector.append(t)
    t_vector = list(map(float, t_vector))
    transform = vtk.vtkTransform()
    transform.PostMultiply()
    transform.Translate(t_vector[0], t_vector[1], t_vector[2])
    f.close()


    computeAndWriteMapping(subjectFolder + "\\structure-def2.json", "STRUCTURAL")
    computeAndWriteMapping(subjectFolder + "\\structure-def3.json", "DTI")




# Display essentials
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
# Add the actors to the renderer, set the background and size
#ren.AddActor(actorLh)
#ren.AddActor(actorRh)
# for actor in lesionActors:
#ren.AddActor(lesionActors[23])

#ren.AddActor(lesionStreamActorRh)
#ren.AddActor(lesionStreamActorLh)

#ren.AddActor(streamerActor)

#ren.AddVolume(volume)
#ren.AddActor(actorStreamlines)
ren.SetBackground(255, 0, 0)
renWin.SetSize(800, 800)
iren.Initialize()
# We'll zoom in a little by accessing the camera and invoking a "Zoom"
# method on it.
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1)
renWin.Render()
# Start the event loop.
iren.Start()
