import os
import vtk
import LesionUtils
import numpy as np
from nibabel import freesurfer
import json
import copy

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
      self.interactionStyleLeft = None
      self.interactionStyleRight = None
      #print("done1")

  def leftCameraModifiedCallback(self,obj,event):
      self.lesionvis.iren_LesionMapDualRight.Render()
  def rightCameraModifiedCallback(self,obj,event):
      self.lesionvis.iren_LesionMapDualLeft.Render()

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
    self.overlayDataMainRightParcellationImpact = {"SELECTED BRAIN REGION:":"NA", "LESION INFLUENCE ON SELECTED REGION:":"NA", "NUMBER OF INFLUENCING LESIONS:":"NA", "INFLUENCING LESION IDs:" : "NA"}
    
    LesionUtils.setOverlayText(self.overlayDataMainLeftLesions, self.textActorLesionStatistics)
    LesionUtils.setOverlayText(self.overlayDataMainLeftLesionImpact, self.textActorLesionImpact)
    LesionUtils.setOverlayText(self.overlayDataMainRightParcellationImpact, self.textActorParcellation)

    # Load parcellation data from precomputed files.
    self.loadParcellationData()

    # Add legend data
    legend = vtk.vtkLegendBoxActor()
    legend.SetNumberOfEntries(2)
    overlayTextProperty = vtk.vtkTextProperty()
    overlayTextProperty.SetFontFamily(4)
    overlayTextProperty.SetFontFile("fonts\\RobotoMono-Medium.ttf")
    overlayTextProperty.SetFontSize(16)
    legend.SetEntryTextProperty(overlayTextProperty)
    legendBox = vtk.vtkCubeSource()
    legendBox.Update()
    legend.SetEntryString(0, "NORMAL AREA")
    legend.SetEntryString(1, "LESION INFLUENCE AREA")
    legend.SetEntrySymbol(0, legendBox.GetOutput())
    legend.SetEntrySymbol(1, legendBox.GetOutput())
    legend.SetEntryColor(0, [161/255,217/255,155/255])
    legend.SetEntryColor(1, [227/255,74/255,51/255])
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
        self.AddObserver("PickEvent",self.pickEvent)
        self.lesionvis = lesionvis
        self.lesionMapper = lesionMapper
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.currentActiveStreamlineActor = None
        self.currentLesionID = None
        self.clrRed = [227,74,51]

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

    def tintColor(self, clr, p=0.5):
        r = 255 - int(p * (255 - clr[0]))
        g = 255 - int(p * (255 - clr[1]))
        b = 255 - int(p * (255 - clr[2]))
        return [r,g,b]

    def mapLesionToSurface(self, lesionID, NewPickedActor):
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
        NewPickedActor.GetMapper().ScalarVisibilityOff()
        NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
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


        vtk_colorsLh = vtk.vtkUnsignedCharArray()
        vtk_colorsLh.SetNumberOfComponents(3)
        vtk_colorsLh.SetName("ColorsLh")
        vtk_colorsRh = vtk.vtkUnsignedCharArray()
        vtk_colorsRh.SetNumberOfComponents(3)
        vtk_colorsRh.SetName("ColorsRh")

        #clrGreen = [161,217,155]
        

        # LESION IMPACT COLOR MAPPING STARTS HERE (3D SURFACE)
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

        for vertexIndex in range(self.lesionMapper.lesionMappingRh.size):
            if(self.lesionMapper.lesionMappingRh[vertexIndex] == True):
                vtk_colorsRh.InsertNextTuple3(self.clrRed[0], self.clrRed[1], self.clrRed[2])
            else:
                if(self.lesionvis.labelsRh[vertexIndex] == -1):
                    clrParcellationRh = [25,5,25]
                else:
                    clrParcellationRh = self.lesionvis.metaRh[self.lesionvis.labelsRh[vertexIndex]]["color"]
                    lightClr = self.tintColor(clrParcellationRh, 0.2)
                vtk_colorsRh.InsertNextTuple3(lightClr[0], lightClr[1], lightClr[2])
        for vertexIndex in range(self.lesionMapper.lesionMappingLh.size):
            if(self.lesionMapper.lesionMappingLh[vertexIndex] == True):
                vtk_colorsLh.InsertNextTuple3(self.clrRed[0], self.clrRed[1], self.clrRed[2])
            else:
                if(self.lesionvis.labelsLh[vertexIndex] == -1):
                    clrParcellationRh = [25,5,25]
                else:
                    clrParcellationLh = self.lesionvis.metaLh[self.lesionvis.labelsLh[vertexIndex]]["color"]
                    lightClr = self.tintColor(clrParcellationLh, 0.2)
                vtk_colorsLh.InsertNextTuple3(lightClr[0], lightClr[1], lightClr[2])

        self.lesionvis.rhwhiteMapper.ScalarVisibilityOn()
        self.lesionvis.lhwhiteMapper.ScalarVisibilityOn()
        self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetScalars(vtk_colorsRh)
        self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetScalars(vtk_colorsLh)

        # LESION IMPACT COLOR MAPPING ENDS HERE (3D SURFACE)

        #self.NewPickedActor.GetProperty().SetRepresentationToWireframe()
        LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainLeftLesions, self.lesionMapper.textActorLesionStatistics)
        LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainLeftLesionImpact, self.lesionMapper.textActorLesionImpact)

    def pickEvent(self,obj,event):
        print("pick event")

    # Highlight lesions based on selected parcellation.
    def highlightLesionsBasedOnSelectedParcellation(self, parcellationAssociatedLesionList):
        for actor in self.lesionvis.lesionActors:
            lesionID = actor.GetProperty().GetInformation().Get(self.lesionvis.informationUniqueKey)
            actor.GetMapper().ScalarVisibilityOn()
            if lesionID in parcellationAssociatedLesionList:
                actor.GetMapper().ScalarVisibilityOff()
                actor.GetProperty().SetColor(1.0, 1.0, 0.0)
                actor.GetProperty().SetDiffuse(1.0)
                actor.GetProperty().SetSpecular(0.0)


    # Update surface colors based on user interaction.
    def updateSurfaceColorsForParcellationPick(self, hemisphere, pickedParcellationColor):
        scalarsLh = self.lesionvis.lhwhiteMapper.GetInput().GetPointData().GetScalars()
        scalarsRh = self.lesionvis.rhwhiteMapper.GetInput().GetPointData().GetScalars()
        for i in range(scalarsLh.GetNumberOfTuples()):
            if(self.lesionMapper.lesionMappingLh[i] == True):
                    scalarsLh.SetTuple3(i, self.clrRed[0], self.clrRed[1], self.clrRed[2])
            else:
                if(self.lesionvis.labelsLh[i] == -1):
                    clrParcellationLh = self.lesionvis.metaLh[0]["color"]
                else:
                    clrParcellationLh = self.lesionvis.metaLh[self.lesionvis.labelsLh[i]]["color"]
                    lightClr = self.tintColor(clrParcellationLh, 0.1)
                if(clrParcellationLh == pickedParcellationColor and hemisphere == "lh"): # If picked color is same as current color, Apply tint.
                    scalarsLh.SetTuple(i, self.tintColor(clrParcellationLh, 0.9))
                else:
                    scalarsLh.SetTuple3(i, lightClr[0], lightClr[1], lightClr[2])

        for i in range(scalarsRh.GetNumberOfTuples()):
            if(self.lesionMapper.lesionMappingRh[i] == True):
                    scalarsRh.SetTuple3(i, self.clrRed[0], self.clrRed[1], self.clrRed[2])
            else:
                if(self.lesionvis.labelsRh[i] == -1):
                    clrParcellationRh = self.lesionvis.metaRh[0]["color"]
                else:
                    clrParcellationRh = self.lesionvis.metaRh[self.lesionvis.labelsRh[i]]["color"]
                    lightClr = self.tintColor(clrParcellationRh, 0.1)
                if(clrParcellationRh == pickedParcellationColor and hemisphere == "rh"): # If picked color is same as current color, Apply tint.
                    scalarsRh.SetTuple(i, self.tintColor(clrParcellationRh, 0.9))
                else:
                    scalarsRh.SetTuple3(i, lightClr[0], lightClr[1], lightClr[2])

        self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsLh")
        self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetActiveScalars("ColorsRh")

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
            self.currentLesionID = lesionID
            #print(cellPicker.GetPointId())

            if("lh" in str(itemType)):
                parcellationIndex = self.lesionvis.uniqueLabelsLh.tolist().index(self.lesionvis.labelsLh[cellPicker.GetPointId()])
                self.lesionMapper.overlayDataMainRightParcellationImpact["SELECTED BRAIN REGION:"] = str(self.lesionvis.regionsLh[self.lesionvis.uniqueLabelsLh.tolist().index(self.lesionvis.labelsLh[cellPicker.GetPointId()])].decode('utf-8'))
                self.lesionMapper.overlayDataMainRightParcellationImpact["LESION INFLUENCE ON SELECTED REGION:"] = str("{0:.2f}".format(self.lesionMapper.parcellationAffectedPercentageLh[parcellationIndex])) + "%"
                self.lesionMapper.overlayDataMainRightParcellationImpact["NUMBER OF INFLUENCING LESIONS:"] = self.lesionMapper.parcellationLesionInfluenceCountLh[parcellationIndex]
                parcellationAssociatedLesionList = list(self.lesionMapper.parcellationAssociatedLesionsLh[parcellationIndex].keys())
                self.lesionMapper.overlayDataMainRightParcellationImpact["INFLUENCING LESION IDs:"] = parcellationAssociatedLesionList
                pickedParcellationColor = self.lesionvis.metaLh[self.lesionvis.labelsLh[cellPicker.GetPointId()]]["color"]
                self.updateSurfaceColorsForParcellationPick("lh", pickedParcellationColor)
                self.highlightLesionsBasedOnSelectedParcellation(parcellationAssociatedLesionList)

            if("rh" in str(itemType)):
                parcellationIndex = self.lesionvis.uniqueLabelsRh.tolist().index(self.lesionvis.labelsRh[cellPicker.GetPointId()])
                self.lesionMapper.overlayDataMainRightParcellationImpact["SELECTED BRAIN REGION:"] = str(self.lesionvis.regionsRh[self.lesionvis.uniqueLabelsRh.tolist().index(self.lesionvis.labelsRh[cellPicker.GetPointId()])].decode('utf-8'))
                self.lesionMapper.overlayDataMainRightParcellationImpact["LESION INFLUENCE ON SELECTED REGION:"] = str("{0:.2f}".format(self.lesionMapper.parcellationAffectedPercentageRh[parcellationIndex])) + "%"
                self.lesionMapper.overlayDataMainRightParcellationImpact["NUMBER OF INFLUENCING LESIONS:"] = self.lesionMapper.parcellationLesionInfluenceCountRh[parcellationIndex]
                parcellationAssociatedLesionList = list(self.lesionMapper.parcellationAssociatedLesionsRh[parcellationIndex].keys())
                self.lesionMapper.overlayDataMainRightParcellationImpact["INFLUENCING LESION IDs:"] = parcellationAssociatedLesionList
                pickedParcellationColor = self.lesionvis.metaRh[self.lesionvis.labelsRh[cellPicker.GetPointId()]]["color"]
                self.updateSurfaceColorsForParcellationPick("rh", pickedParcellationColor)
                self.highlightLesionsBasedOnSelectedParcellation(parcellationAssociatedLesionList)

            if itemType==None: # Itemtype is None for lesions. They only have Ids.
                self.mapLesionToSurface(lesionID, self.NewPickedActor)
                self.lesionvis.userPickedLesion = lesionID
                self.lesionvis.style.clickedLesionActor = self.NewPickedActor
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
                    

                # # Set overlay dictionary
                # self.centerOfMass = self.lesionvis.lesionCentroids[int(lesionID)-1]
                # self.lesionMapper.overlayDataMainLeftLesions["Lesion ID"] = str(lesionID)
                # self.lesionMapper.overlayDataMainLeftLesions["Centroid"] = str("{0:.2f}".format(self.centerOfMass[0])) +", " +  str("{0:.2f}".format(self.centerOfMass[1])) + ", " + str("{0:.2f}".format(self.centerOfMass[2]))
                # self.lesionMapper.overlayDataMainLeftLesions["Voxel Count"] = self.lesionvis.lesionNumberOfPixels[int(lesionID)-1]
                # self.lesionMapper.overlayDataMainLeftLesions["Elongation"] = "{0:.2f}".format(self.lesionvis.lesionElongation[int(lesionID)-1])
                # self.lesionMapper.overlayDataMainLeftLesions["Lesion Perimeter"] = "{0:.2f}".format(self.lesionvis.lesionPerimeter[int(lesionID)-1])
                # self.lesionMapper.overlayDataMainLeftLesions["Lesion Spherical Radius"] = "{0:.2f}".format(self.lesionvis.lesionSphericalRadius[int(lesionID)-1])
                # self.lesionMapper.overlayDataMainLeftLesions["Lesion Spherical Perimeter"] = "{0:.2f}".format(self.lesionvis.lesionSphericalPerimeter[int(lesionID)-1])
                # self.lesionMapper.overlayDataMainLeftLesions["Lesion Flatness"] = "{0:.2f}".format(self.lesionvis.lesionFlatness[int(lesionID)-1])
                # self.lesionMapper.overlayDataMainLeftLesions["Lesion Roundness"] = "{0:.2f}".format(self.lesionvis.lesionRoundness[int(lesionID)-1])
                # self.lesionMapper.overlayDataMainLeftLesionImpact["Lesion ID"] = str(lesionID)
                # impactStringList = self.computeLesionImpact(lesionID)
                # functionListString = "\n"
                # for elemIndex in range(len(impactStringList)):
                #     functionListString = functionListString + str(impactStringList[elemIndex]) + "\n"

                # self.lesionMapper.overlayDataMainLeftLesionImpact["Affected Functions"] = functionListString
                # self.lesionMapper.overlayDataMainLeftLesionImpact["# Functions"] = len(impactStringList)
                
                # # Highlight the picked actor by changing its properties
                # self.NewPickedActor.GetMapper().ScalarVisibilityOff()
                # self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                # self.NewPickedActor.GetProperty().SetDiffuse(1.0)
                # self.NewPickedActor.GetProperty().SetSpecular(0.0)
                # vtk_colorsLh = vtk.vtkUnsignedCharArray()
                # vtk_colorsLh.SetNumberOfComponents(3)
                # vtk_colorsRh = vtk.vtkUnsignedCharArray()
                # vtk_colorsRh.SetNumberOfComponents(3)

                # clrGreen = [161,217,155]
                # clrRed = [227,74,51]

                # # LESION IMPACT COLOR MAPPING STARTS HERE (3D SURFACE)
                # numberOfPointsRh = self.lesionvis.rhwhiteMapper.GetInput().GetNumberOfPoints()
                # numberOfPointsLh = self.lesionvis.lhwhiteMapper.GetInput().GetNumberOfPoints()
                # vertexIndexArrayRh = np.arange(numberOfPointsRh)
                # vertexIndexArrayLh = np.arange(numberOfPointsLh)
                # affectedRh = np.asarray(self.lesionvis.lesionAffectedPointIdsRh[int(lesionID)-1])
                # affectedLh = np.asarray(self.lesionvis.lesionAffectedPointIdsLh[int(lesionID)-1])
                # lesionMappingRh = np.isin(vertexIndexArrayRh, affectedRh)
                # lesionMappingLh = np.isin(vertexIndexArrayLh, affectedLh)
                # for elem in lesionMappingRh:
                #     if(elem==True):
                #         vtk_colorsRh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                #     else:
                #         vtk_colorsRh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
                # for elem in lesionMappingLh:
                #     if(elem==True):
                #         vtk_colorsLh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                #     else:
                #         vtk_colorsLh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])

                # self.lesionvis.rhwhiteMapper.ScalarVisibilityOn()
                # self.lesionvis.lhwhiteMapper.ScalarVisibilityOn()
                # self.lesionvis.rhwhiteMapper.GetInput().GetPointData().SetScalars(vtk_colorsRh)
                # self.lesionvis.lhwhiteMapper.GetInput().GetPointData().SetScalars(vtk_colorsLh)
                # # LESION IMPACT COLOR MAPPING ENDS HERE (3D SURFACE)

                # #self.NewPickedActor.GetProperty().SetRepresentationToWireframe()
                # LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainLeftLesions, self.lesionMapper.textActorLesionStatistics)
                # LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainLeftLesionImpact, self.lesionMapper.textActorLesionImpact)
            
            LesionUtils.setOverlayText(self.lesionMapper.overlayDataMainRightParcellationImpact, self.lesionMapper.textActorParcellation)
             
            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor

        
        self.OnLeftButtonDown()
        return