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

    self.rendererSurface.SetBackground(0.0078,0.0470,0.0196)
    self.rendererLesion.SetBackground(0.0039,0.0196,0.0078)
    self.rendererUnfoldedRh.SetBackground(0.0039,0.0196,0.0078)
    self.rendererUnfoldedLh.SetBackground(0.0078,0.0470,0.0196)

    #self.rendererLesion.SetViewport(xmins[2], ymins[2], xmaxs[2], ymaxs[2])
    #self.rendererSurface.SetViewport(xmins[0], ymins[0], xmaxs[0], ymaxs[0])
    #self.rendererUnfoldedRh.SetViewport(xmins[3], ymins[3], xmaxs[3], ymaxs[3])
    #self.rendererUnfoldedLh.SetViewport(xmins[1], ymins[1], xmaxs[1], ymaxs[1])

    self.rendererUnfoldedLh.SetViewport(xmins[2], ymins[2], xmaxs[2], ymaxs[2])
    self.rendererLesion.SetViewport(xmins[0], ymins[0], xmaxs[0], ymaxs[0])
    self.rendererUnfoldedRh.SetViewport(xmins[3], ymins[3], xmaxs[3], ymaxs[3])
    self.rendererSurface.SetViewport(xmins[1], ymins[1], xmaxs[1], ymaxs[1])

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
    self.rendererTypes = {id(self.rendererLesion):"tbcameraLesion", id(self.rendererSurface):"tbcameraSurface", id(self.rendererUnfoldedRh):"rh", id(self.rendererUnfoldedLh):"lh"}

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
    #self.interactionStyle = CustomLesionInteractorStyle()
    #self.interactionStyle.lesionvis = self.lesionvis
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

    self.textActorLesion.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    self.textActorLesion.SetPosition(0.01, 0.01)
    self.textActorLesion.GetTextProperty().SetFontFamily(4)
    self.textActorLesion.GetTextProperty().SetFontFile(fontPath)
    self.textActorLesion.GetTextProperty().SetFontSize(18)
    self.textActorLesion.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
    self.textActorLesion.GetTextProperty().SetJustificationToLeft()
    self.textActorLesion.SetInput("3D LESIONS")

    self.textActorSurface.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    self.textActorSurface.SetPosition(0.99, 0.01)
    self.textActorSurface.GetTextProperty().SetFontFamily(4)
    self.textActorSurface.GetTextProperty().SetFontFile(fontPath)
    self.textActorSurface.GetTextProperty().SetFontSize(18)
    self.textActorSurface.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
    self.textActorSurface.GetTextProperty().SetJustificationToRight()
    self.textActorSurface.SetInput("PIAL SURFACE")

    self.textActorRh.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    self.textActorRh.SetPosition(0.99, 0.95)
    self.textActorRh.GetTextProperty().SetFontFamily(4)
    self.textActorRh.GetTextProperty().SetFontFile(fontPath)
    self.textActorRh.GetTextProperty().SetFontSize(18)
    self.textActorRh.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
    self.textActorRh.GetTextProperty().SetJustificationToRight()
    self.textActorRh.SetInput("RIGHT HEM")

    self.textActorLh.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    self.textActorLh.SetPosition(0.01, 0.95)
    self.textActorLh.GetTextProperty().SetFontFamily(4)
    self.textActorLh.GetTextProperty().SetFontFile(fontPath)
    self.textActorLh.GetTextProperty().SetFontSize(18)
    self.textActorLh.GetTextProperty().SetColor( 0.3372, 0.7490, 0.4627 )
    self.textActorLh.GetTextProperty().SetJustificationToLeft()
    self.textActorLh.SetInput("LEFT HEM")

    self.rendererLesion.AddActor(self.textActorLesion)
    self.rendererSurface.AddActor(self.textActorSurface)
    self.rendererUnfoldedRh.AddActor(self.textActorRh)
    self.rendererUnfoldedLh.AddActor(self.textActorLh)

    pialSurfaceFilePathRh = self.lesionvis.subjectFolder + "\\surfaces\\rh.inflated.obj"
    pialSurfaceFilePathLh = self.lesionvis.subjectFolder + "\\surfaces\\lh.inflated.obj"
    unfoldedFilePathRh = self.lesionvis.subjectFolder + "\\surfaces\\rh.aparc.annot.pial_unfolded.obj"
    unfoldedFilePathLh = self.lesionvis.subjectFolder +  "\\surfaces\\lh.aparc.annot.pial_unfolded.obj"
    # scalarDataPathRh = self.lesionvis.subjectFolder + "\\surfaces\\rh.aparc.annotXMLPolyData.vtp"
    # scalarDataPathLh = self.lesionvis.subjectFolder + "\\surfaces\\lh.aparc.annotXMLPolyData.vtp"
    scalarDataPathRh = self.lesionvis.subjectFolder + "\\surfaces\\rh.aparc.annotXMLPolyDataLabelAndIndexScalars.vtp"
    scalarDataPathLh = self.lesionvis.subjectFolder + "\\surfaces\\lh.aparc.annotXMLPolyDataLabelAndIndexScalars.vtp"
    
    
    
    labelFilePathRh = self.lesionvis.subjectFolder +  "\\surfaces\\rh.aparc.annot"
    labelFilePathLh = self.lesionvis.subjectFolder +  "\\surfaces\\lh.aparc.annot"

    # load Rh pial
    pialReaderRh = vtk.vtkOBJReader()
    pialReaderRh.SetFileName(pialSurfaceFilePathRh)
    pialReaderRh.Update()
    self.pialMapperRh = vtk.vtkOpenGLPolyDataMapper()
    self.pialMapperRh.SetInputConnection(pialReaderRh.GetOutputPort())
    self.pialActorRh = vtk.vtkActor()
    self.pialActorRh.SetMapper(self.pialMapperRh)
    xminRh = self.pialActorRh.GetBounds()[0]
    xmaxRh = self.pialActorRh.GetBounds()[1]
    #print("RIGHT", self.pialActorRh.GetBounds())

    # load Lh pial
    pialReaderLh = vtk.vtkOBJReader()
    pialReaderLh.SetFileName(pialSurfaceFilePathLh)
    pialReaderLh.Update()
    self.pialMapperLh = vtk.vtkOpenGLPolyDataMapper()
    self.pialMapperLh.SetInputConnection(pialReaderLh.GetOutputPort())
    self.pialActorLh = vtk.vtkActor()
    self.pialActorLh.SetMapper(self.pialMapperLh)
    xminLh = self.pialActorLh.GetBounds()[0]
    xmaxLh = self.pialActorLh.GetBounds()[1]

    boundDiffRh = xmaxRh - xminRh
    boundDiffLh = xmaxLh - xminLh
    xTranslateSurface = 0
    if(boundDiffLh>boundDiffRh):
        xTranslateSurface = boundDiffLh / 2
    else:
        xTranslateSurface = boundDiffRh / 2

    surfaceTransformRh = vtk.vtkTransform()
    surfaceTransformRh.Translate(xTranslateSurface, 0.0, 0.0)
    surfaceTransformLh = vtk.vtkTransform()
    surfaceTransformLh.Translate(-xTranslateSurface, 0.0, 0.0)
    self.pialActorRh.SetUserTransform(surfaceTransformRh)
    self.pialActorLh.SetUserTransform(surfaceTransformLh)
    #print("LEFT", self.pialActorLh.GetBounds())

    # load unfolded surface Rh
    unfoldReaderRh = vtk.vtkOBJReader()
    unfoldReaderRh.SetFileName(unfoldedFilePathRh)
    unfoldReaderRh.Update()
    self.unfoldedMapperRh = vtk.vtkOpenGLPolyDataMapper()
    self.unfoldedMapperRh.SetInputConnection(unfoldReaderRh.GetOutputPort())
    self.unfoldedActorRh = vtk.vtkActor()
    self.unfoldedActorRh.SetMapper(self.unfoldedMapperRh)
    #unfoldedActorRh.GetProperty().SetOpacity(0.5)
    #numberOfPointsRh = unfoldedMapperRh.GetInput().GetNumberOfPoints()
    #print(numberOfPointsRh)

    # load unfolded surface Lh
    unfoldReaderLh = vtk.vtkOBJReader()
    unfoldReaderLh.SetFileName(unfoldedFilePathLh)
    unfoldReaderLh.Update()
    self.unfoldedMapperLh = vtk.vtkOpenGLPolyDataMapper()
    self.unfoldedMapperLh.SetInputConnection(unfoldReaderLh.GetOutputPort())
    self.unfoldedActorLh = vtk.vtkActor()
    self.unfoldedActorLh.SetMapper(self.unfoldedMapperLh)
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
    self.labelsRh, ctabRh, regionsRh = freesurfer.read_annot(labelFilePathRh, orig_ids=False)
    self.metaRh = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regionsRh, ctabRh)))

    # Read annotation data Lh
    self.labelsLh, ctabLh, regionsLh = freesurfer.read_annot(labelFilePathLh, orig_ids=False)
    self.metaLh = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regionsLh, ctabLh)))

    pDataRh = xmlReaderScalarDataRh.GetOutput()
    pDataRh.GetPointData().SetActiveScalars("FSLabels")
    self.pointCountRh = pDataRh.GetNumberOfPoints()
    self.labelScalarArrayRh = pDataRh.GetPointData().GetScalars()

    pDataLh = xmlReaderScalarDataLh.GetOutput()
    pDataLh.GetPointData().SetActiveScalars("FSLabels")
    self.pointCountLh = pDataLh.GetNumberOfPoints()
    self.labelScalarArrayLh = pDataLh.GetPointData().GetScalars()

    pDataRh.GetPointData().SetActiveScalars("VertexIndices")
    pDataLh.GetPointData().SetActiveScalars("VertexIndices")
    self.vertexIdScalarArrayRh = pDataRh.GetPointData().GetScalars()
    self.vertexIdScalarArrayLh = pDataLh.GetPointData().GetScalars()
    print(pDataRh.GetNumberOfPoints())

    self.actualVertexIdsRh = []
    for index in range(self.pointCountRh):
        self.actualVertexIdsRh.append(self.vertexIdScalarArrayRh.GetValue(index))

    self.actualVertexIdsLh = []
    for index in range(self.pointCountLh):
        self.actualVertexIdsLh.append(self.vertexIdScalarArrayLh.GetValue(index))


    for index in range(self.pointCountRh):
        clr = self.metaRh[self.labelScalarArrayRh.GetValue(index)]["color"]
        vtk_colorsRh.InsertNextTuple3(clr[0], clr[1], clr[2])
    for index in range(self.pointCountLh):
        clr = self.metaLh[self.labelScalarArrayLh.GetValue(index)]["color"]
        vtk_colorsLh.InsertNextTuple3(clr[0], clr[1], clr[2])

    self.unfoldedMapperRh.GetInput().GetPointData().SetScalars(vtk_colorsRh)
    self.unfoldedMapperLh.GetInput().GetPointData().SetScalars(vtk_colorsLh)

    self.rendererSurface.AddActor(self.pialActorRh)
    self.rendererSurface.AddActor(self.pialActorLh)
    self.rendererUnfoldedRh.AddActor(self.unfoldedActorRh)
    self.rendererUnfoldedLh.AddActor(self.unfoldedActorLh)

    self.imageStyle = vtk.vtkInteractorStyleImage()
    # custom interactor style.
    self.customInteractorStyle = CustomLesionInteractorStyle()
    self.customInteractorStyle.lesionvis = self.lesionvis
    self.customInteractorStyle.twoDModeMapper = self

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


    def brightenColor(self, clr):
        lightenAddVal = 255 - np.amax(clr)
        if(clr[0] + lightenAddVal <= 255):
            clr[0] = clr[0] + lightenAddVal
        if(clr[1] + lightenAddVal <= 255):
            clr[1] = clr[1] + lightenAddVal
        if(clr[2] + lightenAddVal <= 255):
            clr[2] = clr[2] + lightenAddVal

    # Assign colors to 2D unfolded surface.
    def reColor2D(self, selectedParcellationColorLh = None, selectedParcellationColorRh = None):
        vtk_colorsLh = vtk.vtkUnsignedCharArray()
        vtk_colorsLh.SetNumberOfComponents(3)
        vtk_colorsRh = vtk.vtkUnsignedCharArray()
        vtk_colorsRh.SetNumberOfComponents(3)
        #clrGreen = [161,217,155]
        clrRed = [227,74,51]
        clrParcellationRh = [0,0,0]
        clrParcellationRh = [0,0,0]
        vertexIndexArrayRh = self.twoDModeMapper.actualVertexIdsRh
        vertexIndexArrayLh = self.twoDModeMapper.actualVertexIdsLh
        affectedRh = np.asarray(self.lesionvis.lesionAffectedPointIdsRh[int(self.lesionID)-1])
        affectedLh = np.asarray(self.lesionvis.lesionAffectedPointIdsLh[int(self.lesionID)-1])
        lesionMappingRh = np.isin(vertexIndexArrayRh, affectedRh)
        lesionMappingLh = np.isin(vertexIndexArrayLh, affectedLh)

        for vertexIndex in range(lesionMappingLh.size):
            if(lesionMappingLh[vertexIndex] == True):
                vtk_colorsLh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
            else:
                clrParcellationLh = self.twoDModeMapper.metaLh[self.twoDModeMapper.labelScalarArrayLh.GetValue(vertexIndex)]["color"]
                if(selectedParcellationColorLh != None and selectedParcellationColorLh == clrParcellationLh):
                    self.brightenColor(clrParcellationLh)
                    vtk_colorsLh.InsertNextTuple3(clrParcellationLh[0], clrParcellationLh[1], clrParcellationLh[2])
                    continue
                vtk_colorsLh.InsertNextTuple3(clrParcellationLh[0]/4, clrParcellationLh[1]/4, clrParcellationLh[2]/4)
        self.twoDModeMapper.unfoldedMapperLh.GetInput().GetPointData().SetScalars(vtk_colorsLh)
        
        for vertexIndex in range(lesionMappingRh.size):
            if(lesionMappingRh[vertexIndex]==True):
                vtk_colorsRh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
            else:
                clrParcellationRh = self.twoDModeMapper.metaRh[self.twoDModeMapper.labelScalarArrayRh.GetValue(vertexIndex)]["color"]
                if(selectedParcellationColorRh != None and selectedParcellationColorRh == clrParcellationRh):
                    self.brightenColor(clrParcellationRh)
                    vtk_colorsRh.InsertNextTuple3(clrParcellationRh[0], clrParcellationRh[1], clrParcellationRh[2])
                    continue
                vtk_colorsRh.InsertNextTuple3(clrParcellationRh[0]/4, clrParcellationRh[1]/4, clrParcellationRh[2]/4)
        self.twoDModeMapper.unfoldedMapperRh.GetInput().GetPointData().SetScalars(vtk_colorsRh)

    # Assign colors to 3D unfolded surface.
    def reColor3D(self, selectedParcellationColorLh = None, selectedParcellationColorRh = None):
        vtk_colors3DLh = vtk.vtkUnsignedCharArray()
        vtk_colors3DLh.SetNumberOfComponents(3)
        vtk_colors3DRh = vtk.vtkUnsignedCharArray()
        vtk_colors3DRh.SetNumberOfComponents(3)
        #clrGreen = [161,217,155]
        clrRed = [227,74,51]
        clrParcellationRh = [0,0,0]
        clrParcellationRh = [0,0,0]

        # LESION IMPACT COLOR MAPPING STARTS HERE (3D SURFACE)
        numberOfPointsRh = self.twoDModeMapper.pialMapperRh.GetInput().GetNumberOfPoints()
        numberOfPointsLh = self.twoDModeMapper.pialMapperLh.GetInput().GetNumberOfPoints()
        vertexIndexArrayRh = np.arange(numberOfPointsRh)
        vertexIndexArrayLh = np.arange(numberOfPointsLh)
        affectedRh = np.asarray(self.lesionvis.lesionAffectedPointIdsRh[int(self.lesionID)-1])
        affectedLh = np.asarray(self.lesionvis.lesionAffectedPointIdsLh[int(self.lesionID)-1])
        lesionMappingRh = np.isin(vertexIndexArrayRh, affectedRh)
        lesionMappingLh = np.isin(vertexIndexArrayLh, affectedLh)

        for vertexIndex in range(lesionMappingRh.size):
            if(lesionMappingRh[vertexIndex] == True):
                vtk_colors3DRh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
            else:
                if(self.twoDModeMapper.labelsRh[vertexIndex] == -1):
                    clrParcellationRh = [25,5,25]
                else:
                    clrParcellationRh = self.twoDModeMapper.metaRh[self.twoDModeMapper.labelsRh[vertexIndex]]["color"]
                
                if(selectedParcellationColorRh != None and selectedParcellationColorRh == clrParcellationRh):
                    self.brightenColor(clrParcellationRh)
                    vtk_colors3DRh.InsertNextTuple3(clrParcellationRh[0], clrParcellationRh[1], clrParcellationRh[2])
                    continue
                vtk_colors3DRh.InsertNextTuple3(clrParcellationRh[0]/4, clrParcellationRh[1]/4, clrParcellationRh[2]/4)
        for vertexIndex in range(lesionMappingLh.size):
            if(lesionMappingLh[vertexIndex] == True):
                vtk_colors3DLh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
            else:
                if(self.twoDModeMapper.labelsLh[vertexIndex] == -1):
                    clrParcellationLh = [25,5,25]
                else:
                    clrParcellationLh = self.twoDModeMapper.metaLh[self.twoDModeMapper.labelsLh[vertexIndex]]["color"]
                
                if(selectedParcellationColorLh != None and selectedParcellationColorLh == clrParcellationLh):
                    self.brightenColor(clrParcellationLh)
                    vtk_colors3DLh.InsertNextTuple3(clrParcellationLh[0], clrParcellationLh[1], clrParcellationLh[2])
                    continue
                vtk_colors3DLh.InsertNextTuple3(clrParcellationLh[0]/4, clrParcellationLh[1]/4, clrParcellationLh[2]/4)
        self.twoDModeMapper.pialMapperRh.GetInput().GetPointData().SetScalars(vtk_colors3DRh)
        self.twoDModeMapper.pialMapperLh.GetInput().GetPointData().SetScalars(vtk_colors3DLh)

    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        renderer = self.iren.FindPokedRenderer(clickPos[0], clickPos[1])
        #print(self.rendererTypes[id(renderer)])
        self.SetDefaultRenderer(renderer)

        picker = vtk.vtkPropPicker()
        #picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        picker.Pick(clickPos[0], clickPos[1], 0, renderer)
        
        cellPicker = vtk.vtkCellPicker()
        cellPicker.SetTolerance(0.0005)
        cellPicker.Pick(clickPos[0], clickPos[1], 0, renderer)

        # if current renderer is "Rh"
        if(self.rendererTypes[id(renderer)] == "rh"):
            clr = self.twoDModeMapper.metaRh[self.twoDModeMapper.labelsRh[self.twoDModeMapper.actualVertexIdsRh[cellPicker.GetPointId()]]]["color"]
            self.reColor2D(None, clr)
            self.reColor3D(None, clr)
            self.twoDModeMapper.iren_2x2.Render()
            #self.OnLeftButtonDown()
            return

        # if current renderer is "Lh"
        if(self.rendererTypes[id(renderer)] == "lh"):
            clr = self.twoDModeMapper.metaLh[self.twoDModeMapper.labelsLh[self.twoDModeMapper.actualVertexIdsLh[cellPicker.GetPointId()]]]["color"]
            self.reColor2D(clr, None)
            self.reColor3D(clr, None)
            self.twoDModeMapper.iren_2x2.Render()
            #self.OnLeftButtonDown()
            return

        # if current renderer is "Surface"
        if(self.rendererTypes[id(renderer)] == "tbcameraSurface"):
            print("Surface")
            self.OnLeftButtonDown()
            return

        # Check if current renderer is rendererLesion or rendererSurface
        if(self.rendererTypes[id(renderer)] == "tbcameraLesion"):
            print("camera")
        
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

                self.lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.informationUniqueKey)
                # Highlight the picked actor by changing its properties
                self.NewPickedActor.GetMapper().ScalarVisibilityOff()
                self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                self.NewPickedActor.GetProperty().SetDiffuse(1.0)
                self.NewPickedActor.GetProperty().SetSpecular(0.0)

                vtk_colorsLh = vtk.vtkUnsignedCharArray()
                vtk_colorsLh.SetNumberOfComponents(4)
                vtk_colorsRh = vtk.vtkUnsignedCharArray()
                vtk_colorsRh.SetNumberOfComponents(4)

                clrGreen = [161,217,155]
                clrRed = [227,74,51]
                clrParcellationRh = [0,0,0]
                clrParcellationRh = [0,0,0]

                # LESION IMPACT COLOR MAPPING STARTS HERE (2D)
                self.reColor2D()
                self.reColor3D()
                # vertexIndexArrayRh = self.twoDModeMapper.actualVertexIdsRh
                # vertexIndexArrayLh = self.twoDModeMapper.actualVertexIdsLh
                # affectedRh = np.asarray(self.lesionvis.lesionAffectedPointIdsRh[int(lesionID)-1])
                # affectedLh = np.asarray(self.lesionvis.lesionAffectedPointIdsLh[int(lesionID)-1])
                # lesionMappingRh = np.isin(vertexIndexArrayRh, affectedRh)
                # lesionMappingLh = np.isin(vertexIndexArrayLh, affectedLh)

                # for vertexIndex in range(lesionMappingRh.size):
                #     if(lesionMappingRh[vertexIndex]==True):
                #         vtk_colorsRh.InsertNextTuple4(clrRed[0], clrRed[1], clrRed[2], 255.0)
                #     else:
                #         clrParcellationRh = self.twoDModeMapper.metaRh[self.twoDModeMapper.labelScalarArrayRh.GetValue(vertexIndex)]["color"]
                #         vtk_colorsRh.InsertNextTuple4(clrParcellationRh[0], clrParcellationRh[1], clrParcellationRh[2], 120)

                # for vertexIndex in range(lesionMappingLh.size):
                #     if(lesionMappingLh[vertexIndex] == True):
                #         vtk_colorsLh.InsertNextTuple4(clrRed[0], clrRed[1], clrRed[2], 255.0)
                #     else:
                #         clrParcellationLh = self.twoDModeMapper.metaLh[self.twoDModeMapper.labelScalarArrayLh.GetValue(vertexIndex)]["color"]
                #         vtk_colorsLh.InsertNextTuple4(clrParcellationLh[0], clrParcellationLh[1], clrParcellationLh[2], 120)
                # self.twoDModeMapper.unfoldedMapperRh.GetInput().GetPointData().SetScalars(vtk_colorsRh)
                # self.twoDModeMapper.unfoldedMapperLh.GetInput().GetPointData().SetScalars(vtk_colorsLh)
                # LESION IMPACT COLOR MAPPING ENDS HERE

                # vtk_colors3DLh = vtk.vtkUnsignedCharArray()
                # vtk_colors3DLh.SetNumberOfComponents(3)
                # vtk_colors3DRh = vtk.vtkUnsignedCharArray()
                # vtk_colors3DRh.SetNumberOfComponents(3)

                # # LESION IMPACT COLOR MAPPING STARTS HERE (3D SURFACE)
                # numberOfPointsRh = self.twoDModeMapper.pialMapperRh.GetInput().GetNumberOfPoints()
                # numberOfPointsLh = self.twoDModeMapper.pialMapperLh.GetInput().GetNumberOfPoints()
                # vertexIndexArrayRh = np.arange(numberOfPointsRh)
                # vertexIndexArrayLh = np.arange(numberOfPointsLh)
                # affectedRh = np.asarray(self.lesionvis.lesionAffectedPointIdsRh[int(self.lesionID)-1])
                # affectedLh = np.asarray(self.lesionvis.lesionAffectedPointIdsLh[int(self.lesionID)-1])
                # lesionMappingRh = np.isin(vertexIndexArrayRh, affectedRh)
                # lesionMappingLh = np.isin(vertexIndexArrayLh, affectedLh)

                # for vertexIndex in range(lesionMappingRh.size):
                #     if(lesionMappingRh[vertexIndex] == True):
                #         vtk_colors3DRh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                #     else:
                #         if(self.twoDModeMapper.labelsRh[vertexIndex] == -1):
                #             clrParcellationRh = [25,5,25]
                #         else:
                #             clrParcellationRh = self.twoDModeMapper.metaRh[self.twoDModeMapper.labelsRh[vertexIndex]]["color"]
                #         vtk_colors3DRh.InsertNextTuple3(clrParcellationRh[0]/4, clrParcellationRh[1]/4, clrParcellationRh[2]/4)
                # for vertexIndex in range(lesionMappingLh.size):
                #     if(lesionMappingLh[vertexIndex] == True):
                #         vtk_colors3DLh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                #     else:
                #         if(self.twoDModeMapper.labelsLh[vertexIndex] == -1):
                #             clrParcellationLh = [25,5,25]
                #         else:
                #             clrParcellationLh = self.twoDModeMapper.metaLh[self.twoDModeMapper.labelsLh[vertexIndex]]["color"]
                #         vtk_colors3DLh.InsertNextTuple3(clrParcellationLh[0]/4, clrParcellationLh[1]/4, clrParcellationLh[2]/4)
                # self.twoDModeMapper.pialMapperRh.GetInput().GetPointData().SetScalars(vtk_colors3DRh)
                # self.twoDModeMapper.pialMapperLh.GetInput().GetPointData().SetScalars(vtk_colors3DLh)
                # LESION IMPACT COLOR MAPPING ENDS HERE (3D SURFACE)
            
                # save the last picked actor
                self.LastPickedActor = self.NewPickedActor
            
            self.OnLeftButtonDown()
            return
        else:
            #self.OnLeftButtonDown()
            #self.iren.SetInteractorStyle(self.imageStyle)
            return


        #self.SetDefaultRenderer(renderer)
        #self.renderer = renderer
        

