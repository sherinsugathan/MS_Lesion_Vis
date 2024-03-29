import os
import vtk
import LesionUtils
import numpy as np
from nibabel import freesurfer
import json
import copy
import operator

class LesionMapper():
  def __init__(self, lesionvis):
      self.lesionvis = lesionvis
      self.textActorLesionStatistics = vtk.vtkTextActor() # Left dual Text actor to show lesion properties
      self.textActorParcellation = vtk.vtkTextActor() # Right dual text actor for showing parcellation data
      self.textActorLesionImpact = vtk.vtkTextActor() # Left dual text actor for showing lesion impact.
      self.textActorLesionStatistics.UseBorderAlignOff() 
      self.textActorLesionStatistics.SetPosition(10,0)
      self.textActorLesionStatistics.GetTextProperty().SetFontFamily(4)
      self.textActorLesionStatistics.GetTextProperty().SetFontFile("asset\\GoogleSans-Medium.ttf")
      self.textActorLesionStatistics.GetTextProperty().SetFontSize(14)
      self.textActorLesionStatistics.GetTextProperty().ShadowOn()
      self.textActorLesionStatistics.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )

      self.textActorParcellation.UseBorderAlignOff() 
      self.textActorParcellation.GetTextProperty().SetFontFamily(4)
      self.textActorParcellation.GetTextProperty().SetFontFile("asset\\GoogleSans-Medium.ttf")
      self.textActorParcellation.GetTextProperty().SetFontSize(14)
      self.textActorParcellation.GetTextProperty().ShadowOn()
      self.textActorParcellation.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
      self.textActorParcellation.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
      self.textActorParcellation.SetPosition(0.01, 1)
      self.textActorParcellation.GetTextProperty().SetVerticalJustificationToTop()
      self.textActorLesionImpact.SetTextProperty(self.textActorParcellation.GetTextProperty())
      self.textActorLesionImpact.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
      self.textActorLesionImpact.SetPosition(0.01, 1)
      self.interactionStyleLeft = None
      self.interactionStyleRight = None

      # Ui Control handlers.
      self.lesionvis.horizontalSlider_TopNRegions.valueChanged.connect(self.on_sliderChangedTopNRegions)
      self.lesionvis.horizontalSlider_TopNLesions.valueChanged.connect(self.on_sliderChangedTopNLesions)
      #print("done1")

  def leftCameraModifiedCallback(self,obj,event):
      self.lesionvis.iren_LesionMapDualRight.Render()
  def rightCameraModifiedCallback(self,obj,event):
      self.lesionvis.iren_LesionMapDualLeft.Render()

  def on_sliderChangedTopNRegions(self):
    if(self.interactionStyleLeft.currentLesionID != None):
        sliderValue = self.lesionvis.horizontalSlider_TopNRegions.value()
        lhdata, rhdata = self.getTopNRegions(sliderValue, self.interactionStyleLeft.currentLesionID, self.parcellationLesionContributionSortedLh, self.parcellationLesionContributionSortedRh)
        self.lesionvis.label_TopNRegions.setText("Showing top " + str(sliderValue) +" influenced regions")
        self.interactionStyleLeft.mapLesionToSurface(self.interactionStyleLeft.currentLesionID, None, lhdata, rhdata)
        self.lesionvis.renDualRight.Render()

  def on_sliderChangedTopNLesions(self):
    if(self.interactionStyleRight.currentParcellationLabel != None):
        indexToParcellationDict = {0:-1,1:1,2:2,3:3,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:13,13:14,14:15,15:16,16:17,17:18,18:19,19:20,20:21,21:22,22:23,23:24,24:25,25:26,26:27,27:28,28:29,29:30,30:31,31:32,32:33,33:34,34:35}
        parcellationLabelToIndexValue = list(indexToParcellationDict.keys())[list(indexToParcellationDict.values()).index(self.interactionStyleRight.currentParcellationLabel[0])]
        #print(parcellationLabelToIndexValue)
        lesionIDs = []      
        if(self.interactionStyleRight.currentParcellationLabel[1] == "lh"):
            sortedListLh = self.parcellationLesionContributionSortedLh[int(parcellationLabelToIndexValue)]
            for elem in sortedListLh:
                lesionIDs.append(int(elem[0]))
            #print("LH", self.lesionMapper.parcellationLesionContributionSortedLh[int(parcellationLabelToIndexValue)])
        if(self.interactionStyleRight.currentParcellationLabel[1] == "rh"):
            sortedListRh = self.parcellationLesionContributionSortedRh[int(parcellationLabelToIndexValue)]
            for elem in sortedListRh:
                lesionIDs.append(int(elem[0]))

        sliderValue = self.lesionvis.horizontalSlider_TopNLesions.value()
        self.lesionvis.label_TopNLesions.setText("Showing top " + str(sliderValue) +" influenced lesions")
        topLesionsHighestToLowest = lesionIDs[::-1]
        topLesions = topLesionsHighestToLowest[:int(sliderValue)]
        

        for actor in self.lesionvis.lesionActors:
            lesionID = actor.GetProperty().GetInformation().Get(self.lesionvis.informationUniqueKey)

            if(self.lesionvis.pushButton_Discrete.isChecked() == True):
                actor.GetMapper().ScalarVisibilityOff()
            else:
                actor.GetMapper().ScalarVisibilityOn()

            if int(lesionID) in topLesions:
                actor.GetMapper().ScalarVisibilityOff()
                actor.GetProperty().SetColor(1.0, 1.0, 0.0)
                actor.GetProperty().SetDiffuse(1.0)
                actor.GetProperty().SetSpecular(0.0)

        self.lesionvis.renDualRight.Render()


  def loadParcellationData(self):
    # load precomputed lesion properties
    if(self.lesionvis.mappingType == "Heat Equation"):
        paracellationDataFileNameLh = self.lesionvis.subjectFolder + "\\parcellationLh.json"
        paracellationDataFileNameRh = self.lesionvis.subjectFolder + "\\parcellationRh.json"
    if(self.lesionvis.mappingType == "Diffusion"):
        paracellationDataFileNameLh = self.lesionvis.subjectFolder + "\\parcellationLhDTI.json"
        paracellationDataFileNameRh = self.lesionvis.subjectFolder + "\\parcellationRhDTI.json"
    if(self.lesionvis.mappingType == "Danielsson Distance"):
        paracellationDataFileNameLh = self.lesionvis.subjectFolder + "\\parcellationLhDanielsson.json"
        paracellationDataFileNameRh = self.lesionvis.subjectFolder + "\\parcellationRhDanielsson.json"

    self.structureInfoLh = None
    with open(paracellationDataFileNameLh) as fp: 
        self.structureInfoLh = json.load(fp)
    self.parcellationsLhCount = len(self.structureInfoLh)
    self.structureInfoRh = None
    with open(paracellationDataFileNameRh) as fp: 
        self.structureInfoRh = json.load(fp)
    self.parcellationsRhCount = len(self.structureInfoRh)

    self.parcellationAffectedPercentageLh = []
    self.parcellationLesionInfluenceCountLh = []
    self.parcellationAssociatedLesionsLh = []
    self.parcellationLesionContributionSortedLh = []

    for jsonElementIndex in list(self.structureInfoLh.keys()):
        for p in self.structureInfoLh[str(jsonElementIndex)]:
            self.parcellationAffectedPercentageLh.append(p["PercentageAffected"])
            self.parcellationLesionInfluenceCountLh.append(p["LesionInfluenceCount"])
            self.parcellationAssociatedLesionsLh.append(p["AssociatedLesions"])
            self.parcellationLesionContributionSortedLh.append(p["lesionContributionSorted"])

    self.parcellationAffectedPercentageRh = []
    self.parcellationLesionInfluenceCountRh = []
    self.parcellationAssociatedLesionsRh = []
    self.parcellationLesionContributionSortedRh = []

    for jsonElementIndex in list(self.structureInfoLh.keys()):
        for p in self.structureInfoRh[str(jsonElementIndex)]:
            self.parcellationAffectedPercentageRh.append(p["PercentageAffected"])
            self.parcellationLesionInfluenceCountRh.append(p["LesionInfluenceCount"])
            self.parcellationAssociatedLesionsRh.append(p["AssociatedLesions"])
            self.parcellationLesionContributionSortedRh.append(p["lesionContributionSorted"])

  def getTopNLesions(self, n, parcellationLabel, parcellationLesionContributionSortedLh, parcellationLesionContributionSortedRh, isLeftHemisphere):
      topLesionIds = []
      indexToParcellationDict = {0:-1,1:1,2:2,3:3,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:13,13:14,14:15,15:16,16:17,17:18,18:19,19:20,20:21,21:22,22:23,23:24,24:25,25:26,26:27,27:28,28:29,29:30,30:31,31:32,32:33,33:34,34:35}
      parcellationIndex = list(indexToParcellationDict.keys())[list(indexToParcellationDict.values()).index(parcellationLabel)]
      if(isLeftHemisphere):
          lesionsAndImpactCountOnParcellation = parcellationLesionContributionSortedLh[parcellationIndex]
      else:
          lesionsAndImpactCountOnParcellation = parcellationLesionContributionSortedRh[parcellationIndex]
          
      reversedList = lesionsAndImpactCountOnParcellation[::-1]
      topN = reversedList[:n]
      for item in topN:
          topLesionIds.append(int(item[0]))
      return topLesionIds

  def getTopNRegions(self, n, lesionID, parcellationLesionContributionSortedLh, parcellationLesionContributionSortedRh):
        # Convert from list of list to list of tuples.
        #[['6', 14], ['5', 16], ['3', 20], ['4', 32], ['8', 44], ['2', 61], ['7', 76], ['1', 159]]
        #[('6', 14), ('5', 16), ('3', 20), ('4', 32), ('8', 44), ('2', 61), ('7', 76), ('1', 159)]
        for elem in parcellationLesionContributionSortedLh:
            for i in range(len(elem)):
                elem[i] = tuple(elem[i])

        for elem in parcellationLesionContributionSortedRh:
            for i in range(len(elem)):
                elem[i] = tuple(elem[i])

        #print("LH DATA", parcellationLesionContributionSortedLh)
        #print("RH DATA", parcellationLesionContributionSortedRh)

        topParcellationLabelsLh = []
        topParcellationLabelsRh = []
        indexToParcellationDict = {0:-1,1:1,2:2,3:3,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:13,13:14,14:15,15:16,16:17,17:18,18:19,19:20,20:21,21:22,22:23,23:24,24:25,25:26,26:27,27:28,28:29,29:30,30:31,31:32,32:33,33:34,34:35}
        combinedList = []
        #print(parcellationLesionContributionSortedLh)
        for item in parcellationLesionContributionSortedLh:
            if(item): # list not empty
                for entry in item:
                    if(int(lesionID) == int(entry[0])):
                        combinedList.append(['l', '%d'%parcellationLesionContributionSortedLh.index(item),entry[1]])
  
        for item in parcellationLesionContributionSortedRh:
            if(item): # list not empty
                for entry in item:
                    if(int(lesionID) ==int(entry[0])):
                        combinedList.append(['r','%d'%parcellationLesionContributionSortedRh.index(item), entry[1]])
             
        combinedListsorted = sorted(combinedList, key=operator.itemgetter(2))
        finalList = combinedListsorted[::-1][:n]
  
  
        #compute parcellation labels
        for item in finalList:
            item[1] = indexToParcellationDict[int(item[1])]
            #print(item)
            if(item[0]=='l'):
                topParcellationLabelsLh.append(item[1])
            else:
                topParcellationLabelsRh.append(item[1])
          
        return topParcellationLabelsLh, topParcellationLabelsRh

  def ResetTextOverlay(self):
    self.overlayDataMainLeftLesions = {"Lesion ID":"NA", "Voxel Count":"NA", "Centroid":"NA", "Elongation":"NA", "Lesion Perimeter":"NA", "Lesion Spherical Radius":"NA", "Lesion Spherical Perimeter":"NA", "Lesion Flatness":"NA", "Lesion Roundness":"NA"}
    self.overlayDataMainLeftLesionImpact = {"Lesion ID":"NA", "# Functions":"NA", "Affected Functions" : "NA"}
    self.overlayDataMainRightParcellationImpact = {"SELECTED BRAIN REGION:":"NA", "LESION INFLUENCE ON SELECTED REGION:":"NA", "NUMBER OF INFLUENCING LESIONS:":"NA", "INFLUENCING LESION IDs:" : "NA"}
    LesionUtils.setOverlayText(self.overlayDataMainLeftLesions, self.textActorLesionStatistics)
    LesionUtils.setOverlayText(self.overlayDataMainLeftLesionImpact, self.textActorLesionImpact)
    LesionUtils.setOverlayText(self.overlayDataMainRightParcellationImpact, self.textActorParcellation)

  def AddData(self):
    self.lesionvis.renDualRight.SetActiveCamera(self.lesionvis.renDualLeft.GetActiveCamera())
    self.interactionStyleLeft = LesionMappingInteraction(None, self.lesionvis, self)
    self.interactionStyleLeft.renderer = self.lesionvis.renDualLeft
    self.lesionvis.iren_LesionMapDualLeft.SetInteractorStyle(self.interactionStyleLeft)

    self.interactionStyleRight = LesionMappingInteraction(None, self.lesionvis, self)
    self.interactionStyleRight.renderer = self.lesionvis.renDualRight
    self.lesionvis.iren_LesionMapDualRight.SetInteractorStyle(self.interactionStyleRight)
    # Sync cameras
    self.lesionvis.renDualLeft.AddObserver("StartEvent", self.leftCameraModifiedCallback)
    self.lesionvis.renDualRight.AddObserver("StartEvent", self.rightCameraModifiedCallback)

    for actor in self.lesionvis.actors: # Adding actors to left and right viewports.
        itemType = actor.GetProperty().GetInformation().Get(self.lesionvis.informationKey)
        if(itemType == None or itemType == "ventricleMesh"):
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
    self.overlayDataMainRightParcellationImpact = {"SELECTED BRAIN REGION:":"NA", "LESION INFLUENCE ON SELECTED REGION:":"NA", "NUMBER OF INFLUENCING LESIONS:":"NA", "INFLUENCING LESION IDs:" : "NA"}
    
    LesionUtils.setOverlayText(self.overlayDataMainLeftLesions, self.textActorLesionStatistics)
    LesionUtils.setOverlayText(self.overlayDataMainLeftLesionImpact, self.textActorLesionImpact)
    LesionUtils.setOverlayText(self.overlayDataMainRightParcellationImpact, self.textActorParcellation)

    # Load parcellation data from precomputed files.
    self.loadParcellationData()

    # Add legend data
    legend = vtk.vtkLegendBoxActor()
    legend.SetNumberOfEntries(1)
    overlayTextProperty = vtk.vtkTextProperty()
    overlayTextProperty.SetFontFamily(4)
    overlayTextProperty.SetFontFile("asset\\RobotoMono-Medium.ttf")
    overlayTextProperty.SetFontSize(16)
    legend.SetEntryTextProperty(overlayTextProperty)
    legendBox = vtk.vtkCubeSource()
    legendBox.Update()
    legend.SetEntryString(0, "LESION INFLUENCE AREA")
    legend.SetEntrySymbol(0, legendBox.GetOutput())
    legend.SetEntryColor(0, [227/255,74/255,51/255])
    legend.BoxOff()
    legend.BorderOff()
    # place legend in lower right
    legend.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    legend.GetPositionCoordinate().SetValue(0, 0)
    legend.GetPosition2Coordinate().SetCoordinateSystemToNormalizedViewport()
    legend.GetPosition2Coordinate().SetValue(0.33, 0.1)
    #legend.UseBackgroundOn()
    #egend.SetBackgroundColor(colors.GetColor3d("warm_grey"))

    self.lesionvis.renDualRight.AddActor(legend)
    self.lesionvis.legend.SetPosition(0.8, 0.01)
    self.lesionvis.legend.SetPosition2(0.2,0.1)
    self.lesionvis.renDualLeft.AddActor(self.lesionvis.legend)

    self.lesionvis.renDualLeft.ResetCamera()
    self.lesionvis.renDualRight.ResetCamera()
    
    self.lesionvis.renDualRight.Render()
    self.lesionvis.renDualLeft.Render()

  def ClearData(self):
    self.lesionvis.renDualLeft.RemoveAllViewProps()
    self.lesionvis.renDualRight.RemoveAllViewProps()

  def EnableStreamlines(self):
      if(self.interactionStyleLeft.currentActiveStreamlineActor!=None):
        self.lesionvis.renDualLeft.AddActor(self.interactionStyleLeft.currentActiveStreamlineActor)
        self.lesionvis.renDualLeft.Render()

  def ClearStreamlines(self):
      if(self.interactionStyleLeft.currentActiveStreamlineActor!=None):
        self.lesionvis.renDualLeft.RemoveActor(self.interactionStyleLeft.currentActiveStreamlineActor)
        self.lesionvis.renDualLeft.Render()

  def autoMapping(self, userPickedLesion, clickedLesionActor):
      if(clickedLesionActor == None):
          return
      self.interactionStyleLeft.mapLesionToSurface(userPickedLesion, clickedLesionActor)
      self.interactionStyleRight.mapLesionToSurface(userPickedLesion, clickedLesionActor)
      self.interactionStyleLeft.LastPickedActor = clickedLesionActor
      self.interactionStyleRight.LastPickedActor = clickedLesionActor

  def updateMappingDisplay(self):
      if(self.interactionStyleLeft.currentActiveStreamlineActor!=None):
          self.lesionvis.renDualLeft.RemoveActor(self.interactionStyleLeft.currentActiveStreamlineActor)
          if(self.lesionvis.streamActors!=None): # If Signed Distance Map
            streamlineActor = self.lesionvis.streamActors[int(self.interactionStyleLeft.currentLesionID)-1]
            self.lesionvis.renDualLeft.AddActor(streamlineActor)
            self.interactionStyleLeft.currentActiveStreamlineActor = streamlineActor
      if(self.interactionStyleLeft.LastPickedActor!=None):
          self.loadParcellationData() # Update parcellation data by reading precomputed files.
          self.interactionStyleLeft.mapLesionToSurface(self.interactionStyleLeft.currentLesionID, self.interactionStyleLeft.LastPickedActor)
          self.lesionvis.renDualLeft.Render()

  def Refresh(self):
      self.lesionvis.renDualLeft.Render()
      self.lesionvis.renDualRight.Render()

