import os
import vtk
import LesionUtils
import numpy as np
from nibabel import freesurfer
import json

class LesionMapper:
  def __init__(self):
      self.textActorLesionStatistics = vtk.vtkTextActor() # Left dual Text actor to show lesion properties
      self.textActorParcellation = vtk.vtkTextActor() # Right dual text actor for showing parcellation data
      self.textActorLesionImpact = vtk.vtkTextActor() # Left dual text actor for showing lesion impact.
      self.textActorLesionStatistics.UseBorderAlignOff() 
      self.textActorLesionStatistics.SetPosition(10,0)
      self.textActorLesionStatistics.GetTextProperty().SetFontFamily(4)
      self.textActorLesionStatistics.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
      self.textActorLesionStatistics.GetTextProperty().SetFontSize(14)
      self.textActorLesionStatistics.GetTextProperty().ShadowOn()
      self.textActorLesionStatistics.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )

      self.textActorParcellation.UseBorderAlignOff() 
      self.textActorParcellation.GetTextProperty().SetFontFamily(4)
      self.textActorParcellation.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
      self.textActorParcellation.GetTextProperty().SetFontSize(14)
      self.textActorParcellation.GetTextProperty().ShadowOn()
      self.textActorParcellation.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
      self.textActorParcellation.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
      self.textActorParcellation.SetPosition(0.01, 1)
      self.textActorParcellation.GetTextProperty().SetVerticalJustificationToTop()
      self.textActorLesionImpact.SetTextProperty(self.textActorParcellation.GetTextProperty())
      self.textActorLesionImpact.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
      self.textActorLesionImpact.SetPosition(0.01, 1)

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
    print(id(self.renDualRight))
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

    # Add text actors
    self.renDualLeft.AddActor2D(self.textActorLesionStatistics)
    self.renDualRight.AddActor2D(self.textActorParcellation)
    self.renDualLeft.AddActor2D(self.textActorLesionImpact)
    self.overlayDataMainLeftLesions = {"Lesion ID":"NA", "Voxel Count":"NA", "Centroid":"NA", "Elongation":"NA", "Lesion Perimeter":"NA", "Lesion Spherical Radius":"NA", "Lesion Spherical Perimeter":"NA", "Lesion Flatness":"NA", "Lesion Roundness":"NA"}
    self.overlayDataMainLeftLesionImpact = {"Lesion ID":"NA", "# Functions":"NA", "Affected Functions" : "NA"}
    self.overlayDataMainRightParcellationImpact = {"Selected Brain Region:":"NA", "Lesion Influence:":"NA", "Number of Lesions Influencing:":"NA", "Lesion IDs:" : "NA"}
    
    LesionUtils.setOverlayText(self.overlayDataMainLeftLesions, self.textActorLesionStatistics)
    LesionUtils.setOverlayText(self.overlayDataMainLeftLesionImpact, self.textActorLesionImpact)
    LesionUtils.setOverlayText(self.overlayDataMainRightParcellationImpact, self.textActorParcellation)

    self.interactionStyleLeft.overlayDataMainLeftLesions = self.overlayDataMainLeftLesions
    self.interactionStyleLeft.overlayDataMainLeftLesionImpact = self.overlayDataMainLeftLesionImpact
    self.interactionStyleLeft.overlayDataMainRightParcellationImpact = self.overlayDataMainRightParcellationImpact
    self.interactionStyleLeft.textActorLesionStatistics = self.textActorLesionStatistics
    self.interactionStyleLeft.textActorLesionImpact = self.textActorLesionImpact
    self.interactionStyleLeft.textActorParcellation = self.textActorParcellation

    self.interactionStyleRight.overlayDataMainLeftLesions = self.overlayDataMainLeftLesions
    self.interactionStyleRight.overlayDataMainLeftLesionImpact = self.overlayDataMainLeftLesionImpact
    self.interactionStyleRight.overlayDataMainRightParcellationImpact = self.overlayDataMainRightParcellationImpact
    self.interactionStyleRight.textActorLesionStatistics = self.textActorLesionStatistics
    self.interactionStyleRight.textActorLesionImpact = self.textActorLesionImpact
    self.interactionStyleRight.textActorParcellation = self.textActorParcellation

    self.interactionStyleLeft.labelsRh = self.labelsRh
    self.interactionStyleLeft.regionsRh = self.regionsRh
    self.interactionStyleLeft.metaRh = self.metaRh
    self.interactionStyleLeft.uniqueLabelsRh = self.uniqueLabelsRh
    self.interactionStyleLeft.areaRh = self.areaRh
    self.interactionStyleLeft.labelsLh = self.labelsLh
    self.interactionStyleLeft.regionsLh = self.regionsLh
    self.interactionStyleLeft.metaLh = self.metaLh
    self.interactionStyleLeft.uniqueLabelsLh = self.uniqueLabelsLh
    self.interactionStyleLeft.areaLh = self.areaLh
    self.interactionStyleLeft.polyDataRh = self.polyDataRh
    self.interactionStyleLeft.polyDataLh = self.polyDataLh

    self.interactionStyleRight.labelsRh = self.labelsRh
    self.interactionStyleRight.regionsRh = self.regionsRh
    self.interactionStyleRight.metaRh = self.metaRh
    self.interactionStyleRight.uniqueLabelsRh = self.uniqueLabelsRh
    self.interactionStyleRight.areaRh = self.areaRh
    self.interactionStyleRight.labelsLh = self.labelsLh
    self.interactionStyleRight.regionsLh = self.regionsLh
    self.interactionStyleRight.metaLh = self.metaLh
    self.interactionStyleRight.uniqueLabelsLh = self.uniqueLabelsLh
    self.interactionStyleRight.areaLh = self.areaLh
    self.interactionStyleRight.polyDataRh = self.polyDataRh
    self.interactionStyleRight.polyDataLh = self.polyDataLh

    self.interactionStyleLeft.lesionCentroids = self.lesionCentroids
    self.interactionStyleLeft.lesionNumberOfPixels = self.lesionNumberOfPixels
    self.interactionStyleLeft.lesionElongation = self.lesionElongation
    self.interactionStyleLeft.lesionPerimeter = self.lesionPerimeter
    self.interactionStyleLeft.lesionSphericalRadius = self.lesionSphericalRadius
    self.interactionStyleLeft.lesionSphericalPerimeter = self.lesionSphericalPerimeter
    self.interactionStyleLeft.lesionFlatness = self.lesionFlatness
    self.interactionStyleLeft.lesionRoundness = self.lesionRoundness

    self.interactionStyleRight.lesionCentroids = self.lesionCentroids
    self.interactionStyleRight.lesionNumberOfPixels = self.lesionNumberOfPixels
    self.interactionStyleRight.lesionElongation = self.lesionElongation
    self.interactionStyleRight.lesionPerimeter = self.lesionPerimeter
    self.interactionStyleRight.lesionSphericalRadius = self.lesionSphericalRadius
    self.interactionStyleRight.lesionSphericalPerimeter = self.lesionSphericalPerimeter
    self.interactionStyleRight.lesionFlatness = self.lesionFlatness
    self.interactionStyleRight.lesionRoundness = self.lesionRoundness
    # load precomputed lesion properties
    self.structureInfoLh = None
    with open(self.subjectFolder + "\\parcellationLh.json") as fp: 
        self.structureInfoLh = json.load(fp)
    #print(self.structureInfoLh.keys())
    self.parcellationsLhCount = len(self.structureInfoLh)
    self.structureInfoRh = None
    with open(self.subjectFolder + "\\parcellationRh.json") as fp: 
        self.structureInfoRh = json.load(fp)
    self.parcellationsRhCount = len(self.structureInfoRh)

    self.parcellationAffectedPercentageLh = []
    self.parcellationLesionInfluenceCountLh = []
    self.parcellationAssociatedLesionsLh = []
    # for jsonElementIndex in range(self.parcellationsLhCount):
    #     for p in self.structureInfoLh[str(jsonElementIndex)]:
    #         self.parcellationAffectedPercentageLh.append(p["PercentageAffected"])
    #         self.parcellationLesionInfluenceCountLh.append(p["LesionInfluenceCount"])
    #         self.parcellationAssociatedLesionsLh.append(p["AssociatedLesions"])

    for jsonElementIndex in list(self.structureInfoLh.keys()):
        for p in self.structureInfoLh[str(jsonElementIndex)]:
            self.parcellationAffectedPercentageLh.append(p["PercentageAffected"])
            self.parcellationLesionInfluenceCountLh.append(p["LesionInfluenceCount"])
            self.parcellationAssociatedLesionsLh.append(p["AssociatedLesions"])

    self.parcellationAffectedPercentageRh = []
    self.parcellationLesionInfluenceCountRh = []
    self.parcellationAssociatedLesionsRh = []
    # for jsonElementIndex in range(self.parcellationsRhCount):
    #     for p in self.structureInfoRh[str(jsonElementIndex)]:
    #         self.parcellationAffectedPercentageRh.append(p["PercentageAffected"])
    #         self.parcellationLesionInfluenceCountRh.append(p["LesionInfluenceCount"])
    #         self.parcellationAssociatedLesionsRh.append(p["AssociatedLesions"])
    for jsonElementIndex in list(self.structureInfoLh.keys()):
        for p in self.structureInfoRh[str(jsonElementIndex)]:
            self.parcellationAffectedPercentageRh.append(p["PercentageAffected"])
            self.parcellationLesionInfluenceCountRh.append(p["LesionInfluenceCount"])
            self.parcellationAssociatedLesionsRh.append(p["AssociatedLesions"])

    self.interactionStyleLeft.parcellationsLhCount = self.parcellationsLhCount
    self.interactionStyleLeft.parcellationAffectedPercentageLh = self.parcellationAffectedPercentageLh
    self.interactionStyleLeft.parcellationLesionInfluenceCountLh = self.parcellationLesionInfluenceCountLh
    self.interactionStyleLeft.parcellationAssociatedLesionsLh = self.parcellationAssociatedLesionsLh
    self.interactionStyleLeft.parcellationsRhCount = self.parcellationsRhCount
    self.interactionStyleLeft.parcellationAffectedPercentageRh = self.parcellationAffectedPercentageRh
    self.interactionStyleLeft.parcellationLesionInfluenceCountRh = self.parcellationLesionInfluenceCountRh
    self.interactionStyleLeft.parcellationAssociatedLesionsRh = self.parcellationAssociatedLesionsRh

    self.interactionStyleRight.parcellationsLhCount = self.parcellationsLhCount
    self.interactionStyleRight.parcellationAffectedPercentageLh = self.parcellationAffectedPercentageLh
    self.interactionStyleRight.parcellationLesionInfluenceCountLh = self.parcellationLesionInfluenceCountLh
    self.interactionStyleRight.parcellationAssociatedLesionsLh = self.parcellationAssociatedLesionsLh
    self.interactionStyleRight.parcellationsRhCount = self.parcellationsRhCount
    self.interactionStyleRight.parcellationAffectedPercentageRh = self.parcellationAffectedPercentageRh
    self.interactionStyleRight.parcellationLesionInfluenceCountRh = self.parcellationLesionInfluenceCountRh
    self.interactionStyleRight.parcellationAssociatedLesionsRh = self.parcellationAssociatedLesionsRh

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

    def computeLesionImpact(self, lesionId):
        indexToParcellationDict = {0:-1,1:1,2:2,3:3,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:13,13:14,14:15,15:16,16:17,17:18,18:19,19:20,20:21,21:22,22:23,23:24,24:25,25:26,26:27,27:28,28:29,29:30,30:31,31:32,32:33,33:34,34:35}
        impactString = []
        for parcellationIndex in range(self.parcellationsRhCount):
            if(lesionId in list(self.parcellationAssociatedLesionsRh[parcellationIndex].keys())):
                impactString.append("RH-" + str(self.regionsRh[self.uniqueLabelsRh.tolist().index(indexToParcellationDict[parcellationIndex])].decode('utf-8')))
        for parcellationIndex in range(self.parcellationsLhCount):
            if(lesionId in list(self.parcellationAssociatedLesionsLh[parcellationIndex].keys())):
                impactString.append("LH-" + str(self.regionsLh[self.uniqueLabelsLh.tolist().index(indexToParcellationDict[parcellationIndex])].decode('utf-8')))
        return impactString

    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkPropPicker()
        #picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        
        cellPicker = vtk.vtkCellPicker()
        cellPicker.SetTolerance(0.0005)
        cellPicker.Pick(clickPos[0], clickPos[1], 0, self.renderer)

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
                parcellationIndex = self.uniqueLabelsLh.tolist().index(self.labelsLh[cellPicker.GetPointId()])
                self.overlayDataMainRightParcellationImpact["Selected Brain Region:"] = str(self.regionsLh[self.uniqueLabelsLh.tolist().index(self.labelsLh[cellPicker.GetPointId()])].decode('utf-8'))
                self.overlayDataMainRightParcellationImpact["Lesion Influence:"] = str("{0:.2f}".format(self.parcellationAffectedPercentageLh[parcellationIndex])) + "%"
                self.overlayDataMainRightParcellationImpact["Number of Lesions Influencing:"] = self.parcellationLesionInfluenceCountLh[parcellationIndex]
                self.overlayDataMainRightParcellationImpact["Lesion IDs:"] = list(self.parcellationAssociatedLesionsLh[parcellationIndex].keys())
            if("rh" in str(itemType)):
                parcellationIndex = self.uniqueLabelsRh.tolist().index(self.labelsRh[cellPicker.GetPointId()])
                self.overlayDataMainRightParcellationImpact["Selected Brain Region:"] = str(self.regionsRh[self.uniqueLabelsRh.tolist().index(self.labelsRh[cellPicker.GetPointId()])].decode('utf-8'))
                self.overlayDataMainRightParcellationImpact["Lesion Influence:"] = str("{0:.2f}".format(self.parcellationAffectedPercentageRh[parcellationIndex])) + "%"
                self.overlayDataMainRightParcellationImpact["Number of Lesions Influencing:"] = self.parcellationLesionInfluenceCountRh[parcellationIndex]
                self.overlayDataMainRightParcellationImpact["Lesion IDs:"] = list(self.parcellationAssociatedLesionsRh[parcellationIndex].keys())
            if itemType==None: # Itemtype is None for lesions. They only have Ids.
                # Set overlay dictionary
                self.centerOfMass = self.lesionCentroids[int(lesionID)-1]
                self.overlayDataMainLeftLesions["Lesion ID"] = str(lesionID)
                self.overlayDataMainLeftLesions["Centroid"] = str("{0:.2f}".format(self.centerOfMass[0])) +", " +  str("{0:.2f}".format(self.centerOfMass[1])) + ", " + str("{0:.2f}".format(self.centerOfMass[2]))
                #self.overlayDataMainLeftLesions["Selection Type"] = str(itemType)
                self.overlayDataMainLeftLesions["Voxel Count"] = self.lesionNumberOfPixels[int(lesionID)-1]
                self.overlayDataMainLeftLesions["Elongation"] = "{0:.2f}".format(self.lesionElongation[int(lesionID)-1])
                self.overlayDataMainLeftLesions["Lesion Perimeter"] = "{0:.2f}".format(self.lesionPerimeter[int(lesionID)-1])
                self.overlayDataMainLeftLesions["Lesion Spherical Radius"] = "{0:.2f}".format(self.lesionSphericalRadius[int(lesionID)-1])
                self.overlayDataMainLeftLesions["Lesion Spherical Perimeter"] = "{0:.2f}".format(self.lesionSphericalPerimeter[int(lesionID)-1])
                self.overlayDataMainLeftLesions["Lesion Flatness"] = "{0:.2f}".format(self.lesionFlatness[int(lesionID)-1])
                self.overlayDataMainLeftLesions["Lesion Roundness"] = "{0:.2f}".format(self.lesionRoundness[int(lesionID)-1])
                self.overlayDataMainLeftLesionImpact["Lesion ID"] = str(lesionID)
                impactStringList = self.computeLesionImpact(lesionID)
                functionListString = "\n"
                for elemIndex in range(len(impactStringList)):
                    #if(elemIndex % 3 == 0):
                    #    functionListString = functionListString + "\n"
                    #else:
                    functionListString = functionListString + str(impactStringList[elemIndex]) + "\n"

                self.overlayDataMainLeftLesionImpact["Affected Functions"] = functionListString
                self.overlayDataMainLeftLesionImpact["# Functions"] = len(impactStringList)
                
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
                            numberOfPointsLh = actorItem.GetMapper().GetInput().GetNumberOfPoints()
                            for index in range(numberOfPointsLh):
                                if(index in self.lesionAffectedPointIdsLh[int(lesionID)-1]):
                                    vtk_colorsLh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                                else:
                                    vtk_colorsLh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
                            actorItem.GetMapper().GetInput().GetPointData().SetScalars(vtk_colorsLh)
                        if actorItem.GetProperty().GetInformation().Get(self.informationKey) in ["rh.pial", "rh.white"]:
                            numberOfPointsRh = actorItem.GetMapper().GetInput().GetNumberOfPoints()
                            for index in range(numberOfPointsRh):
                                if(index in self.lesionAffectedPointIdsRh[int(lesionID)-1]):
                                    vtk_colorsRh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                                else:
                                    vtk_colorsRh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
                            actorItem.GetMapper().GetInput().GetPointData().SetScalars(vtk_colorsRh)
                #self.NewPickedActor.GetProperty().SetRepresentationToWireframe()
                LesionUtils.setOverlayText(self.overlayDataMainLeftLesions, self.textActorLesionStatistics)
                LesionUtils.setOverlayText(self.overlayDataMainLeftLesionImpact, self.textActorLesionImpact)
            
            LesionUtils.setOverlayText(self.overlayDataMainRightParcellationImpact, self.textActorParcellation)
             
            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor
        
        self.OnLeftButtonDown()
        return