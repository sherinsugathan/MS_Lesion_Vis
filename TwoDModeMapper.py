import os
import vtk
import LesionUtils
import numpy as np
from nibabel import freesurfer
import json
from PyQt5 import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class TwoDModeMapper():
  def __init__(self, lesionvis):
    self.lesionvis = lesionvis

    xmins = [0,.5,0,.5]
    xmaxs = [0.5,1,0.5,1]
    ymins = [0,0,.5,.5]
    ymaxs = [0.5,0.5,1,1]

    self.vl_lesion2x2 = Qt.QVBoxLayout()
    self.vtkWidget2x2 = QVTKRenderWindowInteractor(self.lesionvis.frame_2x2)
    self.vl_lesion2x2.addWidget(self.vtkWidget2x2)
    self.vtkWidget2x2.Initialize()

    self.rendererLesion = vtk.vtkRenderer()
    self.rendererSurface = vtk.vtkRenderer()
    self.rendererUnfoldedRh = vtk.vtkRenderer()
    self.rendererUnfoldedLh = vtk.vtkRenderer()

    self.rendererLesion.SetBackground(0.0078,0.0470,0.0196)
    self.rendererSurface.SetBackground(0.0039,0.0196,0.0078)
    self.rendererUnfoldedRh.SetBackground(0.0039,0.0196,0.0078)
    self.rendererUnfoldedLh.SetBackground(0.0078,0.0470,0.0196)

    self.rendererLesion.SetViewport(xmins[2], ymins[2], xmaxs[2], ymaxs[2])
    self.rendererSurface.SetViewport(xmins[0], ymins[0], xmaxs[0], ymaxs[0])
    self.rendererUnfoldedRh.SetViewport(xmins[3], ymins[3], xmaxs[3], ymaxs[3])
    self.rendererUnfoldedLh.SetViewport(xmins[1], ymins[1], xmaxs[1], ymaxs[1])

    self.vtkWidget2x2.GetRenderWindow().AddRenderer(self.rendererLesion)
    self.vtkWidget2x2.GetRenderWindow().AddRenderer(self.rendererSurface)
    self.vtkWidget2x2.GetRenderWindow().AddRenderer(self.rendererUnfoldedRh)
    self.vtkWidget2x2.GetRenderWindow().AddRenderer(self.rendererUnfoldedLh)

    self.iren_2x2 = self.vtkWidget2x2.GetRenderWindow().GetInteractor()

    self.rendererLesion.ResetCamera()
    self.rendererSurface.ResetCamera()
    self.rendererUnfoldedRh.ResetCamera()
    self.rendererUnfoldedLh.ResetCamera()

    self.lesionvis.frame_2x2.setLayout(self.vl_lesion2x2)

    self.iren_2x2.Initialize()
    self.rendererTypes = {id(self.rendererLesion):"tbcamera", id(self.rendererSurface):"tbcamera", id(self.rendererUnfoldedRh):"image", id(self.rendererUnfoldedLh):"image"}

    #   self.textActorLesionStatistics = vtk.vtkTextActor() # Left dual Text actor to show lesion properties
    #   self.textActorParcellation = vtk.vtkTextActor() # Right dual text actor for showing parcellation data
    #   self.textActorLesionImpact = vtk.vtkTextActor() # Left dual text actor for showing lesion impact.
    #   self.textActorLesionStatistics.UseBorderAlignOff() 
    #   self.textActorLesionStatistics.SetPosition(10,0)
    #   self.textActorLesionStatistics.GetTextProperty().SetFontFamily(4)
    #   self.textActorLesionStatistics.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
    #   self.textActorLesionStatistics.GetTextProperty().SetFontSize(14)
    #   self.textActorLesionStatistics.GetTextProperty().ShadowOn()
    #   self.textActorLesionStatistics.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )

    #   self.textActorParcellation.UseBorderAlignOff() 
    #   self.textActorParcellation.GetTextProperty().SetFontFamily(4)
    #   self.textActorParcellation.GetTextProperty().SetFontFile("fonts\\RobotoMono-Medium.ttf")
    #   self.textActorParcellation.GetTextProperty().SetFontSize(14)
    #   self.textActorParcellation.GetTextProperty().ShadowOn()
    #   self.textActorParcellation.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
    #   self.textActorParcellation.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    #   self.textActorParcellation.SetPosition(0.01, 1)
    #   self.textActorParcellation.GetTextProperty().SetVerticalJustificationToTop()
    #   self.textActorLesionImpact.SetTextProperty(self.textActorParcellation.GetTextProperty())
    #   self.textActorLesionImpact.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    #   self.textActorLesionImpact.SetPosition(0.01, 1)
      
  def AddData(self):
    #print("Hello add")
    #self.lesionvis.renDualRight.SetActiveCamera(self.lesionvis.renDualLeft.GetActiveCamera())
    self.interactionStyle = CustomLesionInteractorStyle()
    self.interactionStyle.lesionvis = self.lesionvis
    #self.interactionStyleLeft.renderer = self.lesionvis.renDualLeft
    #self.interactionStyleLeft.informationKey = self.lesionvis.informationKey
    #self.interactionStyleLeft.informationKeyID = self.lesionvis.informationUniqueKey
    #self.interactionStyleLeft.actors = self.lesionvis.actors
    #self.interactionStyleLeft.lesionAffectedPointIdsLh = self.lesionvis.lesionAffectedPointIdsLh
    #self.interactionStyleLeft.lesionAffectedPointIdsRh = self.lesionvis.lesionAffectedPointIdsRh
    #self.interactionStyleLeft.SetDefaultRenderer(self.renDualLeft)
    #self.lesionvis.iren_LesionMapDualLeft.SetInteractorStyle(self.interactionStyleLeft)

    #self.interactionStyleRight = LesionMappingInteraction()
    #self.interactionStyleRight.renderer = self.lesionvis.renDualRight
    #print(id(self.lesionvis.renDualRight))
    #self.interactionStyleRight.informationKey = self.lesionvis.informationKey
    #self.interactionStyleRight.informationKeyID = self.lesionvis.informationUniqueKey
    #self.interactionStyleRight.actors = self.lesionvis.actors
    #self.interactionStyleRight.lesionAffectedPointIdsLh = self.lesionvis.lesionAffectedPointIdsLh
    #self.interactionStyleRight.lesionAffectedPointIdsRh = self.lesionvis.lesionAffectedPointIdsRh
    #self.interactionStyleRight.SetDefaultRenderer(self.renDualRight)
    #self.lesionvis.iren_LesionMapDualRight.SetInteractorStyle(self.interactionStyleRight)
    #self.renDualLeft.GetActiveCamera().AddObserver("ModifiedEvent", self.cameraModifiedCallback)
    #self.renDualRight.GetActiveCamera().AddObserver("ModifiedEvent", self.cameraModifiedCallback)
    #self.lesionvis.renDualLeft.AddObserver("EndEvent", self.leftCameraModifiedCallback)
    #self.lesionvis.renDualRight.AddObserver("EndEvent", self.rightCameraModifiedCallback)
    #self.iren_LesionMapDualLeft.Start()
    #self.iren_LesionMapDualRight.Start()
    #self.iren_LesionMapDualLeft.Initialize()
    for actor in self.lesionvis.actors:

        itemType = actor.GetProperty().GetInformation().Get(self.lesionvis.informationKey)
        #lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationUniqueKey)
        if(itemType == None):
            #self.lesionvis.ren2x2.AddActor(actor)
            #actor.GetMapper().ScalarVisibilityOff()
            self.rendererLesion.AddActor(actor)


    ui_path = os.path.dirname(os.path.abspath(__file__))
    fontPath = os.path.join(ui_path, "fonts\\RobotoMono-Medium.ttf")
    self.textActorLesion = vtk.vtkTextActor()
    self.textActorSurface = vtk.vtkTextActor()
    self.textActorRh = vtk.vtkTextActor()
    self.textActorLh = vtk.vtkTextActor()

    self.textActorLesion.UseBorderAlignOn()
    self.textActorLesion.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    self.textActorLesion.SetPosition(0.01, 0.95)
    self.textActorLesion.GetTextProperty().SetFontFamily(4)
    self.textActorLesion.GetTextProperty().SetFontFile(fontPath)
    self.textActorLesion.GetTextProperty().SetFontSize(18)
    self.textActorLesion.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
    self.textActorLesion.GetTextProperty().SetJustificationToLeft()
    self.textActorLesion.SetInput("3D LESIONS")

    self.textActorSurface.UseBorderAlignOn()
    self.textActorSurface.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    self.textActorSurface.SetPosition(0.01, 0.01)
    self.textActorSurface.GetTextProperty().SetFontFamily(4)
    self.textActorSurface.GetTextProperty().SetFontFile(fontPath)
    self.textActorSurface.GetTextProperty().SetFontSize(18)
    self.textActorSurface.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
    self.textActorSurface.GetTextProperty().SetJustificationToLeft()
    self.textActorSurface.SetInput("PIAL SURFACE")

    #self.textActorRh.UseBorderAlignOn()
    self.textActorRh.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    self.textActorRh.SetPosition(0.99, 0.95)
    self.textActorRh.GetTextProperty().SetFontFamily(4)
    self.textActorRh.GetTextProperty().SetFontFile(fontPath)
    self.textActorRh.GetTextProperty().SetFontSize(18)
    self.textActorRh.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
    self.textActorRh.GetTextProperty().SetJustificationToRight()
    self.textActorRh.SetInput("RIGHT HEM")

    #self.textActorLh.UseBorderAlignOn()
    self.textActorLh.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    self.textActorLh.SetPosition(0.99, 0.01)
    self.textActorLh.GetTextProperty().SetFontFamily(4)
    self.textActorLh.GetTextProperty().SetFontFile(fontPath)
    self.textActorLh.GetTextProperty().SetFontSize(18)
    self.textActorLh.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
    self.textActorLh.GetTextProperty().SetJustificationToRight()
    self.textActorLh.SetInput("LEFT HEM")

    self.rendererLesion.AddActor(self.textActorLesion)
    self.rendererSurface.AddActor(self.textActorSurface)
    self.rendererUnfoldedRh.AddActor(self.textActorRh)
    self.rendererUnfoldedLh.AddActor(self.textActorLh)

    pialSurfaceFilePathRh = self.lesionvis.subjectFolder + "\\surfaces\\rh.pial.obj"
    pialSurfaceFilePathLh = self.lesionvis.subjectFolder + "\\surfaces\\lh.pial.obj"
    unfoldedFilePathRh = self.lesionvis.subjectFolder + "\\surfaces\\rh.aparc.annot.pial_unfolded.obj"
    scalarDataPathRh = self.lesionvis.subjectFolder + "\\surfaces\\rh.aparc.annotXMLPolyData.vtp"
    scalarDataPathLh = self.lesionvis.subjectFolder + "\\surfaces\\lh.aparc.annotXMLPolyData.vtp"
    unfoldedFilePathLh = self.lesionvis.subjectFolder +  "\\surfaces\\lh.aparc.annot.pial_unfolded.obj"
    labelFilePathRh = self.lesionvis.subjectFolder +  "\\surfaces\\rh.aparc.annot"
    labelFilePathLh = self.lesionvis.subjectFolder +  "\\surfaces\\lh.aparc.annot"

    # load Rh pial
    pialReaderRh = vtk.vtkOBJReader()
    pialReaderRh.SetFileName(pialSurfaceFilePathRh)
    pialReaderRh.Update()
    pialMapperRh = vtk.vtkOpenGLPolyDataMapper()
    pialMapperRh.SetInputConnection(pialReaderRh.GetOutputPort())
    pialActorRh = vtk.vtkActor()
    pialActorRh.SetMapper(pialMapperRh)

    # load Lh pial
    pialReaderLh = vtk.vtkOBJReader()
    pialReaderLh.SetFileName(pialSurfaceFilePathLh)
    pialReaderLh.Update()
    pialMapperLh = vtk.vtkOpenGLPolyDataMapper()
    pialMapperLh.SetInputConnection(pialReaderLh.GetOutputPort())
    pialActorLh = vtk.vtkActor()
    pialActorLh.SetMapper(pialMapperLh)

    # load unfolded surface Rh
    unfoldReaderRh = vtk.vtkOBJReader()
    unfoldReaderRh.SetFileName(unfoldedFilePathRh)
    unfoldReaderRh.Update()
    unfoldedMapperRh = vtk.vtkOpenGLPolyDataMapper()
    unfoldedMapperRh.SetInputConnection(unfoldReaderRh.GetOutputPort())
    unfoldedActorRh = vtk.vtkActor()
    unfoldedActorRh.SetMapper(unfoldedMapperRh)
    #numberOfPointsRh = unfoldedMapperRh.GetInput().GetNumberOfPoints()
    #print(numberOfPointsRh)

    # load unfolded surface Lh
    unfoldReaderLh = vtk.vtkOBJReader()
    unfoldReaderLh.SetFileName(unfoldedFilePathLh)
    unfoldReaderLh.Update()
    unfoldedMapperLh = vtk.vtkOpenGLPolyDataMapper()
    unfoldedMapperLh.SetInputConnection(unfoldReaderLh.GetOutputPort())
    unfoldedActorLh = vtk.vtkActor()
    unfoldedActorLh.SetMapper(unfoldedMapperLh)
    #numberOfPointsLh = unfoldedMapperLh.GetInput().GetNumberOfPoints()

    # Read scalar data from vtp file. (for coloring 2D unfolded surfaces)
    xmlReaderScalarDataRh = vtk.vtkXMLPolyDataReader()
    xmlReaderScalarDataRh.SetFileName(scalarDataPathRh)
    xmlReaderScalarDataRh.Update()
    xmlReaderScalarDataLh = vtk.vtkXMLPolyDataReader()
    xmlReaderScalarDataLh.SetFileName(scalarDataPathLh)
    xmlReaderScalarDataLh.Update()

    # Color for Rh
    vtk_colorsRh = vtk.vtkUnsignedCharArray()
    vtk_colorsRh.SetNumberOfComponents(3)

    # Color for Lh
    vtk_colorsLh = vtk.vtkUnsignedCharArray()
    vtk_colorsLh.SetNumberOfComponents(3)

    # load annotation data Rh
    labelsRh, ctabRh, regionsRh = freesurfer.read_annot(labelFilePathRh, orig_ids=False)
    metaRh = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regionsRh, ctabRh)))

    # Read annotation data Lh
    labelsLh, ctabLh, regionsLh = freesurfer.read_annot(labelFilePathLh, orig_ids=False)
    metaLh = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regionsLh, ctabLh)))

    pDataRh = xmlReaderScalarDataRh.GetOutput()
    pointCountRh = pDataRh.GetNumberOfPoints()
    labelScalarArrayRh = pDataRh.GetPointData().GetScalars()

    pDataLh = xmlReaderScalarDataLh.GetOutput()
    pointCountLh = pDataLh.GetNumberOfPoints()
    labelScalarArrayLh = pDataLh.GetPointData().GetScalars()

    for index in range(pointCountRh):
        clr = metaRh[labelScalarArrayRh.GetValue(index)]["color"]
        vtk_colorsRh.InsertNextTuple3(clr[0], clr[1], clr[2])
    for index in range(pointCountLh):
        clr = metaLh[labelScalarArrayLh.GetValue(index)]["color"]
        vtk_colorsLh.InsertNextTuple3(clr[0], clr[1], clr[2])

    unfoldedMapperRh.GetInput().GetPointData().SetScalars(vtk_colorsRh)
    unfoldedMapperLh.GetInput().GetPointData().SetScalars(vtk_colorsLh)

    self.rendererSurface.AddActor(pialActorRh)
    self.rendererSurface.AddActor(pialActorLh)
    self.rendererUnfoldedRh.AddActor(unfoldedActorRh)
    self.rendererUnfoldedLh.AddActor(unfoldedActorLh)

    self.imageStyle = vtk.vtkInteractorStyleImage()
    # custom interactor style.
    self.customInteractorStyle = CustomLesionInteractorStyle()
    self.customInteractorStyle.SetDefaultRenderer(self.rendererSurface)
    self.iren_2x2.SetInteractorStyle(self.customInteractorStyle)
    self.iren_2x2.SetRenderWindow(self.vtkWidget2x2.GetRenderWindow())
    self.iren_2x2.Initialize()

    self.customInteractorStyle.iren = self.iren_2x2
    self.customInteractorStyle.rendererTypes = self.rendererTypes
    self.customInteractorStyle.imageStyle = self.imageStyle

    # Add text actors
    # self.lesionvis.renDualLeft.AddActor2D(self.textActorLesionStatistics)
    # self.lesionvis.renDualRight.AddActor2D(self.textActorParcellation)
    # self.lesionvis.renDualLeft.AddActor2D(self.textActorLesionImpact)
    # self.overlayDataMainLeftLesions = {"Lesion ID":"NA", "Voxel Count":"NA", "Centroid":"NA", "Elongation":"NA", "Lesion Perimeter":"NA", "Lesion Spherical Radius":"NA", "Lesion Spherical Perimeter":"NA", "Lesion Flatness":"NA", "Lesion Roundness":"NA"}
    # self.overlayDataMainLeftLesionImpact = {"Lesion ID":"NA", "# Functions":"NA", "Affected Functions" : "NA"}
    # self.overlayDataMainRightParcellationImpact = {"Selected Brain Region:":"NA", "Lesion Influence:":"NA", "Number of Lesions Influencing:":"NA", "Lesion IDs:" : "NA"}
    
    # LesionUtils.setOverlayText(self.overlayDataMainLeftLesions, self.textActorLesionStatistics)
    # LesionUtils.setOverlayText(self.overlayDataMainLeftLesionImpact, self.textActorLesionImpact)
    # LesionUtils.setOverlayText(self.overlayDataMainRightParcellationImpact, self.textActorParcellation)

    # self.interactionStyleLeft.overlayDataMainLeftLesions = self.overlayDataMainLeftLesions
    # self.interactionStyleLeft.overlayDataMainLeftLesionImpact = self.overlayDataMainLeftLesionImpact
    # self.interactionStyleLeft.overlayDataMainRightParcellationImpact = self.overlayDataMainRightParcellationImpact
    # self.interactionStyleLeft.textActorLesionStatistics = self.textActorLesionStatistics
    # self.interactionStyleLeft.textActorLesionImpact = self.textActorLesionImpact
    # self.interactionStyleLeft.textActorParcellation = self.textActorParcellation

    # self.interactionStyleRight.overlayDataMainLeftLesions = self.overlayDataMainLeftLesions
    # self.interactionStyleRight.overlayDataMainLeftLesionImpact = self.overlayDataMainLeftLesionImpact
    # self.interactionStyleRight.overlayDataMainRightParcellationImpact = self.overlayDataMainRightParcellationImpact
    # self.interactionStyleRight.textActorLesionStatistics = self.textActorLesionStatistics
    # self.interactionStyleRight.textActorLesionImpact = self.textActorLesionImpact
    # self.interactionStyleRight.textActorParcellation = self.textActorParcellation

    # self.interactionStyleLeft.labelsRh = self.lesionvis.labelsRh
    # self.interactionStyleLeft.regionsRh = self.lesionvis.regionsRh
    # self.interactionStyleLeft.metaRh = self.lesionvis.metaRh
    # self.interactionStyleLeft.uniqueLabelsRh = self.lesionvis.uniqueLabelsRh
    # self.interactionStyleLeft.areaRh = self.lesionvis.areaRh
    # self.interactionStyleLeft.labelsLh = self.lesionvis.labelsLh
    # self.interactionStyleLeft.regionsLh = self.lesionvis.regionsLh
    # self.interactionStyleLeft.metaLh = self.lesionvis.metaLh
    # self.interactionStyleLeft.uniqueLabelsLh = self.lesionvis.uniqueLabelsLh
    # self.interactionStyleLeft.areaLh = self.lesionvis.areaLh
    # self.interactionStyleLeft.polyDataRh = self.lesionvis.polyDataRh
    # self.interactionStyleLeft.polyDataLh = self.lesionvis.polyDataLh

    # self.interactionStyleRight.labelsRh = self.lesionvis.labelsRh
    # self.interactionStyleRight.regionsRh = self.lesionvis.regionsRh
    # self.interactionStyleRight.metaRh = self.lesionvis.metaRh
    # self.interactionStyleRight.uniqueLabelsRh = self.lesionvis.uniqueLabelsRh
    # self.interactionStyleRight.areaRh = self.lesionvis.areaRh
    # self.interactionStyleRight.labelsLh = self.lesionvis.labelsLh
    # self.interactionStyleRight.regionsLh = self.lesionvis.regionsLh
    # self.interactionStyleRight.metaLh = self.lesionvis.metaLh
    # self.interactionStyleRight.uniqueLabelsLh = self.lesionvis.uniqueLabelsLh
    # self.interactionStyleRight.areaLh = self.lesionvis.areaLh
    # self.interactionStyleRight.polyDataRh = self.lesionvis.polyDataRh
    # self.interactionStyleRight.polyDataLh = self.lesionvis.polyDataLh

    # self.interactionStyleLeft.lesionCentroids = self.lesionvis.lesionCentroids
    # self.interactionStyleLeft.lesionNumberOfPixels = self.lesionvis.lesionNumberOfPixels
    # self.interactionStyleLeft.lesionElongation = self.lesionvis.lesionElongation
    # self.interactionStyleLeft.lesionPerimeter = self.lesionvis.lesionPerimeter
    # self.interactionStyleLeft.lesionSphericalRadius = self.lesionvis.lesionSphericalRadius
    # self.interactionStyleLeft.lesionSphericalPerimeter = self.lesionvis.lesionSphericalPerimeter
    # self.interactionStyleLeft.lesionFlatness = self.lesionvis.lesionFlatness
    # self.interactionStyleLeft.lesionRoundness = self.lesionvis.lesionRoundness

    # self.interactionStyleRight.lesionCentroids = self.lesionvis.lesionCentroids
    # self.interactionStyleRight.lesionNumberOfPixels = self.lesionvis.lesionNumberOfPixels
    # self.interactionStyleRight.lesionElongation = self.lesionvis.lesionElongation
    # self.interactionStyleRight.lesionPerimeter = self.lesionvis.lesionPerimeter
    # self.interactionStyleRight.lesionSphericalRadius = self.lesionvis.lesionSphericalRadius
    # self.interactionStyleRight.lesionSphericalPerimeter = self.lesionvis.lesionSphericalPerimeter
    # self.interactionStyleRight.lesionFlatness = self.lesionvis.lesionFlatness
    # self.interactionStyleRight.lesionRoundness = self.lesionvis.lesionRoundness
    # load precomputed lesion properties
    # self.structureInfoLh = None
    # with open(self.lesionvis.subjectFolder + "\\parcellationLh.json") as fp: 
    #     self.structureInfoLh = json.load(fp)
    # #print(self.structureInfoLh.keys())
    # self.parcellationsLhCount = len(self.structureInfoLh)
    # self.structureInfoRh = None
    # with open(self.lesionvis.subjectFolder + "\\parcellationRh.json") as fp: 
    #     self.structureInfoRh = json.load(fp)
    # self.parcellationsRhCount = len(self.structureInfoRh)

    # self.parcellationAffectedPercentageLh = []
    # self.parcellationLesionInfluenceCountLh = []
    # self.parcellationAssociatedLesionsLh = []
    # for jsonElementIndex in range(self.parcellationsLhCount):
    #     for p in self.structureInfoLh[str(jsonElementIndex)]:
    #         self.parcellationAffectedPercentageLh.append(p["PercentageAffected"])
    #         self.parcellationLesionInfluenceCountLh.append(p["LesionInfluenceCount"])
    #         self.parcellationAssociatedLesionsLh.append(p["AssociatedLesions"])

    # for jsonElementIndex in list(self.structureInfoLh.keys()):
    #     for p in self.structureInfoLh[str(jsonElementIndex)]:
    #         self.parcellationAffectedPercentageLh.append(p["PercentageAffected"])
    #         self.parcellationLesionInfluenceCountLh.append(p["LesionInfluenceCount"])
    #         self.parcellationAssociatedLesionsLh.append(p["AssociatedLesions"])

    # self.parcellationAffectedPercentageRh = []
    # self.parcellationLesionInfluenceCountRh = []
    # self.parcellationAssociatedLesionsRh = []
    # # for jsonElementIndex in range(self.parcellationsRhCount):
    # #     for p in self.structureInfoRh[str(jsonElementIndex)]:
    # #         self.parcellationAffectedPercentageRh.append(p["PercentageAffected"])
    # #         self.parcellationLesionInfluenceCountRh.append(p["LesionInfluenceCount"])
    # #         self.parcellationAssociatedLesionsRh.append(p["AssociatedLesions"])
    # for jsonElementIndex in list(self.structureInfoLh.keys()):
    #     for p in self.structureInfoRh[str(jsonElementIndex)]:
    #         self.parcellationAffectedPercentageRh.append(p["PercentageAffected"])
    #         self.parcellationLesionInfluenceCountRh.append(p["LesionInfluenceCount"])
    #         self.parcellationAssociatedLesionsRh.append(p["AssociatedLesions"])

    # self.interactionStyleLeft.parcellationsLhCount = self.parcellationsLhCount
    # self.interactionStyleLeft.parcellationAffectedPercentageLh = self.parcellationAffectedPercentageLh
    # self.interactionStyleLeft.parcellationLesionInfluenceCountLh = self.parcellationLesionInfluenceCountLh
    # self.interactionStyleLeft.parcellationAssociatedLesionsLh = self.parcellationAssociatedLesionsLh
    # self.interactionStyleLeft.parcellationsRhCount = self.parcellationsRhCount
    # self.interactionStyleLeft.parcellationAffectedPercentageRh = self.parcellationAffectedPercentageRh
    # self.interactionStyleLeft.parcellationLesionInfluenceCountRh = self.parcellationLesionInfluenceCountRh
    # self.interactionStyleLeft.parcellationAssociatedLesionsRh = self.parcellationAssociatedLesionsRh

    # self.interactionStyleRight.parcellationsLhCount = self.parcellationsLhCount
    # self.interactionStyleRight.parcellationAffectedPercentageLh = self.parcellationAffectedPercentageLh
    # self.interactionStyleRight.parcellationLesionInfluenceCountLh = self.parcellationLesionInfluenceCountLh
    # self.interactionStyleRight.parcellationAssociatedLesionsLh = self.parcellationAssociatedLesionsLh
    # self.interactionStyleRight.parcellationsRhCount = self.parcellationsRhCount
    # self.interactionStyleRight.parcellationAffectedPercentageRh = self.parcellationAffectedPercentageRh
    # self.interactionStyleRight.parcellationLesionInfluenceCountRh = self.parcellationLesionInfluenceCountRh
    # self.interactionStyleRight.parcellationAssociatedLesionsRh = self.parcellationAssociatedLesionsRh

    # self.lesionvis.ren2x2.ResetCamera()
    # self.lesionvis.ren2x2.Render()
    self.rendererLesion.ResetCamera()
    self.rendererSurface.ResetCamera()
    self.rendererUnfoldedRh.ResetCamera()
    self.rendererUnfoldedLh.ResetCamera()
    self.rendererLesion.Render()
    self.rendererSurface.Render()
    self.rendererUnfoldedRh.Render()
    self.rendererUnfoldedLh.Render()

  def ClearData(self):
    self.rendererLesion.RemoveAllViewProps()
    self.rendererSurface.RemoveAllViewProps()
    self.rendererUnfoldedRh.RemoveAllViewProps()
    self.rendererUnfoldedLh.RemoveAllViewProps()

  def Refresh(self):
    self.lesionvis.ren2x2.Render()


class CustomLesionInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,parent=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
        self.AddObserver("RightButtonPressEvent",self.rightButtonPressEvent)
        self.AddObserver("MiddleButtonPressEvent",self.middleButtonPressEvent)
        self.AddObserver("MouseWheelForwardEvent",self.mouseWheelForwardEvent)
        self.AddObserver("MouseWheelBackwardEvent",self.mouseWheelBackwardEvent)

        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()

    def mouseWheelForwardEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        renderer = self.iren.FindPokedRenderer(clickPos[0], clickPos[1])
        #print(self.rendererTypes[id(renderer)])
        self.SetDefaultRenderer(renderer)
        self.OnMouseWheelForward()
        return

    def mouseWheelBackwardEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        renderer = self.iren.FindPokedRenderer(clickPos[0], clickPos[1])
        #print(self.rendererTypes[id(renderer)])
        self.SetDefaultRenderer(renderer)
        self.OnMouseWheelBackward()
        return

    def middleButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        renderer = self.iren.FindPokedRenderer(clickPos[0], clickPos[1])
        #print(self.rendererTypes[id(renderer)])
        self.SetDefaultRenderer(renderer)
        self.OnMiddleButtonDown()
        return

    def rightButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        renderer = self.iren.FindPokedRenderer(clickPos[0], clickPos[1])
        #print(self.rendererTypes[id(renderer)])
        self.SetDefaultRenderer(renderer)
        self.OnRightButtonDown()
        return

 
    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        renderer = self.iren.FindPokedRenderer(clickPos[0], clickPos[1])
        print(self.rendererTypes[id(renderer)])
        self.SetDefaultRenderer(renderer)
        if(self.rendererTypes[id(renderer)] == "tbcamera"):
            print("camera")
        else:
            #self.OnLeftButtonDown()
            #self.iren.SetInteractorStyle(self.imageStyle)
            return


        #self.SetDefaultRenderer(renderer)
        #self.renderer = renderer
        

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        
        # get the new
        self.NewPickedActor = picker.GetActor()
        
        # If something was selected
        if self.NewPickedActor:
            # If we picked something before, reset its property
            if self.LastPickedActor:
                self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
    
            
            # Save the property of the picked actor so that we can
            # restore it next time
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
            # Highlight the picked actor by changing its properties
            self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)
            
            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor
        
        self.OnLeftButtonDown()
        return