'''
##########################################################################
    Class for implementing custom interactor for dual mode
##########################################################################
'''
class LesionMappingInteraction(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,parent = None, lesionvis = None, lesionMapper = None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
        self.AddObserver("LeftButtonReleaseEvent",self.leftButtonReleaseEvent)
        self.AddObserver("MouseMoveEvent", self.mouseMoveEvent)

        self.lesionvis = lesionvis
        self.lesionMapper = lesionMapper
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.currentActiveStreamlineActor = None
        self.currentLesionID = None
        self.currentParcellationLabel = None
        self.clrRed = [227,74,51]
        self.isLesionMappingActivatedOnceAndInitialized = False
        self.lesionMapper.lesionMappingRh = np.array([])
        self.lesionMapper.lesionMappingLh = np.array([])

        self.vtk_colorsLh = vtk.vtkUnsignedCharArray()
        self.vtk_colorsRh = vtk.vtkUnsignedCharArray()
        self.vtk_colorsLh.SetNumberOfComponents(3)
        self.vtk_colorsLh.SetName("ColorsLh")
        self.vtk_colorsRh.SetNumberOfComponents(3)
        self.vtk_colorsRh.SetName("ColorsRh")
        self.vtk_colorsLh.SetNumberOfTuples(self.lesionvis.lhwhiteMapper.GetInput().GetNumberOfPoints())
        self.vtk_colorsRh.SetNumberOfTuples(self.lesionvis.rhwhiteMapper.GetInput().GetNumberOfPoints())

        self.vtk_colorsLh.DeepCopy(self.lesionvis.colorsLightLh)
        self.vtk_colorsRh.DeepCopy(self.lesionvis.colorsLightRh)

        self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferLh")
        self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferRh")
        self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetScalars(self.lesionvis.colorsLightRh)
        self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetScalars(self.lesionvis.colorsLightLh)

        self.MouseMotion = 0

    # def computeLesionImpact(self, lesionId):
    #     indexToParcellationDict = {0:-1,1:1,2:2,3:3,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:13,13:14,14:15,15:16,16:17,17:18,18:19,19:20,20:21,21:22,22:23,23:24,24:25,25:26,26:27,27:28,28:29,29:30,30:31,31:32,32:33,33:34,34:35}
    #     impactString = []
    #     impactParcellationLabelsRh = []
    #     impactParcellationLabelsLh = []
    #     print("PARCCOUNT", self.lesionMapper.parcellationsRhCount)
    #     for parcellationIndex in range(self.lesionMapper.parcellationsRhCount):
    #         if(lesionId in list(self.lesionMapper.parcellationAssociatedLesionsRh[parcellationIndex].keys())):
    #             uniqueLabelIndex = self.lesionvis.uniqueLabelsRh.tolist().index(indexToParcellationDict[parcellationIndex])
    #             impactParcellationLabelsRh.append(self.lesionvis.uniqueLabelsRh[uniqueLabelIndex])
    #             impactString.append("RH-" + str(self.lesionvis.regionsRh[self.lesionvis.uniqueLabelsRh.tolist().index(indexToParcellationDict[parcellationIndex])].decode('utf-8')))
    #     for parcellationIndex in range(self.lesionMapper.parcellationsLhCount):
    #         if(lesionId in list(self.lesionMapper.parcellationAssociatedLesionsLh[parcellationIndex].keys())):
    #             uniqueLabelIndex = self.lesionvis.uniqueLabelsLh.tolist().index(indexToParcellationDict[parcellationIndex])
    #             impactParcellationLabelsLh.append(self.lesionvis.uniqueLabelsLh[uniqueLabelIndex])
    #             impactString.append("LH-" + str(self.lesionvis.regionsLh[self.lesionvis.uniqueLabelsLh.tolist().index(indexToParcellationDict[parcellationIndex])].decode('utf-8')))
    #     return impactString, impactParcellationLabelsLh, impactParcellationLabelsRh

    def computeLesionImpact(self, lesionId, parcellationWhiteListLh = None, parcellationWhiteListRh = None):
        indexToParcellationDict = {0:-1,1:1,2:2,3:3,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:13,13:14,14:15,15:16,16:17,17:18,18:19,19:20,20:21,21:22,22:23,23:24,24:25,25:26,26:27,27:28,28:29,29:30,30:31,31:32,32:33,33:34,34:35}
        impactString = []
        impactParcellationLabelsRh = []
        impactParcellationLabelsLh = []
        for parcellationIndex in range(self.lesionMapper.parcellationsRhCount):
            if(lesionId in list(self.lesionMapper.parcellationAssociatedLesionsRh[parcellationIndex].keys())):
                uniqueLabelIndex = self.lesionvis.uniqueLabelsRh.tolist().index(indexToParcellationDict[parcellationIndex])
                if(parcellationWhiteListRh != None):
                    if(self.lesionvis.uniqueLabelsRh[uniqueLabelIndex] not in parcellationWhiteListRh):
                        continue
                impactParcellationLabelsRh.append(self.lesionvis.uniqueLabelsRh[uniqueLabelIndex])
                impactString.append("RH-" + str(self.lesionvis.regionsRh[self.lesionvis.uniqueLabelsRh.tolist().index(indexToParcellationDict[parcellationIndex])].decode('utf-8')))
        for parcellationIndex in range(self.lesionMapper.parcellationsLhCount):
            if(lesionId in list(self.lesionMapper.parcellationAssociatedLesionsLh[parcellationIndex].keys())):
                uniqueLabelIndex = self.lesionvis.uniqueLabelsLh.tolist().index(indexToParcellationDict[parcellationIndex])
                if(parcellationWhiteListLh != None):
                    if(self.lesionvis.uniqueLabelsLh[uniqueLabelIndex] not in parcellationWhiteListLh):
                        continue
                impactParcellationLabelsLh.append(self.lesionvis.uniqueLabelsLh[uniqueLabelIndex])
                impactString.append("LH-" + str(self.lesionvis.regionsLh[self.lesionvis.uniqueLabelsLh.tolist().index(indexToParcellationDict[parcellationIndex])].decode('utf-8')))
        return impactString, impactParcellationLabelsLh, impactParcellationLabelsRh

    def tintColor(self, clr, p=0.5):
        r = 255 - int(p * (255 - clr[0]))
        g = 255 - int(p * (255 - clr[1]))
        b = 255 - int(p * (255 - clr[2]))
        return [r,g,b]

    def mapLesionToSurface(self, lesionID, NewPickedActor = None, parcellationWhiteListLh = None, parcellationWhiteListRh = None):
        numberOfPointsRh = self.lesionvis.rhwhiteMapper.GetInput().GetNumberOfPoints()
        numberOfPointsLh = self.lesionvis.lhwhiteMapper.GetInput().GetNumberOfPoints()
        vertexIndexArrayRh = np.arange(numberOfPointsRh)
        vertexIndexArrayLh = np.arange(numberOfPointsLh)
        if(self.lesionvis.mappingType == "Heat Equation"):
            affectedRh = np.asarray(self.lesionvis.lesionAffectedPointIdsRh[int(lesionID)-1])
            affectedLh = np.asarray(self.lesionvis.lesionAffectedPointIdsLh[int(lesionID)-1])
        if(self.lesionvis.mappingType == "Diffusion"):
            affectedRh = np.asarray(self.lesionvis.lesionAffectedPointIdsRhDTI[int(lesionID)-1])
            affectedLh = np.asarray(self.lesionvis.lesionAffectedPointIdsLhDTI[int(lesionID)-1])
        if(self.lesionvis.mappingType == "Danielsson Distance"):
            affectedRh = np.asarray(self.lesionvis.lesionAffectedPointIdsRhDanielsson[int(lesionID)-1])
            affectedLh = np.asarray(self.lesionvis.lesionAffectedPointIdsLhDanielsson[int(lesionID)-1])
        self.lesionMapper.lesionMappingRh = np.isin(vertexIndexArrayRh, affectedRh)
        self.lesionMapper.lesionMappingLh = np.isin(vertexIndexArrayLh, affectedLh)

        # if(self.lesionMapper.lesionMappingLh.size > 0): # Can use lesionMappingRh also. This is to check if lesion mapping is done atleast once.
        #     self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsLh")
        #     self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsRh")
        #     print("MapLesionsToSurface-->ColorsLh")
        # else: # Use parcellation colors that has no red lesion impact patches
        #     self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferLh")
        #     self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferRh")
        #     print("MapLesionsToSurface-->ColorsFreeSurferLh")

        self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferLh")
        self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferRh")

        scalarsLh = self.lesionvis.lhwhiteMapper.GetInput().GetPointData().GetScalars()
        scalarsRh = self.lesionvis.rhwhiteMapper.GetInput().GetPointData().GetScalars()

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
        if(parcellationWhiteListLh == None or parcellationWhiteListRh == None):
            impactStringList, impactParcellationLabelsLh, impactParcellationLabelsRh = self.computeLesionImpact(lesionID)
            totalParcellationsAffected = len(impactStringList)
            self.lesionvis.label_TopNRegions.setText("Showing top " + str(totalParcellationsAffected) +" influenced regions")
            self.lesionvis.horizontalSlider_TopNRegions.setMaximum(totalParcellationsAffected)
            self.lesionvis.horizontalSlider_TopNRegions.blockSignals(True)
            self.lesionvis.horizontalSlider_TopNRegions.setValue(totalParcellationsAffected)
            self.lesionvis.horizontalSlider_TopNRegions.blockSignals(False)
        else:
            impactStringList, impactParcellationLabelsLh, impactParcellationLabelsRh = self.computeLesionImpact(lesionID, parcellationWhiteListLh, parcellationWhiteListRh)
        #print(impactParcellationLabelsLh)
        #print(impactParcellationLabelsRh)

        #print("LESION ID", lesionID)
        #print("SORTED LH", self.lesionMapper.parcellationLesionContributionSortedLh)

        #print("SORTED RH", self.lesionMapper.parcellationLesionContributionSortedRh)
        #lhdata, rhdata = self.lesionMapper.getTopNRegions(10, lesionID, self.lesionMapper.parcellationLesionContributionSortedLh, self.lesionMapper.parcellationLesionContributionSortedRh)
        #print("RESULTLH", lhdata)
        #print("RESULTRH", rhdata)
        

        
        functionListString = "\n"
        for elemIndex in range(len(impactStringList)):
            functionListString = functionListString + str(impactStringList[elemIndex]) + "\n"

        self.lesionMapper.overlayDataMainLeftLesionImpact["Affected Functions"] = functionListString
        self.lesionMapper.overlayDataMainLeftLesionImpact["# Functions"] = len(impactStringList)
        
        # Highlight the picked actor by changing its properties
        if(NewPickedActor!=None):
            NewPickedActor.GetMapper().ScalarVisibilityOff()
            NewPickedActor.GetProperty().SetColor(1.0, 1.0, 0.0)
            NewPickedActor.GetProperty().SetDiffuse(1.0)
            NewPickedActor.GetProperty().SetSpecular(0.0)

        if(self.lesionvis.mappingType == "Signed Distance Map"): #  If SDM, then directly map loaded scalars and return.
            #self.lesionvis.rhwhiteMapper.ScalarVisibilityOn()
            #self.lesionvis.lhwhiteMapper.ScalarVisibilityOn()
            self.lesionvis.LhMappingPolyData.GetPointData().SetActiveScalars("Distance" + str(int(lesionID)-1))
            self.lesionvis.RhMappingPolyData.GetPointData().SetActiveScalars("Distance" + str(int(lesionID)-1))
            #self.lesionvis.lhwhiteMapper.SetScalarRange(self.lesionvis.LhMappingPolyData.GetPointData().GetScalars().GetRange())
            #self.lesionvis.rhwhiteMapper.SetScalarRange(self.lesionvis.RhMappingPolyData.GetPointData().GetScalars().GetRange())
            self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetScalars(self.lesionvis.LhMappingPolyData.GetPointData().GetScalars())
            self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetScalars(self.lesionvis.RhMappingPolyData.GetPointData().GetScalars())
            ctf = vtk.vtkColorTransferFunction()
            ctf.AddRGBPoint(0.0, 1.0, 0.0, 0.0)
            ctf.AddRGBPoint(10, 0.5, 0.0, 0.0)
            ctf.AddRGBPoint(15, 1, 1, 1)    
            ctf.AddRGBPoint(100, 1, 1 , 1)
            self.lesionvis.lhwhiteMapper.SetLookupTable(ctf)
            self.lesionvis.rhwhiteMapper.SetLookupTable(ctf)
            LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainLeftLesions, self.lesionMapper.textActorLesionStatistics)
            LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainLeftLesionImpact, self.lesionMapper.textActorLesionImpact)
            return


        #vtk_colorsLh = vtk.vtkUnsignedCharArray()
        #vtk_colorsLh.SetNumberOfComponents(3)
        #vtk_colorsLh.SetName("ColorsLh")
        #vtk_colorsRh = vtk.vtkUnsignedCharArray()
        #vtk_colorsRh.SetNumberOfComponents(3)
        #vtk_colorsRh.SetName("ColorsRh")

        #clrGreen = [161,217,155]
        

        # LESION IMPACT COLOR MAPPING STARTS HERE (3D SURFACE)


        # for elem in lesionMappingRh:
        #     if(elem==True):
        #         vtk_colorsRh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
        #     else:
        #         #clrParcellationRh = self.lesionvis.metaRh[self.lesionvis.labelsRh[]]["color"]
        #         vtk_colorsRh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
        # for elem in lesionMappingLh:
        #     if(elem==True):
        #         vtk_colorsLh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
        #     else:
        #         vtk_colorsLh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])

        # RIGHT HEMISPHERE
        for vertexIndex in range(scalarsRh.GetNumberOfTuples()):
            if(self.lesionMapper.lesionMappingRh[vertexIndex] == True):
                self.vtk_colorsRh.SetTuple3(vertexIndex, self.clrRed[0], self.clrRed[1], self.clrRed[2])
            else:
                if(self.lesionvis.labelsRh[vertexIndex] == -1):
                    clrParcellationRh = self.lesionvis.metaRh[0]["color"]#[25,5,25]
                    if(self.lesionvis.labelsRh[vertexIndex] in impactParcellationLabelsRh and self.lesionvis.checkBox_AutoHighlightRegions.isChecked()==True): # If parcellation label id is element of affected parcellations then darken
                        lightClr = clrParcellationRh
                    else: # else lighten up parcellation.
                        lightClr = self.tintColor(clrParcellationRh, 0.1)
                else:
                    clrParcellationRh = self.lesionvis.metaRh[self.lesionvis.labelsRh[vertexIndex]]["color"]
                    if(self.lesionvis.labelsRh[vertexIndex] in impactParcellationLabelsRh and self.lesionvis.checkBox_AutoHighlightRegions.isChecked()==True): # If parcellation label id is element of affected parcellations then darken
                        lightClr = clrParcellationRh
                    else: # else lighten up parcellation.
                        lightClr = self.tintColor(clrParcellationRh, 0.1)
                self.vtk_colorsRh.SetTuple3(vertexIndex, lightClr[0], lightClr[1], lightClr[2])

        # LEFT HEMISPHERE
        for vertexIndex in range(scalarsLh.GetNumberOfTuples()):
            if(self.lesionMapper.lesionMappingLh[vertexIndex] == True):
                self.vtk_colorsLh.SetTuple3(vertexIndex, self.clrRed[0], self.clrRed[1], self.clrRed[2])
            else:
                if(self.lesionvis.labelsLh[vertexIndex] == -1):
                    clrParcellationLh = self.lesionvis.metaLh[0]["color"]#[25,5,25]
                    if(self.lesionvis.labelsLh[vertexIndex] in impactParcellationLabelsLh and self.lesionvis.checkBox_AutoHighlightRegions.isChecked()==True): # If parcellation label id is element of affected parcellations then darken
                        lightClr = clrParcellationLh
                    else:  # else lighten up parcellation.
                        lightClr = self.tintColor(clrParcellationLh, 0.1)
                else:
                    clrParcellationLh = self.lesionvis.metaLh[self.lesionvis.labelsLh[vertexIndex]]["color"]
                    if(self.lesionvis.labelsLh[vertexIndex] in impactParcellationLabelsLh and self.lesionvis.checkBox_AutoHighlightRegions.isChecked()==True): # If parcellation label id is element of affected parcellations then darken
                        lightClr = clrParcellationLh
                    else:  # else lighten up parcellation.
                        lightClr = self.tintColor(clrParcellationLh, 0.1)
                self.vtk_colorsLh.SetTuple3(vertexIndex, lightClr[0], lightClr[1], lightClr[2])

        self.lesionvis.rhwhiteMapper.ScalarVisibilityOn()
        self.lesionvis.lhwhiteMapper.ScalarVisibilityOn()
        self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetScalars(self.vtk_colorsRh)
        self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetScalars(self.vtk_colorsLh)

        # LESION IMPACT COLOR MAPPING ENDS HERE (3D SURFACE)

        #self.NewPickedActor.GetProperty().SetRepresentationToWireframe()
        LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainLeftLesions, self.lesionMapper.textActorLesionStatistics)
        LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainLeftLesionImpact, self.lesionMapper.textActorLesionImpact)

    # Highlight lesions based on selected parcellation.
    def highlightLesionsBasedOnSelectedParcellation(self, parcellationAssociatedLesionList, selectedParcellationLabel, hemisphere):
        for actor in self.lesionvis.lesionActors:
            lesionID = actor.GetProperty().GetInformation().Get(self.lesionvis.informationUniqueKey)

            if(self.lesionvis.pushButton_Discrete.isChecked() == True):
                actor.GetMapper().ScalarVisibilityOff()
            else:
                actor.GetMapper().ScalarVisibilityOn()

            if lesionID in parcellationAssociatedLesionList:
                actor.GetMapper().ScalarVisibilityOff()
                actor.GetProperty().SetColor(1.0, 1.0, 0.0)
                actor.GetProperty().SetDiffuse(1.0)
                actor.GetProperty().SetSpecular(0.0)

        influencingLesionCount = len(parcellationAssociatedLesionList)
        self.lesionvis.horizontalSlider_TopNLesions.setMaximum(influencingLesionCount)
        self.lesionvis.horizontalSlider_TopNLesions.blockSignals(True)
        self.lesionvis.horizontalSlider_TopNLesions.setValue(influencingLesionCount)
        self.lesionvis.horizontalSlider_TopNLesions.blockSignals(False)
        self.lesionvis.label_TopNLesions.setText("Showing top " + str(influencingLesionCount) +" influenced lesions")

    # Update surface colors based on user interaction.
    def updateSurfaceColorsForParcellationPick(self, hemisphere, pickedParcellationColor):
        # if(self.lesionMapper.lesionMappingLh.size > 0): # Can use lesionMappingRh also. This is to check if lesion mapping is done atleast once.
        #     self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsLh")
        #     self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsRh")
        #     print("ColorsLh")
        # else: # Use parcellation colors that has no red lesion impact patches
        #     self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferLh")
        #     self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferRh")
        #     print("ColorsFreeSurferLh")

        self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferLh")
        self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferRh")

        scalarsLh = self.lesionvis.lhwhiteMapper.GetInput().GetPointData().GetScalars()
        scalarsRh = self.lesionvis.rhwhiteMapper.GetInput().GetPointData().GetScalars()

        for i in range(scalarsLh.GetNumberOfTuples()):
            if(self.lesionMapper.lesionMappingLh.size > 0 and self.lesionMapper.lesionMappingLh[i] == True):
                scalarsLh.SetTuple3(i, self.clrRed[0], self.clrRed[1], self.clrRed[2])
            else:
                if(self.lesionvis.labelsLh[i] == -1):
                    clrParcellationLh = self.lesionvis.metaLh[0]["color"]
                    #print("entry here", clrParcellationLh)
                else:
                    clrParcellationLh = self.lesionvis.metaLh[self.lesionvis.labelsLh[i]]["color"]
                    lightClr = self.tintColor(clrParcellationLh, 0.1)
                if(clrParcellationLh == pickedParcellationColor and hemisphere == "lh"): # If picked color is same as current color, Apply tint.
                    scalarsLh.SetTuple(i, self.tintColor(clrParcellationLh, 0.9)) # Darken parcellation
                else:
                    scalarsLh.SetTuple3(i, lightClr[0], lightClr[1], lightClr[2])

        for i in range(scalarsRh.GetNumberOfTuples()):
            if(self.lesionMapper.lesionMappingRh.size > 0 and self.lesionMapper.lesionMappingRh[i] == True):
                scalarsRh.SetTuple3(i, self.clrRed[0], self.clrRed[1], self.clrRed[2])
            else:
                if(self.lesionvis.labelsRh[i] == -1):
                    clrParcellationRh = self.lesionvis.metaRh[0]["color"]
                    #print("entry here", clrParcellationRh)
                else:
                    clrParcellationRh = self.lesionvis.metaRh[self.lesionvis.labelsRh[i]]["color"]
                    lightClr = self.tintColor(clrParcellationRh, 0.1)
                if(clrParcellationRh == pickedParcellationColor and hemisphere == "rh"): # If picked color is same as current color, Apply tint.
                    scalarsRh.SetTuple(i, self.tintColor(clrParcellationRh, 0.9)) # darken parcellation.
                else:
                    scalarsRh.SetTuple3(i, lightClr[0], lightClr[1], lightClr[2])

        #self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetScalars(scalarsRh)
        #self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetScalars(scalarsLh)

    # # Update surface colors based on user interaction. (Original)
    # def updateSurfaceColorsForParcellationPick(self, hemisphere, pickedParcellationColor):
    #     scalarsLh = self.lesionvis.lhwhiteMapper.GetInput().GetPointData().GetScalars()
    #     scalarsRh = self.lesionvis.rhwhiteMapper.GetInput().GetPointData().GetScalars()

    #     for i in range(scalarsLh.GetNumberOfTuples()):
    #         if(self.lesionMapper.lesionMappingLh != None):
    #             if(self.lesionMapper.lesionMappingLh[i] == True):
    #                 scalarsLh.SetTuple3(i, self.clrRed[0], self.clrRed[1], self.clrRed[2])
    #         else:
    #             if(self.lesionvis.labelsLh[i] == -1):
    #                 clrParcellationLh = self.lesionvis.metaLh[0]["color"]
    #             else:
    #                 clrParcellationLh = self.lesionvis.metaLh[self.lesionvis.labelsLh[i]]["color"]
    #                 lightClr = self.tintColor(clrParcellationLh, 0.1)
    #             if(clrParcellationLh == pickedParcellationColor and hemisphere == "lh"): # If picked color is same as current color, Apply tint.
    #                 scalarsLh.SetTuple(i, self.tintColor(clrParcellationLh, 0.9)) # Darken parcellation
    #             else:
    #                 scalarsLh.SetTuple3(i, lightClr[0], lightClr[1], lightClr[2])

    #     for i in range(scalarsRh.GetNumberOfTuples()):
    #         if(self.lesionMapper.lesionMappingRh!=None):
    #             if(self.lesionMapper.lesionMappingRh[i] == True):
    #                 scalarsRh.SetTuple3(i, self.clrRed[0], self.clrRed[1], self.clrRed[2])
    #         else:
    #             if(self.lesionvis.labelsRh[i] == -1):
    #                 clrParcellationRh = self.lesionvis.metaRh[0]["color"]
    #             else:
    #                 clrParcellationRh = self.lesionvis.metaRh[self.lesionvis.labelsRh[i]]["color"]
    #                 lightClr = self.tintColor(clrParcellationRh, 0.1)
    #             if(clrParcellationRh == pickedParcellationColor and hemisphere == "rh"): # If picked color is same as current color, Apply tint.
    #                 scalarsRh.SetTuple(i, self.tintColor(clrParcellationRh, 0.9)) # darken parcellation.
    #             else:
    #                 scalarsRh.SetTuple3(i, lightClr[0], lightClr[1], lightClr[2])

    #     self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsLh")
    #     self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsRh")

    def leftButtonReleaseEvent(self, obj, event):
        if(self.MouseMotion == 0):
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
                shouldProcessNewActor = True
                itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.informationKey)
                if(itemType=="structural tracts"):# or itemType=="ventricles"): # If clicked on streamtubes.
                    shouldProcessNewActor = False

                if(shouldProcessNewActor == True): # Process only the relevant actors.
                    lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.informationUniqueKey)
                    self.currentLesionID = lesionID

                    # If we picked something before, reset its property
                    if self.LastPickedActor:
                        self.LastPickedActor.GetMapper().ScalarVisibilityOn()
                        self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)

                    # Save the property of the picked actor so that we can
                    # restore it next time
                    self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
                    #print(cellPicker.GetPointId())

                    #print(self.lesionvis.labelsLh)
                    #print(self.lesionvis.metaLh)


                    if("lh" in str(itemType)):
                        self.currentParcellationLabel = [self.lesionvis.labelsLh[cellPicker.GetPointId()], "lh"]
                        parcellationIndex = self.lesionvis.uniqueLabelsLh.tolist().index(self.lesionvis.labelsLh[cellPicker.GetPointId()])
                        self.lesionMapper.overlayDataMainRightParcellationImpact["SELECTED BRAIN REGION:"] = str(self.lesionvis.regionsLh[self.lesionvis.uniqueLabelsLh.tolist().index(self.lesionvis.labelsLh[cellPicker.GetPointId()])].decode('utf-8'))
                        self.lesionMapper.overlayDataMainRightParcellationImpact["LESION INFLUENCE ON SELECTED REGION:"] = str("{0:.2f}".format(self.lesionMapper.parcellationAffectedPercentageLh[parcellationIndex])) + "%"
                        self.lesionMapper.overlayDataMainRightParcellationImpact["NUMBER OF INFLUENCING LESIONS:"] = self.lesionMapper.parcellationLesionInfluenceCountLh[parcellationIndex]
                        parcellationAssociatedLesionList = list(self.lesionMapper.parcellationAssociatedLesionsLh[parcellationIndex].keys())
                        self.lesionMapper.overlayDataMainRightParcellationImpact["INFLUENCING LESION IDs:"] = parcellationAssociatedLesionList
                        if(self.lesionvis.labelsLh[cellPicker.GetPointId()] != -1): # If not corpus callosum
                            pickedParcellationColor = self.lesionvis.metaLh[self.lesionvis.labelsLh[cellPicker.GetPointId()]]["color"]
                        else: # if corpus callosum
                            pickedParcellationColor = [25, 5, 25, 0] # color label of corpus callosum from freesurfer.
                        #print(pickedParcellationColor)
                        self.updateSurfaceColorsForParcellationPick("lh", pickedParcellationColor)
                        self.highlightLesionsBasedOnSelectedParcellation(parcellationAssociatedLesionList, self.lesionvis.labelsLh[cellPicker.GetPointId()], "lh")

                    if("rh" in str(itemType)):
                        self.currentParcellationLabel = [self.lesionvis.labelsRh[cellPicker.GetPointId()], "rh"]
                        parcellationIndex = self.lesionvis.uniqueLabelsRh.tolist().index(self.lesionvis.labelsRh[cellPicker.GetPointId()])
                        self.lesionMapper.overlayDataMainRightParcellationImpact["SELECTED BRAIN REGION:"] = str(self.lesionvis.regionsRh[self.lesionvis.uniqueLabelsRh.tolist().index(self.lesionvis.labelsRh[cellPicker.GetPointId()])].decode('utf-8'))
                        self.lesionMapper.overlayDataMainRightParcellationImpact["LESION INFLUENCE ON SELECTED REGION:"] = str("{0:.2f}".format(self.lesionMapper.parcellationAffectedPercentageRh[parcellationIndex])) + "%"
                        self.lesionMapper.overlayDataMainRightParcellationImpact["NUMBER OF INFLUENCING LESIONS:"] = self.lesionMapper.parcellationLesionInfluenceCountRh[parcellationIndex]
                        parcellationAssociatedLesionList = list(self.lesionMapper.parcellationAssociatedLesionsRh[parcellationIndex].keys())
                        self.lesionMapper.overlayDataMainRightParcellationImpact["INFLUENCING LESION IDs:"] = parcellationAssociatedLesionList
                        if(self.lesionvis.labelsRh[cellPicker.GetPointId()] != -1): # If not corpus callosum
                            pickedParcellationColor = self.lesionvis.metaRh[self.lesionvis.labelsRh[cellPicker.GetPointId()]]["color"]
                        else: # if corpuscallosum
                            pickedParcellationColor = [25, 5, 25, 0] # color label of corpus callosum from freesurfer.
                        #print(pickedParcellationColor)
                        self.updateSurfaceColorsForParcellationPick("rh", pickedParcellationColor)
                        self.highlightLesionsBasedOnSelectedParcellation(parcellationAssociatedLesionList, self.lesionvis.labelsRh[cellPicker.GetPointId()], "rh")

                    if itemType==None: # Itemtype is None for lesions. They only have Ids.
                        self.mapLesionToSurface(lesionID, self.NewPickedActor)
                        self.lesionvis.userPickedLesion = lesionID
                        self.lesionvis.style.clickedLesionActor = self.NewPickedActor

                        # Reset view style for all other lesions.
                        for actor in self.lesionvis.lesionActors:
                            scenelesionID = actor.GetProperty().GetInformation().Get(self.lesionvis.informationUniqueKey)
                            if(scenelesionID!=lesionID):
                                if(self.lesionvis.pushButton_Discrete.isChecked() == True):
                                    actor.GetMapper().ScalarVisibilityOff()
                                else:
                                    actor.GetMapper().ScalarVisibilityOn()


                        # Display streamlines associated with the lesion
                        if(self.lesionvis.pushButton_EnableFibers.isChecked()==True):
                            if(self.currentActiveStreamlineActor!=None):
                                self.lesionvis.renDualLeft.RemoveActor(self.currentActiveStreamlineActor)

                            if(self.lesionvis.streamActors != None): # Either diffusion or HE
                                streamlineActor = self.lesionvis.streamActors[int(lesionID)-1]
                                self.lesionvis.renDualLeft.AddActor(streamlineActor)
                                self.currentActiveStreamlineActor = streamlineActor
                            else: # Signed Distance Map is active
                                pass
                            
                    LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainRightParcellationImpact, self.lesionMapper.textActorParcellation)
                    
                    # save the last picked actor
                    self.LastPickedActor = self.NewPickedActor
            else: # no actor picked. Clicked on background space.
                if(self.lesionMapper.interactionStyleLeft.currentActiveStreamlineActor!=None): # Check if there are streamlineActors, if yes, remove.
                    self.lesionvis.renDualLeft.RemoveActor(self.lesionMapper.interactionStyleLeft.currentActiveStreamlineActor)
                # Reset view style for all lesions. (no lesions picked state)
                self.resetToDefaultViewLesions()
                self.resetToDefaultViewSurface() # Reset view style for parcellations.
                self.lesionMapper.ResetTextOverlay()
                self.lesionMapper.Refresh()

                # Reset overlays.
        self.OnLeftButtonUp()
        return

    def resetToDefaultViewLesions(self):
        self.lesionMapper.lesionMappingLh = np.empty(shape=(0))
        self.lesionMapper.lesionMappingRh = np.empty(shape=(0))
        for actor in self.lesionvis.lesionActors:
            if(self.lesionvis.pushButton_Discrete.isChecked() == True):
                self.lesionvis.updateLesionColorsDiscrete()
                break
            else:
                actor.GetMapper().ScalarVisibilityOn()
        self.LastPickedActor = None
        self.currentLesionID = None
        self.currentParcellationLabel = None

    def resetToDefaultViewSurface(self):
        self.lesionMapper.lesionMappingLh = np.empty(shape=(0))
        self.lesionMapper.lesionMappingRh = np.empty(shape=(0))
        self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferLh")
        self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsFreeSurferRh")
        
        # self.lesionvis.colorsLightLh.DeepCopy(self.vtk_colorsLh)
        # self.lesionvis.colorsLightRh.DeepCopy(self.vtk_colorsRh)
        self.vtk_colorsLh.DeepCopy(self.lesionvis.colorsLightLh)
        self.vtk_colorsRh.DeepCopy(self.lesionvis.colorsLightRh)

        self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetScalars(self.vtk_colorsRh)
        self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetScalars(self.vtk_colorsLh)
        self.lesionvis.label_TopNRegions.setText("Showing top N influenced regions")

    def mouseMoveEvent(self, obj, event):
        self.MouseMotion = 1
        self.OnMouseMove()
        return

    def leftButtonPressEvent(self,obj,event):
        #print("leftButtonPressEvent")
        self.MouseMotion = 0
        self.OnLeftButtonDown()
