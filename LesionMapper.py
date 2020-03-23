import os
import vtk
import LesionUtils
import numpy as np
from nibabel import freesurfer
import json

class LesionMapper():
  def __init__(self, lesionvis):
      self.lesionvis = lesionvis
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
      self.lesionvis.iren_LesionMapDualRight.Render()
  def rightCameraModifiedCallback(self,obj,event):
      self.lesionvis.iren_LesionMapDualLeft.Render()
      
  def AddData(self):
    #print("Hello add")
    self.lesionvis.renDualRight.SetActiveCamera(self.lesionvis.renDualLeft.GetActiveCamera())
    self.interactionStyleLeft = LesionMappingInteraction(None, self.lesionvis, self)
    self.interactionStyleLeft.renderer = self.lesionvis.renDualLeft
    self.lesionvis.iren_LesionMapDualLeft.SetInteractorStyle(self.interactionStyleLeft)

    self.interactionStyleRight = LesionMappingInteraction(None, self.lesionvis, self)
    self.interactionStyleRight.renderer = self.lesionvis.renDualRight
    self.lesionvis.iren_LesionMapDualRight.SetInteractorStyle(self.interactionStyleRight)

    self.lesionvis.renDualLeft.AddObserver("EndEvent", self.leftCameraModifiedCallback)
    self.lesionvis.renDualRight.AddObserver("EndEvent", self.rightCameraModifiedCallback)

    for actor in self.lesionvis.actors:
        itemType = actor.GetProperty().GetInformation().Get(self.lesionvis.informationKey)
        if(itemType == None):
            self.lesionvis.renDualLeft.AddActor(actor)
        else:
            actor.GetProperty().SetOpacity(1)
            self.lesionvis.renDualRight.AddActor(actor)


    # Add text actors
    self.lesionvis.renDualLeft.AddActor2D(self.textActorLesionStatistics)
    self.lesionvis.renDualRight.AddActor2D(self.textActorParcellation)
    self.lesionvis.renDualLeft.AddActor2D(self.textActorLesionImpact)
    self.overlayDataMainLeftLesions = {"Lesion ID":"NA", "Voxel Count":"NA", "Centroid":"NA", "Elongation":"NA", "Lesion Perimeter":"NA", "Lesion Spherical Radius":"NA", "Lesion Spherical Perimeter":"NA", "Lesion Flatness":"NA", "Lesion Roundness":"NA"}
    self.overlayDataMainLeftLesionImpact = {"Lesion ID":"NA", "# Functions":"NA", "Affected Functions" : "NA"}
    self.overlayDataMainRightParcellationImpact = {"Selected Brain Region:":"NA", "Lesion Influence:":"NA", "Number of Lesions Influencing:":"NA", "Lesion IDs:" : "NA"}
    
    LesionUtils.setOverlayText(self.overlayDataMainLeftLesions, self.textActorLesionStatistics)
    LesionUtils.setOverlayText(self.overlayDataMainLeftLesionImpact, self.textActorLesionImpact)
    LesionUtils.setOverlayText(self.overlayDataMainRightParcellationImpact, self.textActorParcellation)

    # load precomputed lesion properties
    self.structureInfoLh = None
    with open(self.lesionvis.subjectFolder + "\\parcellationLh.json") as fp: 
        self.structureInfoLh = json.load(fp)
    self.parcellationsLhCount = len(self.structureInfoLh)
    self.structureInfoRh = None
    with open(self.lesionvis.subjectFolder + "\\parcellationRh.json") as fp: 
        self.structureInfoRh = json.load(fp)
    self.parcellationsRhCount = len(self.structureInfoRh)

    self.parcellationAffectedPercentageLh = []
    self.parcellationLesionInfluenceCountLh = []
    self.parcellationAssociatedLesionsLh = []

    for jsonElementIndex in list(self.structureInfoLh.keys()):
        for p in self.structureInfoLh[str(jsonElementIndex)]:
            self.parcellationAffectedPercentageLh.append(p["PercentageAffected"])
            self.parcellationLesionInfluenceCountLh.append(p["LesionInfluenceCount"])
            self.parcellationAssociatedLesionsLh.append(p["AssociatedLesions"])

    self.parcellationAffectedPercentageRh = []
    self.parcellationLesionInfluenceCountRh = []
    self.parcellationAssociatedLesionsRh = []

    for jsonElementIndex in list(self.structureInfoLh.keys()):
        for p in self.structureInfoRh[str(jsonElementIndex)]:
            self.parcellationAffectedPercentageRh.append(p["PercentageAffected"])
            self.parcellationLesionInfluenceCountRh.append(p["LesionInfluenceCount"])
            self.parcellationAssociatedLesionsRh.append(p["AssociatedLesions"])

    # Add legend data
    legend = vtk.vtkLegendBoxActor()
    legend.SetNumberOfEntries(2)
    #legend.LockBorderOn()
    legend.SetWidth(120)
    legend.SetHeight(120)
    colors = vtk.vtkNamedColors()

    overlayTextProperty = vtk.vtkTextProperty()
    overlayTextProperty.SetFontFamily(4)
    overlayTextProperty.SetFontFile("fonts\\RobotoMono-Medium.ttf")
    overlayTextProperty.SetFontSize(16)
    #overlayTextProperty.ShadowOn()
    #overlayTextProperty.SetColor( 0.3372, 0.7490, 0.4627 )
    #legendColor = []
    legend.SetEntryTextProperty(overlayTextProperty)

    legendBox = vtk.vtkCubeSource()
    legendBox.SetXLength(20)
    legendBox.SetYLength(20)
    legendBox.SetZLength(20)
    legendBox.Update()
    # #colors.GetColor("tomato", legendColor)
    # legend.SetEntry(0, legendBox.GetOutput(), "Normal Area", [173,221,142])
    # #colors.GetColor("banana", colors.GetColor3d("tomato"))
    # legend.SetEntry(1, legendBox.GetOutput(), "Influence Area", [222,45,38])

    legend.SetEntryString(0, "Normal Area")
    legend.SetEntryString(1, "Influence Area")
    legend.SetEntrySymbol(0, legendBox.GetOutput())
    legend.SetEntrySymbol(1, legendBox.GetOutput())
    legend.SetEntryColor(0, colors.GetColor3d("forestgreen"))
    legend.SetEntryColor(1, colors.GetColor3d("tomato"))
    legend.BoxOff()
    legend.BorderOff()


    # place legend in lower right
    legend.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    #legend.GetPositionCoordinate().SetCoordinateSystemToView()
    legend.GetPositionCoordinate().SetValue(0, 0)
    #legend.GetPositionCoordinate().SetValue(0.5, -1.0)

    legend.GetPosition2Coordinate().SetCoordinateSystemToNormalizedViewport()
    #legend.GetPosition2Coordinate().SetCoordinateSystemToView()
    legend.GetPosition2Coordinate().SetValue(0.25, 0.09)
    #legend.GetPosition2Coordinate().SetValue(1.0, -0.5)

    #legend.UseBackgroundOn()
    #egend.SetBackgroundColor(colors.GetColor3d("warm_grey"))

    self.lesionvis.renDualRight.AddActor(legend)

    self.lesionvis.renDualLeft.ResetCamera()
    self.lesionvis.renDualRight.ResetCamera()
    self.lesionvis.renDualLeft.Render()
    self.lesionvis.renDualRight.Render()

  def ClearData(self):
    self.lesionvis.renDualLeft.RemoveAllViewProps()
    self.lesionvis.renDualRight.RemoveAllViewProps()

  def Refresh(self):
      self.lesionvis.renDualLeft.Render()
      self.lesionvis.renDualRight.Render()

