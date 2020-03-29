# This program reads removes -1 labelled surface and exports a surface with a hole which can be utilized for flattening the surface.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json
import cv2
from nibabel import freesurfer

listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]
hemisphere = ["rh", "lh"]
#labelFiles = [".aparc.annot"]# ".aparc.DKTatlas.annot"]
labelFiles = [".aparc.DKTatlas.annot"]
for subjectString in listOfSubjects:
        for hm in hemisphere:
                for labelF in labelFiles:
                        surfaceFile = "C:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\surfaces\\"+hm+".pial.obj"
                        labelFile = "C:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\surfaces\\"+hm+ labelF

                        #Load surface data.
                        surfaceReader = vtk.vtkOBJReader()
                        surfaceReader.SetFileName(surfaceFile)
                        surfaceReader.Update()
                        surface_mapper = vtk.vtkOpenGLPolyDataMapper()
                        surface_mapper.SetInputConnection(surfaceReader.GetOutputPort())
                        numberOfPoints = surface_mapper.GetInput().GetNumberOfPoints()
                        numberOfCells = surface_mapper.GetInput().GetNumberOfCells()
                        #print("Number of Points", numberOfPoints)
                        #print("Number of Cells", numberOfCells)


                        vtk_colors = vtk.vtkUnsignedCharArray()
                        vtk_colors.SetNumberOfComponents(3)

                        # Read annotation file.
                        labels, ctab, regions = freesurfer.read_annot(labelFile, orig_ids=False)
                        meta = dict(
                                        (index, {"region": item[0], "color": item[1][:4].tolist()})
                                        for index, item in enumerate(zip(regions, ctab)))

                        #print(type(list(labels)))

                        intLabelArray = vtk.vtkIntArray()
                        intLabelArray.SetName("FSLabels")

                        for index in range(numberOfPoints):
                            intLabelArray.InsertNextValue(labels[index])

                        surface_mapper.GetInput().GetPointData().SetScalars(intLabelArray)



                        #print(surface_mapper.GetInput())


                        cellLocator = vtk.vtkCellLocator()
                        cellLocator.SetDataSet(surface_mapper.GetInput())
                        cellLocator.BuildLocator()

                        ids = vtk.vtkIdTypeArray()
                        ids.SetNumberOfComponents(1)
                        count = 0
                        idsList = []
                        
                        for index in range(numberOfPoints):
                                if(labels[index] != -1):
                                        ids.InsertNextValue(index)
                                        idsList.append(index)
                                else:
                                        count = count + 1
                        idsListArray = np.array(idsList)
                        
                        polyData = surface_mapper.GetInput()
                        ptIds = vtk.vtkIdList()
                        idsCells = vtk.vtkIdTypeArray()
                        idsCells.SetNumberOfComponents(1)
                        # countin = 0
                        # countout = 1
                        for index in range(numberOfCells):
                                # print(str((index/numberOfCells)*100))
                                polyData.GetCellPoints(index, ptIds)
                                trianglePointArray = np.array([ptIds.GetId(0), ptIds.GetId(1), ptIds.GetId(2)])
                                diff = np.setdiff1d(trianglePointArray, idsListArray)
                                if(diff.size ==0):
                                        idsCells.InsertNextValue(index)
                                #         countin = countin +1
                                # else:
                                #         countout = countout +1
                                #print(ptIds.GetId(0), ptIds.GetId(1), ptIds.GetId(2))
                                        
                        # print(countin, countout)
                                        

                        # print("Skip count", count)


                        selectionNode = vtk.vtkSelectionNode()
                        selectionNode.SetFieldType(vtk.vtkSelectionNode.CELL)
                        selectionNode.SetContentType(vtk.vtkSelectionNode.INDICES)
                        selectionNode.SetSelectionList(idsCells)
                        #selectionNode.GetProperties().Set(vtk.vtkSelectionNode.CONTAINING_CELLS(),1)
                        selection = vtk.vtkSelection()
                        selection.AddNode(selectionNode)
                        extractSelection = vtk.vtkExtractSelection()
                        extractSelection.SetInputData(0,surface_mapper.GetInput())
                        extractSelection.SetInputData(1, selection)
                        extractSelection.Update()

                        selected = vtk.vtkUnstructuredGrid()
                        selected.ShallowCopy(extractSelection.GetOutput())
                        selectedMapper = vtk.vtkDataSetMapper()
                        selectedMapper.SetInputData(selected)
                        selectedActor = vtk.vtkActor()
                        selectedActor.SetMapper(selectedMapper)

                        geometryFilter = vtk.vtkGeometryFilter()
                        geometryFilter.SetInputData(extractSelection.GetOutput())
                        geometryFilter.Update()

                        print("Result count", geometryFilter.GetOutput().GetNumberOfPoints())

                        writeFileName = "C:\\Users\\Sherin\\Desktop\\MeshUnfold3\\"+subjectString+"_"+hm+labelF+".pial"
                        xmlPolyData = "C:\\Users\\Sherin\\Desktop\\MeshUnfold3\\"+subjectString+"_"+hm+labelF+"XMLPolyData.vtp"
                        #print(writeFileName)

                        # plyWriter = vtk.vtkPLYWriter()
                        # plyWriter.SetFileName(writeFileName + "ply")
                        # #plyWriter.SetInputData(extractSelection.GetOutput())
                        # plyWriter.SetInputData(geometryFilter.GetOutput())
                        # plyWriter.Write()

                        #print(geometryFilter.GetOutput())

                        arrayWriter = vtk.vtkXMLPolyDataWriter()
                        arrayWriter.SetInputData(geometryFilter.GetOutput())
                        arrayWriter.SetFileName(xmlPolyData)
                        arrayWriter.Write()


                        objWriter = vtk.vtkOBJWriter()
                        objWriter.SetInputData(geometryFilter.GetOutput())
                        objWriter.SetFileName(writeFileName + ".obj")
                        objWriter.Write()
                        print("DONE", writeFileName + ".obj")


# Display essentials
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
# Add the actors to the renderer, set the background and size
#ren.AddActor(actorLh)
ren.AddActor(selectedActor)
# for actor in lesionActors:
#ren.AddActor(lesionActors[23])

#ren.AddActor(lesionStreamActorRh)
#ren.AddActor(lesionStreamActorLh)

#ren.AddActor(streamerActor)
#ren.AddVolume(volume)
#ren.AddActor(actorStreamlines)
ren.SetBackground(0, 0, 0)
renWin.SetSize(800, 800)
iren.Initialize()
# We'll zoom in a little by accessing the camera and invoking a "Zoom"
# method on it.
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1)
renWin.Render()
# Start the event loop.
iren.Start()
