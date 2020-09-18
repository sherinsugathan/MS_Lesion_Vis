# This program create holes in nodif_brain_mask using the synthetic lesion Consensus mask.
import vtk
import numpy as np
import os
import LesionUtils
import math
import SimpleITK as sitk

rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\DTIDATA\\"
rootPath = os.path.dirname(os.path.realpath(__file__))
nodifBrainMaskFile = rootPath + "\\dataFiles\\nodif_brain_mask.nii"

niftiReader = vtk.vtkNIFTIImageReader()
niftiReader.SetFileName(nodifBrainMaskFile)
niftiReader.Update()

readerBrainMask = sitk.ImageFileReader()
readerBrainMask.SetFileName(nodifBrainMaskFile)
readerBrainMask.LoadPrivateTagsOn()
readerBrainMask.ReadImageInformation()
readerBrainMask.LoadPrivateTagsOn()
imageBrainMask = sitk.ReadImage(nodifBrainMaskFile)


consensusLesionMaskFile = rootFolder + "lesionMask\\Consensus.nii"

readerLesionHoles = sitk.ImageFileReader()
readerLesionHoles.SetFileName(consensusLesionMaskFile)
readerLesionHoles.LoadPrivateTagsOn()
readerLesionHoles.ReadImageInformation()
readerLesionHoles.LoadPrivateTagsOn()
imageHoles = sitk.ReadImage(consensusLesionMaskFile)


#brainMaskArray = sitk.GetArrayFromImage(imageBrainMask)
lesionHolesArray = sitk.GetArrayFromImage(imageHoles)
print(lesionHolesArray.shape[0])
print(lesionHolesArray.shape[1])
print(lesionHolesArray.shape[2])

for i in range(lesionHolesArray.shape[0]):
     for j in range(lesionHolesArray.shape[1]):
          for k in range(lesionHolesArray.shape[2]):
               if(imageHoles[i,j,k]==1):
                    pt = imageHoles.TransformIndexToPhysicalPoint((i,j,k))
                    index = imageBrainMask.TransformPhysicalPointToIndex(pt)
                    imageBrainMask[index[0], index[1], index[2]] = 0 

sitk.WriteImage(imageBrainMask, "D:\\finalBrainMask2.nii")

print("done")
quit()












fileNameLh = rootFolder + "surfaces\\lh.white.obj"
fileNameRh = rootFolder + "surfaces\\rh.white.obj"
SDMFilePath = rootFolder + "surfaces\\ProjectionSDM\\"
LhMappingPolyData, RhMappingPolyData = readDistanceMapPolyData(SDMFilePath)
print(LhMappingPolyData)

translationFilePath = os.path.join(rootFolder, "meta\\cras.txt")
f = open(translationFilePath, "r")
t_vector = []
for t in f:
    t_vector.append(t)
t_vector = list(map(float, t_vector))
transform = vtk.vtkTransform()
transform.PostMultiply()
transform.Translate(t_vector[0], t_vector[1], t_vector[2])
f.close()

# Reader Lh inflated
LhReader = vtk.vtkOBJReader()
LhReader.SetFileName(fileNameLh)
LhReader.Update()
Lh_mapper = vtk.vtkOpenGLPolyDataMapper()
Lh_mapper.SetInputConnection(LhReader.GetOutputPort())
Lh_actor = vtk.vtkActor()
Lh_actor.SetMapper(Lh_mapper)
Lh_actor.SetUserTransform(transform)
Lh_actor.GetProperty().SetOpacity(0.5)
#Lh_actor.GetProperty().SetColor(203/255, 147/255, 121/255)

# Reader Rh inflated
RhReader = vtk.vtkOBJReader()
RhReader.SetFileName(fileNameRh)
RhReader.Update()
Rh_mapper = vtk.vtkOpenGLPolyDataMapper()
Rh_mapper.SetInputConnection(RhReader.GetOutputPort())
Rh_actor = vtk.vtkActor()
Rh_actor.SetMapper(Rh_mapper)
Rh_actor.SetUserTransform(transform)
Rh_actor.GetProperty().SetOpacity(0.5)
#Rh_actor.GetProperty().SetColor(0.0, 1.0, 0.0)

# Read lesions
informationUniqueKey = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")
lesionActors = LesionUtils.extractLesions2(rootFolder, informationUniqueKey)

# Display essentials
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# add the custom style
style = MouseInteractorHighLightActor()
style.lh = Lh_actor
style.rh = Rh_actor
style.mappingLh = LhMappingPolyData
style.mappingRh = RhMappingPolyData
style.informationKeyID = informationUniqueKey
style.initPickList(lesionActors)
style.SetDefaultRenderer(ren)
iren.SetInteractorStyle(style)

# Add the actors to the renderer, set the background and size
Rh_actor.GetMapper().ScalarVisibilityOn()
Lh_actor.GetMapper().ScalarVisibilityOn()
ren.AddActor(Rh_actor)
ren.AddActor(Lh_actor)

for actor in lesionActors:
	actor.GetMapper().ScalarVisibilityOff()
	actor.GetProperty().SetColor(0.0, 1.0, 0.0)
	ren.AddActor(actor)

ren.SetBackground(1, 229/255, 204/255)
ren.SetUseDepthPeeling(True)
ren.SetMaximumNumberOfPeels(6)
renWin.SetSize(800, 800)

# This allows the interactor to initalize itself. It has to be
# called before an event loop.
iren.Initialize()

# We'll zoom in a little by accessing the camera and invoking a "Zoom"
# method on it.
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1)
renWin.Render()

# Start the event loop.
iren.Start()