class LesionMappingInteraction(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,parent = None, lesionvis = None, lesionMapper = None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
        self.lesionvis = lesionvis
        self.lesionMapper = lesionMapper
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()

    def computeLesionImpact(self, lesionId):
        indexToParcellationDict = {0:-1,1:1,2:2,3:3,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:13,13:14,14:15,15:16,16:17,17:18,18:19,19:20,20:21,21:22,22:23,23:24,24:25,25:26,26:27,27:28,28:29,29:30,30:31,31:32,32:33,33:34,34:35}
        impactString = []
        for parcellationIndex in range(self.lesionMapper.parcellationsRhCount):
            if(lesionId in list(self.lesionMapper.parcellationAssociatedLesionsRh[parcellationIndex].keys())):
                impactString.append("RH-" + str(self.lesionvis.regionsRh[self.lesionvis.uniqueLabelsRh.tolist().index(indexToParcellationDict[parcellationIndex])].decode('utf-8')))
        for parcellationIndex in range(self.lesionMapper.parcellationsLhCount):
            if(lesionId in list(self.lesionMapper.parcellationAssociatedLesionsLh[parcellationIndex].keys())):
                impactString.append("LH-" + str(self.lesionvis.regionsLh[self.lesionvis.uniqueLabelsLh.tolist().index(indexToParcellationDict[parcellationIndex])].decode('utf-8')))
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
            itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.informationKey)
            lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.informationUniqueKey)

            if("lh" in str(itemType)):
                parcellationIndex = self.lesionvis.uniqueLabelsLh.tolist().index(self.lesionvis.labelsLh[cellPicker.GetPointId()])
                self.lesionMapper.overlayDataMainRightParcellationImpact["Selected Brain Region:"] = str(self.lesionvis.regionsLh[self.lesionvis.uniqueLabelsLh.tolist().index(self.lesionvis.labelsLh[cellPicker.GetPointId()])].decode('utf-8'))
                self.lesionMapper.overlayDataMainRightParcellationImpact["Lesion Influence:"] = str("{0:.2f}".format(self.lesionMapper.parcellationAffectedPercentageLh[parcellationIndex])) + "%"
                self.lesionMapper.overlayDataMainRightParcellationImpact["Number of Lesions Influencing:"] = self.lesionMapper.parcellationLesionInfluenceCountLh[parcellationIndex]
                self.lesionMapper.overlayDataMainRightParcellationImpact["Lesion IDs:"] = list(self.lesionMapper.parcellationAssociatedLesionsLh[parcellationIndex].keys())
            if("rh" in str(itemType)):
                parcellationIndex = self.lesionvis.uniqueLabelsRh.tolist().index(self.lesionvis.labelsRh[cellPicker.GetPointId()])
                self.lesionMapper.overlayDataMainRightParcellationImpact["Selected Brain Region:"] = str(self.lesionvis.regionsRh[self.lesionvis.uniqueLabelsRh.tolist().index(self.lesionvis.labelsRh[cellPicker.GetPointId()])].decode('utf-8'))
                self.lesionMapper.overlayDataMainRightParcellationImpact["Lesion Influence:"] = str("{0:.2f}".format(self.lesionMapper.parcellationAffectedPercentageRh[parcellationIndex])) + "%"
                self.lesionMapper.overlayDataMainRightParcellationImpact["Number of Lesions Influencing:"] = self.lesionMapper.parcellationLesionInfluenceCountRh[parcellationIndex]
                self.lesionMapper.overlayDataMainRightParcellationImpact["Lesion IDs:"] = list(self.lesionMapper.parcellationAssociatedLesionsRh[parcellationIndex].keys())
            if itemType==None: # Itemtype is None for lesions. They only have Ids.
                # Set overlay dictionary
                self.centerOfMass = self.lesionvis.lesionCentroids[int(lesionID)-1]
                self.lesionMapper.overlayDataMainLeftLesions["Lesion ID"] = str(lesionID)
                self.lesionMapper.overlayDataMainLeftLesions["Centroid"] = str("{0:.2f}".format(self.centerOfMass[0])) +", " +  str("{0:.2f}".format(self.centerOfMass[1])) + ", " + str("{0:.2f}".format(self.centerOfMass[2]))
                self.lesionMapper.overlayDataMainLeftLesions["Voxel Count"] = self.lesionvis.lesionNumberOfPixels[int(lesionID)-1]
                self.lesionMapper.overlayDataMainLeftLesions["Elongation"] = "{0:.2f}".format(self.lesionvis.lesionElongation[int(lesionID)-1])
                self.lesionMapper.overlayDataMainLeftLesions["Lesion Perimeter"] = "{0:.2f}".format(self.lesionvis.lesionPerimeter[int(lesionID)-1])
                self.lesionMapper.overlayDataMainLeftLesions["Lesion Spherical Radius"] = "{0:.2f}".format(self.lesionvis.lesionSphericalRadius[int(lesionID)-1])
                self.lesionMapper.overlayDataMainLeftLesions["Lesion Spherical Perimeter"] = "{0:.2f}".format(self.lesionvis.lesionSphericalPerimeter[int(lesionID)-1])
                self.lesionMapper.overlayDataMainLeftLesions["Lesion Flatness"] = "{0:.2f}".format(self.lesionvis.lesionFlatness[int(lesionID)-1])
                self.lesionMapper.overlayDataMainLeftLesions["Lesion Roundness"] = "{0:.2f}".format(self.lesionvis.lesionRoundness[int(lesionID)-1])
                self.lesionMapper.overlayDataMainLeftLesionImpact["Lesion ID"] = str(lesionID)
                impactStringList = self.computeLesionImpact(lesionID)
                functionListString = "\n"
                for elemIndex in range(len(impactStringList)):
                    functionListString = functionListString + str(impactStringList[elemIndex]) + "\n"

                self.lesionMapper.overlayDataMainLeftLesionImpact["Affected Functions"] = functionListString
                self.lesionMapper.overlayDataMainLeftLesionImpact["# Functions"] = len(impactStringList)
                
                # Highlight the picked actor by changing its properties
                self.NewPickedActor.GetMapper().ScalarVisibilityOff()
                self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                self.NewPickedActor.GetProperty().SetDiffuse(1.0)
                self.NewPickedActor.GetProperty().SetSpecular(0.0)
                vtk_colorsLh = vtk.vtkUnsignedCharArray()
                vtk_colorsLh.SetNumberOfComponents(3)
                vtk_colorsRh = vtk.vtkUnsignedCharArray()
                vtk_colorsRh.SetNumberOfComponents(3)
                clrGreen = [173, 221, 142]
                clrRed = [222, 45, 38]
                for actorItem in self.lesionvis.actors:
                    if(actorItem.GetProperty().GetInformation().Get(self.lesionvis.informationKey) != None):
                        if actorItem.GetProperty().GetInformation().Get(self.lesionvis.informationKey) in ["lh.pial", "lh.white"]:
                            numberOfPointsLh = actorItem.GetMapper().GetInput().GetNumberOfPoints()
                            for index in range(numberOfPointsLh):
                                if(index in self.lesionvis.lesionAffectedPointIdsLh[int(lesionID)-1]):
                                    vtk_colorsLh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                                else:
                                    vtk_colorsLh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
                            actorItem.GetMapper().GetInput().GetPointData().SetScalars(vtk_colorsLh)
                        if actorItem.GetProperty().GetInformation().Get(self.lesionvis.informationKey) in ["rh.pial", "rh.white"]:
                            numberOfPointsRh = actorItem.GetMapper().GetInput().GetNumberOfPoints()
                            for index in range(numberOfPointsRh):
                                if(index in self.lesionvis.lesionAffectedPointIdsRh[int(lesionID)-1]):
                                    vtk_colorsRh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                                else:
                                    vtk_colorsRh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
                            actorItem.GetMapper().GetInput().GetPointData().SetScalars(vtk_colorsRh)
                #self.NewPickedActor.GetProperty().SetRepresentationToWireframe()
                LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainLeftLesions, self.lesionMapper.textActorLesionStatistics)
                LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainLeftLesionImpact, self.lesionMapper.textActorLesionImpact)
            
            LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainRightParcellationImpact, self.lesionMapper.textActorParcellation)
             
            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor
        
        self.OnLeftButtonDown()
        return