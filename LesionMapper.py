import os
import vtk
import numpy as np
from nibabel import freesurfer

class LesionMapper:
  def __init__(self):
      pass
  def leftCameraModifiedCallback(self,obj,event):
      self.iren_LesionMapDualRight.Render()
  def rightCameraModifiedCallback(self,obj,event):
      self.iren_LesionMapDualLeft.Render()
      
  def AddData(self):
    #print("Hello add")
    self.renDualRight.SetActiveCamera(self.renDualLeft.GetActiveCamera())
    self.interactionStyleLeft = LesionMappingInteraction()
    self.interactionStyleLeft.renderer = self.renDualLeft
    self.interactionStyleLeft.informationKey = self.informationKey
    self.interactionStyleLeft.informationKeyID = self.informationKeyID
    self.interactionStyleLeft.actors = self.actors
    self.interactionStyleLeft.lesionAffectedPointIdsLh = self.lesionAffectedPointIdsLh
    self.interactionStyleLeft.lesionAffectedPointIdsRh = self.lesionAffectedPointIdsRh
    #self.interactionStyleLeft.SetDefaultRenderer(self.renDualLeft)
    self.iren_LesionMapDualLeft.SetInteractorStyle(self.interactionStyleLeft)

    self.interactionStyleRight = LesionMappingInteraction()
    self.interactionStyleRight.renderer = self.renDualRight
    self.interactionStyleRight.informationKey = self.informationKey
    self.interactionStyleRight.informationKeyID = self.informationKeyID
    self.interactionStyleRight.actors = self.actors
    self.interactionStyleRight.lesionAffectedPointIdsLh = self.lesionAffectedPointIdsLh
    self.interactionStyleRight.lesionAffectedPointIdsRh = self.lesionAffectedPointIdsRh
    #self.interactionStyleRight.SetDefaultRenderer(self.renDualRight)
    self.iren_LesionMapDualRight.SetInteractorStyle(self.interactionStyleRight)
    #self.renDualLeft.GetActiveCamera().AddObserver("ModifiedEvent", self.cameraModifiedCallback)
    #self.renDualRight.GetActiveCamera().AddObserver("ModifiedEvent", self.cameraModifiedCallback)
    self.renDualLeft.AddObserver("EndEvent", self.leftCameraModifiedCallback)
    self.renDualRight.AddObserver("EndEvent", self.rightCameraModifiedCallback)
    #self.iren_LesionMapDualLeft.Start()
    #self.iren_LesionMapDualRight.Start()
    #self.iren_LesionMapDualLeft.Initialize()
    for actor in self.actors:
        itemType = actor.GetProperty().GetInformation().Get(self.informationKey)
        #lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationUniqueKey)
        if(itemType == None):
            self.renDualLeft.AddActor(actor)
        else:
            actor.GetProperty().SetOpacity(1)
            self.renDualRight.AddActor(actor)
    self.renDualLeft.ResetCamera()
    self.renDualRight.ResetCamera()
    self.renDualLeft.Render()
    self.renDualRight.Render()

  def ClearData(self):
    self.renDualLeft.RemoveAllViewProps()
    self.renDualRight.RemoveAllViewProps()

  def Refresh(self):
      self.renDualLeft.Render()
      self.renDualRight.Render()

class LesionMappingInteraction(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,parent=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()

    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        #picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        
        # get the new
        self.NewPickedActor = picker.GetActor()
        
        # If something was selected
        if self.NewPickedActor:
            # If we picked something before, reset its property
            if self.LastPickedActor:
                self.LastPickedActor.GetMapper().ScalarVisibilityOn()
                self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
    
            
            # Save the property of the picked actor so that we can
            # restore it next time
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
            itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationKey)
            lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationKeyID)

            if("lh" in str(itemType)):
                print("left hemisphere")
            if("rh" in str(itemType)):
                print("right hemisphere")
            if itemType==None: # Itemtype is None for lesions. They only have Ids.
                # Highlight the picked actor by changing its properties
                self.NewPickedActor.GetMapper().ScalarVisibilityOff()
                self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                self.NewPickedActor.GetProperty().SetDiffuse(1.0)
                self.NewPickedActor.GetProperty().SetSpecular(0.0)
                vtk_colorsLh = vtk.vtkUnsignedCharArray()
                vtk_colorsLh.SetNumberOfComponents(3)
                vtk_colorsRh = vtk.vtkUnsignedCharArray()
                vtk_colorsRh.SetNumberOfComponents(3)
                clrGreen = [70, 121, 85]
                clrRed = [255, 0, 0]
                for actorItem in self.actors:
                    if(actorItem.GetProperty().GetInformation().Get(self.informationKey) != None):
                        if actorItem.GetProperty().GetInformation().Get(self.informationKey) in ["lh.pial", "lh.white"]:
                            #pointDataArray = actorItem.GetMapper().GetInput().GetPointData().GetArray("MetaImage")
                            numberOfPointsLh = actorItem.GetMapper().GetInput().GetNumberOfPoints()
                            for index in range(numberOfPointsLh):
                                #print(self.lesionAffectedPointIdsLh)
                                if(index in self.lesionAffectedPointIdsLh[int(lesionID)-1]):
                                    vtk_colorsLh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                                else:
                                    vtk_colorsLh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
                            actorItem.GetMapper().GetInput().GetPointData().SetScalars(vtk_colorsLh)
                        if actorItem.GetProperty().GetInformation().Get(self.informationKey) in ["rh.pial", "rh.white"]:
                            #pointDataArray = actorItem.GetMapper().GetInput().GetPointData().GetArray("MetaImage")
                            numberOfPointsRh = actorItem.GetMapper().GetInput().GetNumberOfPoints()
                            for index in range(numberOfPointsRh):
                                if(index in self.lesionAffectedPointIdsRh[int(lesionID)-1]):
                                    vtk_colorsRh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                                else:
                                    vtk_colorsRh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
                            actorItem.GetMapper().GetInput().GetPointData().SetScalars(vtk_colorsRh)
                #self.NewPickedActor.GetProperty().SetRepresentationToWireframe()
            
            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor
        
        self.OnLeftButtonDown()
        return