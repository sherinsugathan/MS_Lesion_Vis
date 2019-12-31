#Author: Sherin Sugathan
#Alg: MarchingCubes Writer.

import vtk
from vtk.util.colors import tomato


niftiReader = vtk.vtkNIFTIImageReader()
#niftiReader.SetFileName("C:\\T1.nii")
#niftiReader.SetFileName("C:\\test2train_bb2_hard_seg.nii")
niftiReader.SetFileName("D:\\DATASET\\MS_SegmentationChallengeDataset\\01016SACH_DATA\\lesionMask\\ConnectedComponents.nii") # Set your lesion binary mask here.
niftiReader.Update()

#loadFilePath = "C:\\SegmentedLesions.obj"
#reader = vtk.vtkOBJReader()
#reader.SetFileName(loadFilePath)
#reader.Update()

bounds = niftiReader.GetOutput().GetBounds()

#volume = vtk.vtkImageData()
#volume.DeepCopy(niftiReader.GetOutput())

surface = vtk.vtkDiscreteMarchingCubes()
#surface.SetInputData(volume)
surface.SetInputConnection(niftiReader.GetOutputPort())
surface.SetValue(0,1)
#surface.SetValue(1,2)
# surface.SetValue(2,3)
# surface.SetValue(3,4)
# surface.SetValue(4,5)
# surface.SetValue(5,6)
# surface.SetValue(6,7)
# surface.SetValue(7,8)
#contour.SetValue(0, 255)
surface.Update()


# writer = vtk.vtkXMLPolyDataWriter()
# writer.SetInputData(surface.GetOutput())
# writer.SetFileName("D:\\mask.vtp")
# writer.Write()

plyWriter = vtk.vtkPLYWriter()
plyWriter.SetFileName("D:\\DATASET\\MS_SegmentationChallengeDataset\\01016SACH_DATA\\lesionMask\\lesions.ply")
plyWriter.SetInputData(surface.GetOutput())
plyWriter.Write()

#objWriter = vtk.vtkOBJWriter()
#objWriter.SetInputData(surface.GetOutput())
#objWriter.SetFileName("D:\\DATASET\\MS_SegmentationChallengeDataset\\01016SACH_DONE\\lesionMask\\lesions.obj")
#objWriter.Write()

#surfaceFilter = vtk.vtkDataSetSurfaceFilter()
#surfaceFilter.SetInputConnection(reader.GetOutputPort())
#surfaceFilter.SetNonlinearSubdivisionLevel(2)
#surfaceFilter.Update()

#probeFilter = vtk.vtkProbeFilter()
#probeFilter.SetSourceConnection(niftiReader.GetOutputPort())
#probeFilter.SetInputData(reader.GetOutput())
#probeFilter.Update()

mapper = vtk.vtkOpenGLPolyDataMapper()
mapper.SetInputConnection(surface.GetOutputPort())
#mapper.SetScalarRange(probeFilter.GetOutput().GetScalarRange())

actor = vtk.vtkActor()
actor.SetMapper(mapper)



# Create the graphics structure. The renderer renders into the render
# window. The render window interactor captures mouse events and will
# perform appropriate camera or actor manipulation depending on the
# nature of the events.
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



print("Done success")
