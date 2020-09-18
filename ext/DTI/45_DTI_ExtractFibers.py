import SimpleITK as sitk
import vtk
import numpy as np
import sys, os


def SplitDisconectedParts(polydata):
    conn = vtk.vtkPolyDataConnectivityFilter()
    conn.SetInputData(polydata)
    conn.SetExtractionModeToAllRegions()
    conn.Update()
    nregions = conn.GetNumberOfExtractedRegions()
    conn.SetExtractionModeToSpecifiedRegions()
    conn.AddSpecifiedRegion(0)
    conn.Update()
 
    polydata_collection = []
    index = 0

    jump = int(nregions/10000)
    appendFilter = vtk.vtkAppendPolyData()

    for region in range(0,nregions,jump):
        print(index, "/", 10000)
        conn.InitializeSpecifiedRegionList()
        conn.AddSpecifiedRegion(region)
        conn.Update()

        cleanPolyData = vtk.vtkCleanPolyData()
        cleanPolyData.SetInputData(conn.GetOutput())
        cleanPolyData.Update()

        p = vtk.vtkPolyData()
        p.DeepCopy(cleanPolyData.GetOutput())
        #print("Number of points in split", p.GetNumberOfPoints())
        polydata_collection.append(cleanPolyData.GetOutput())

        appendFilter.AddInputData(cleanPolyData.GetOutput())
        index=index+1

    appendFilter.Update()
 
    return polydata_collection, appendFilter

def SelectLargestPart(polydata):
    conn = vtk.vtkPolyDataConnectivityFilter()
    conn.SetInputData(polydata)
    conn.SetExtractionModeToLargestRegion()
    conn.Update()
    result = vtk.vtkPolyData()
    result.DeepCopy(conn.GetOutput())
    print(conn.GetNumberOfExtractedRegions())
    conn.SetExtractionModeToSpecifiedRegions()
    return result

fileName = "C:\\Sherin\\OneDrive - University of Bergen\\1M.vtk"

reader = vtk.vtkPolyDataReader()
reader.SetFileName(fileName)
reader.Update()

polydata = reader.GetOutput()
print("Number of points in full fiber", polydata.GetNumberOfPoints())
#largestPolyData = SelectLargestPart(polydata)
polyFibers, newData = SplitDisconectedParts(polydata)
print("poly fiber count", len(polyFibers))
mapper = vtk.vtkOpenGLPolyDataMapper()
mapper.SetInputData(polyFibers[0])
#mapper.SetScalarRange(probeFilter.GetOutput().GetScalarRange())

# print("Number of points in fiber", largestPolyData.GetNumberOfPoints())
writer = vtk.vtkPolyDataWriter()
writer.SetInputData(newData.GetOutput())
writer.SetFileName('C:\\Sherin\\FiberDataHoles10000.vtk')
writer.Update()

actor = vtk.vtkActor()
actor.SetMapper(mapper)

ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
ren.AddActor(actor)
ren.SetBackground(0, 0, 0)
renWin.SetSize(500, 500)

# This allows the interactor to initalize itself. It has to be
# called before an event loop.
iren.Initialize()

# We'll zoom in a little by accessing the camera and invoking a "Zoom"
# method on it.
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1.5)
renWin.Render()

# Start the event loop.
iren.Start()