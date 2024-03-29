#==========================================
# Title:  MS Lesion Visualization Project: Utils
# Author: Sherin Sugathan
# Last Modified Date:   9 Jan 2020
#==========================================

import os
import sys
import vtk
import numpy as np
import time
from datetime import datetime
import SimpleITK as sitk
import time
import json
from nibabel import freesurfer
#from PyQt5.QtCore import QTimer
import pickle
import matplotlib.pyplot as plt
import matplotlib
import pathlib
from PIL import Image

'''
##########################################################################
    For the given path, get the List of all files in the directory tree 
##########################################################################
'''
def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

'''
##########################################################################
    Perform connectivity filter analysis on the algorithm output received from probeFilter.
    Returns: A list of dijoint lesion mappers and the total number of connected components.
##########################################################################
'''
def runLesionConnectivityAnalysis(probeFilterObject):
    connectivityFilter = vtk.vtkPolyDataConnectivityFilter()
    connectivityFilter.SetInputConnection(probeFilterObject.GetOutputPort())
    connectivityFilter.SetExtractionModeToAllRegions()
    connectivityFilter.Update()
    numberOfExtractedRegions = connectivityFilter.GetNumberOfExtractedRegions()
    connectivityFilter.SetExtractionModeToSpecifiedRegions()
    lesionComponentMappers = list()
    idx=0
    while True:
        connectivityFilter.AddSpecifiedRegion(idx)
        connectivityFilter.Update()
        component = vtk.vtkPolyData()
        component.DeepCopy(connectivityFilter.GetOutput())
        if component.GetNumberOfCells() <=0:
            break

        centerOfMassFilter = vtk.vtkCenterOfMass()
        centerOfMassFilter.SetInputData(component)
        centerOfMassFilter.SetUseScalarsAsWeights(False)
        centerOfMassFilter.Update()
        #print(centerOfMassFilter.GetCenter())
        #print(component.GetNumberOfCells())

        mapper = vtk.vtkOpenGLPolyDataMapper()
        mapper.SetInputData(component)
        mapper.SetScalarRange(probeFilterObject.GetOutput().GetScalarRange())
        mapper.Update()
        lesionComponentMappers.append(mapper)
        connectivityFilter.DeleteSpecifiedRegion(idx)
        idx +=1
    return lesionComponentMappers, numberOfExtractedRegions

'''
##########################################################################
    Update overlay text on a specific renderer. (TO BE DEPRECTAED SAFELY)
    Returns: Nothing
##########################################################################
'''
def updateOverlayText(renderWindow, overlayDictionary, overlayGlobalDictionary, overlayTextActor, globalTextActor): 
    overlayText =""
    for key in overlayDictionary.keys():
        overlayText = overlayText + str(key) + ": " + str(overlayDictionary[key]) + "\n"
    overlayTextActor.SetInput(overlayText)
    overlayTextGlobal =""
    for key in overlayGlobalDictionary.keys():
        overlayTextGlobal = overlayTextGlobal + str(key) + ": " + str(overlayGlobalDictionary[key]) + "\n"
    globalTextActor.SetInput(overlayTextGlobal)


'''
##########################################################################
    Update overlay text dictionary.
    Returns: Nothing
##########################################################################
'''
def setOverlayText(overlayDictionary, overlayTextActor): 
    overlayText =""
    for key in overlayDictionary.keys():
        overlayText = overlayText + str(key) + ": " + str(overlayDictionary[key]) + "\n"
    overlayTextActor.SetInput(overlayText)


'''
##########################################################################
    Returns: captureScreen for debug and documentation purposes.
##########################################################################
'''
def captureScreenshot2(renderWindow, modeID): 
    windowToImageFilter = vtk.vtkWindowToImageFilter()
    windowToImageFilter.SetInput(renderWindow)
    windowToImageFilter.SetScale(3,3)
    #windowToImageFilter.SetMagnification(3) #set the resolution of the output image (3 times the current resolution of vtk render window)
    windowToImageFilter.SetInputBufferTypeToRGBA() #also record the alpha (transparency) channel
    windowToImageFilter.ReadFrontBufferOff() # read from the back buffer
    windowToImageFilter.Update()
    curr_time = datetime.now()
    timestr = curr_time.strftime('%H.%M.%S.%f')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    fileName = dir_path + "\\" + timestr + ".png"
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(fileName)
    writer.SetInputConnection(windowToImageFilter.GetOutputPort())
    writer.Write()

'''
##########################################################################
    Capture a screenshot from the main renderer. File gets written with timestamp name.
    Returns: Nothing
##########################################################################
'''
def captureScreenshot(renderWindow, modeID): 
    windowToImageFilter = vtk.vtkWindowToImageFilter()
    windowToImageFilter.SetInput(renderWindow)
    #windowToImageFilter.SetScale(3,3)
    #windowToImageFilter.SetMagnification(3) #set the resolution of the output image (3 times the current resolution of vtk render window)
    windowToImageFilter.SetInputBufferTypeToRGBA() #also record the alpha (transparency) channel
    windowToImageFilter.ReadFrontBufferOff() # read from the back buffer
    windowToImageFilter.Update()

    if getattr(sys, 'frozen', False):
        dir_path = os.path.dirname(sys.executable)
    elif __file__:
        dir_path = os.path.dirname(__file__)

    plt.figure(0)
    curr_time = datetime.now()
    timestr = curr_time.strftime('%H.%M.%S.%f')
    fileName = dir_path + "\\captures\\MPR" + timestr + ".jpg"
    plt.savefig(fileName)

    
    plt.figure(1)
    curr_time = datetime.now()
    timestr = curr_time.strftime('%H.%M.%S.%f')
    fileName = dir_path + "\\captures\\MPR" + timestr + ".jpg"
    plt.savefig(fileName)

    plt.figure(2)
    curr_time = datetime.now()
    timestr = curr_time.strftime('%H.%M.%S.%f')
    fileName = dir_path + "\\captures\\MPR" + timestr + ".jpg"
    plt.savefig(fileName)

    curr_time = datetime.now()
    timestr = curr_time.strftime('%H.%M.%S.%f')
    
    # fileName = dir_path + "\\captures\\" + timestr + ".png"
    # writer = vtk.vtkPNGWriter()
    # writer.SetFileName(fileName)
    # writer.SetInputConnection(windowToImageFilter.GetOutputPort())
    # writer.Write()


    if(modeID == -2):
        timestr = "NOR" + timestr
    if(modeID == -3):
        timestr = "DUA" + timestr
    if(modeID == -4):
        timestr = "2DM" + timestr
    fileName = dir_path +  "\\captures\\" + timestr + ".jpg"
    writer = vtk.vtkJPEGWriter()
    writer.SetFileName(fileName)
    writer.SetInputConnection(windowToImageFilter.GetOutputPort());
    writer.Write()

'''
##########################################################################
    Class for implementing custom interactor for main VR.
##########################################################################
'''
class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,lesionvis,parent=None,iren=None, overlayDataMain=None, textActorLesionStatistics=None, overlayDataGlobal=None, textActorGlobal=None, informationKey = None, informationKeyID = None, lesionSeededFiberTracts=None, sliderA=None, sliderB=None, sliderC=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
        self.AddObserver("LeftButtonReleaseEvent",self.leftButtonReleaseEvent)
        self.AddObserver("MouseMoveEvent", self.mouseMoveEvent)
        self.lesionvis = lesionvis
        self.LastPickedActor = None
        self.NewPickedActor = None
        self.clickedLesionActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.iren = iren
        self.overlayDataMain = overlayDataMain
        self.textActorLesionStatistics = textActorLesionStatistics
        self.overlayDataGlobal = overlayDataGlobal 
        self.textActorGlobal = textActorGlobal
        self.informationKey = informationKey
        self.informationKeyID = informationKeyID
        self.lesionSeededFiberTracts = lesionSeededFiberTracts
        self.sliderA = sliderA
        self.sliderB = sliderB
        self.sliderC = sliderC
        self.MouseMotion = 0
        # self.message = "tick"
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.onTimerEvent)
        

    def addLesionData(self, subjectFolder, lesionCentroids, lesionNumberOfPixels, lesionElongation, lesionPerimeter, lesionSphericalRadius, lesionSphericalPerimeter, lesionFlatness, lesionRoundness, lesionSeededFiberTracts):
        self.lesionCentroids = lesionCentroids
        self.lesionNumberOfPixels = lesionNumberOfPixels
        self.lesionElongation = lesionElongation
        self.lesionPerimeter = lesionPerimeter
        self.lesionSphericalRadius = lesionSphericalRadius
        self.lesionSphericalPerimeter = lesionSphericalPerimeter
        self.lesionFlatness = lesionFlatness
        self.lesionRoundness = lesionRoundness
        self.subjectFolder = subjectFolder
        self.lesionSeededFiberTracts = lesionSeededFiberTracts

    # def onTimerEvent(self):
    #     self.parcellationCurrentActor.RotateY(1)
    #     self.iren.Render()

        # if self.message == "tick":
        #     self.message = "tock"
        #     #self.brodmannTextActor.SetInput("Hello")
        #     #print(self.message)
        #     #self.iren.Render()
        # else:
        #     self.message = "tick"
        #     #self.brodmannTextActor.SetInput("Sherin")
        #     #print(self.message)
        #     #self.iren.Render()
    
    def mapLesionToText(self, lesionID, NewPickedActor):
        self.clickedLesionActor = self.NewPickedActor
        #self.timer.stop()
        if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == True):
            self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renMapOutcome)
        # Highlight the picked actor by changing its properties
        self.NewPickedActor.GetMapper().ScalarVisibilityOff()
        self.NewPickedActor.GetProperty().SetColor(0.4627, 0.4627, 0.9568) # A blueish color.
        self.NewPickedActor.GetProperty().SetDiffuse(1.0)
        self.NewPickedActor.GetProperty().SetSpecular(0.0)

        # centerOfMassFilter = vtk.vtkCenterOfMass()
        # centerOfMassFilter.SetInputData(self.NewPickedActor.GetMapper().GetInput())
        # #print(self.NewPickedActor.GetMapper().GetInput())
        # centerOfMassFilter.SetUseScalarsAsWeights(False)
        # centerOfMassFilter.Update()

        #self.centerOfMass = centerOfMassFilter.GetCenter()
        self.centerOfMass = self.lesionCentroids[int(lesionID)-1][0:3]

        # Get slice numbers for setting the MPRs.
        sliceNumbers = computeSlicePositionFrom3DCoordinates(self.subjectFolder, self.lesionCentroids[int(lesionID)-1][0:3])
    
        # Update sliders based on picked lesion.
        self.sliderA.setValue(sliceNumbers[0])
        self.sliderB.setValue(sliceNumbers[1])
        self.sliderC.setValue(sliceNumbers[2])
        
        self.lesionvis.userPickedLesion = lesionID
        self.overlayDataMain["Lesion ID"] = str(lesionID)
        self.overlayDataMain["Centroid"] = str("{0:.2f}".format(self.centerOfMass[0])) +", " +  str("{0:.2f}".format(self.centerOfMass[1])) + ", " + str("{0:.2f}".format(self.centerOfMass[2]))
        #self.overlayDataMain["Selection Type"] = str(itemType)
        self.overlayDataMain["Voxel Count"] = self.lesionNumberOfPixels[int(lesionID)-1]
        self.overlayDataMain["Elongation"] = "{0:.2f}".format(self.lesionElongation[int(lesionID)-1])
        self.overlayDataMain["Lesion Perimeter"] = "{0:.2f}".format(self.lesionPerimeter[int(lesionID)-1])
        self.overlayDataMain["Lesion Spherical Radius"] = "{0:.2f}".format(self.lesionSphericalRadius[int(lesionID)-1])
        self.overlayDataMain["Lesion Spherical Perimeter"] = "{0:.2f}".format(self.lesionSphericalPerimeter[int(lesionID)-1])
        self.overlayDataMain["Lesion Flatness"] = "{0:.2f}".format(self.lesionFlatness[int(lesionID)-1])
        self.overlayDataMain["Lesion Roundness"] = "{0:.2f}".format(self.lesionRoundness[int(lesionID)-1])
        if (self.lesionSeededFiberTracts == True):
            actorCollection = self.GetDefaultRenderer().GetActors()
            for actor in actorCollection:
                actorName = actor.GetProperty().GetInformation().Get(self.informationKey)
                if(actorName=="structural tracts"):
                    self.GetDefaultRenderer().RemoveActor(actor)

            #lesionPointDataSet = self.rhactor.GetMapper().GetInput()
            lesionPointDataSet = self.NewPickedActor.GetMapper().GetInput()
            streamActor = computeStreamlines(self.subjectFolder, None, self.lesionSphericalRadius[int(lesionID)-1], lesionPointDataSet)
            information = vtk.vtkInformation()
            information.Set(self.informationKey,"structural tracts")
            streamActor.GetProperty().SetInformation(information)
            self.GetDefaultRenderer().AddActor(streamActor)

    def leftButtonReleaseEvent(self,obj,event):
        if(self.MouseMotion == 0):
            clickPos = self.GetInteractor().GetEventPosition()
            picker = vtk.vtkPropPicker()
            picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
            # pointPicker = vtk.vtkPointPicker()
            # pointPicker.SetTolerance(0.0005)
            # pointPicker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
            # worldPosition = pointPicker.GetPickPosition()
            # print(pointPicker.GetPointId())
            self.clickedLesionActor = None
            cellPicker = vtk.vtkCellPicker()
            cellPicker.SetTolerance(0.0005)
            cellPicker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
            #worldPosition = cellPicker.GetPickPosition()
            #print(cellPicker.GetPointId())
            
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

                # Reset view style for all other lesions.
                for actor in self.lesionvis.lesionActors:
                    scenelesionID = actor.GetProperty().GetInformation().Get(self.lesionvis.informationUniqueKey)
                    if(scenelesionID!=lesionID):
                        if(self.lesionvis.pushButton_Discrete.isChecked() == True):
                            actor.GetMapper().ScalarVisibilityOff()
                        else:
                            actor.GetMapper().ScalarVisibilityOn()


                if("lh" in str(itemType) and False):
                    if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == False):
                        self.vtkWidget.GetRenderWindow().AddRenderer(self.renMapOutcome)
                    self.renMapOutcome.RemoveAllViewProps()
                    if(self.labelsLh[cellPicker.GetPointId()] == -1 or cellPicker.GetPointId() == -1):
                        #print("Not a valid point")
                        pass
                    else:
                        clr = self.metaLh[self.labelsLh[cellPicker.GetPointId()]]["color"]
                        self.brodmannTextActor.SetInput(str(self.regionsLh[self.uniqueLabelsLh.tolist().index(self.labelsLh[cellPicker.GetPointId()])].decode('utf-8')) + "\n" + "Normal" + "\n" + str("{0:.2f}".format(self.areaLh[self.uniqueLabelsLh.tolist().index(self.labelsLh[cellPicker.GetPointId()])])))
                        polyDataActor = self.polyDataLh[self.uniqueLabelsLh.tolist().index(self.labelsLh[cellPicker.GetPointId()])]
                        parcellationMapperLh = vtk.vtkOpenGLPolyDataMapper()
                        parcellationMapperLh.SetInputData(polyDataActor)
                        parcellationMapperLh.ScalarVisibilityOn()
                        self.parcellationActorLh = vtk.vtkActor()
                        self.parcellationActorLh.SetMapper(parcellationMapperLh)
                        self.parcellationActorLh.GetProperty().SetColor(clr[0]/255.0, clr[1]/255.0, clr[2]/255.0)
                        self.parcellationActorLh.SetOrigin(self.parcellationActorLh.GetCenter())
                        self.parcellationCurrentActor = self.parcellationActorLh
                        self.renMapOutcome.AddViewProp(self.parcellationActorLh)
                        self.renMapOutcome.AddActor(self.brodmannTextActor)
                        self.renMapOutcome.ResetCamera()
                        #self.timer.start(200)
                if("rh" in str(itemType) and False):
                    if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == False):
                        self.vtkWidget.GetRenderWindow().AddRenderer(self.renMapOutcome)
                    self.renMapOutcome.RemoveAllViewProps()
                    #print("Right")
                    if(self.labelsRh[cellPicker.GetPointId()] == -1 or cellPicker.GetPointId() == -1):
                        #print("Not a valid point")
                        pass
                    else:
                        clr = self.metaRh[self.labelsRh[cellPicker.GetPointId()]]["color"]
                        self.brodmannTextActor.SetInput(str(self.regionsRh[self.uniqueLabelsRh.tolist().index(self.labelsRh[cellPicker.GetPointId()])].decode('utf-8')) + "\n" + "Normal" + "\n" + str("{0:.2f}".format(self.areaRh[self.uniqueLabelsRh.tolist().index(self.labelsRh[cellPicker.GetPointId()])])))
                        polyDataActor = self.polyDataRh[self.uniqueLabelsRh.tolist().index(self.labelsRh[cellPicker.GetPointId()])]
                        parcellationMapperRh = vtk.vtkOpenGLPolyDataMapper()
                        parcellationMapperRh.SetInputData(polyDataActor)
                        parcellationMapperRh.ScalarVisibilityOn()
                        self.parcellationActorRh = vtk.vtkActor()
                        self.parcellationActorRh.SetMapper(parcellationMapperRh)
                        self.parcellationActorRh.GetProperty().SetColor(clr[0]/255.0, clr[1]/255.0, clr[2]/255.0)
                        self.parcellationActorRh.SetOrigin(self.parcellationActorRh.GetCenter())
                        self.parcellationCurrentActor = self.parcellationActorRh
                        self.renMapOutcome.AddViewProp(self.parcellationActorRh)
                        self.renMapOutcome.AddActor(self.brodmannTextActor)
                        self.renMapOutcome.ResetCamera()
                        #self.timer.start(200)
                
                #if itemType==None: # Itemtype is None for lesions. They only have Ids.


                if lesionID!=None and itemType==None:
                    self.mapLesionToText(lesionID, self.NewPickedActor)
                    # self.clickedLesionActor = self.NewPickedActor
                    # #self.timer.stop()
                    # if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == True):
                    #     self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renMapOutcome)
                    # # Highlight the picked actor by changing its properties
                    # self.NewPickedActor.GetMapper().ScalarVisibilityOff()
                    # self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                    # self.NewPickedActor.GetProperty().SetDiffuse(1.0)
                    # self.NewPickedActor.GetProperty().SetSpecular(0.0)

                    # centerOfMassFilter = vtk.vtkCenterOfMass()
                    # centerOfMassFilter.SetInputData(self.NewPickedActor.GetMapper().GetInput())
                    # #print(self.NewPickedActor.GetMapper().GetInput())
                    # centerOfMassFilter.SetUseScalarsAsWeights(False)
                    # centerOfMassFilter.Update()

                    # self.centerOfMass = centerOfMassFilter.GetCenter()

                    # # Get slice numbers for setting the MPRs.
                    # sliceNumbers = computeSlicePositionFrom3DCoordinates(self.subjectFolder, self.centerOfMass)
                    # self.sliderA.setValue(sliceNumbers[2])
                    # self.sliderB.setValue(sliceNumbers[1])
                    # self.sliderC.setValue(sliceNumbers[0])

                    # print("picked lesion")

                    # self.lesionvis.userPickedLesion = lesionID
                    # self.overlayDataMain["Lesion ID"] = str(lesionID)
                    # self.overlayDataMain["Centroid"] = str("{0:.2f}".format(self.centerOfMass[0])) +", " +  str("{0:.2f}".format(self.centerOfMass[1])) + ", " + str("{0:.2f}".format(self.centerOfMass[2]))
                    # #self.overlayDataMain["Selection Type"] = str(itemType)
                    # self.overlayDataMain["Voxel Count"] = self.lesionNumberOfPixels[int(lesionID)-1]
                    # self.overlayDataMain["Elongation"] = "{0:.2f}".format(self.lesionElongation[int(lesionID)-1])
                    # self.overlayDataMain["Lesion Perimeter"] = "{0:.2f}".format(self.lesionPerimeter[int(lesionID)-1])
                    # self.overlayDataMain["Lesion Spherical Radius"] = "{0:.2f}".format(self.lesionSphericalRadius[int(lesionID)-1])
                    # self.overlayDataMain["Lesion Spherical Perimeter"] = "{0:.2f}".format(self.lesionSphericalPerimeter[int(lesionID)-1])
                    # self.overlayDataMain["Lesion Flatness"] = "{0:.2f}".format(self.lesionFlatness[int(lesionID)-1])
                    # self.overlayDataMain["Lesion Roundness"] = "{0:.2f}".format(self.lesionRoundness[int(lesionID)-1])
                    # if (self.lesionSeededFiberTracts == True):
                    #     actorCollection = self.GetDefaultRenderer().GetActors()
                    #     for actor in actorCollection:
                    #         actorName = actor.GetProperty().GetInformation().Get(self.informationKey)
                    #         if(actorName=="structural tracts"):
                    #             self.GetDefaultRenderer().RemoveActor(actor)

                    #     #lesionPointDataSet = self.rhactor.GetMapper().GetInput()
                    #     lesionPointDataSet = self.NewPickedActor.GetMapper().GetInput()
                    #     streamActor = computeStreamlines(self.subjectFolder, self.centerOfMass, self.lesionSphericalRadius[int(lesionID)-1], lesionPointDataSet)
                    #     information = vtk.vtkInformation()
                    #     information.Set(self.informationKey,"structural tracts")
                    #     streamActor.GetProperty().SetInformation(information)
                    #     self.GetDefaultRenderer().AddActor(streamActor)
                else:
                    self.clearTextOverlayLesionStatistics()

                updateOverlayText(self.iren, self.overlayDataMain, self.overlayDataGlobal, self.textActorLesionStatistics, self.textActorGlobal)
                self.iren.Render()
                # save the last picked actor
                self.LastPickedActor = self.NewPickedActor
            else: # no actor picked. Clicked on background.
                self.resetToDefaultViewLesions()
                self.clearTextOverlayLesionStatistics()
                updateOverlayText(self.iren, self.overlayDataMain, self.overlayDataGlobal, self.textActorLesionStatistics, self.textActorGlobal)

        self.OnLeftButtonUp()
        return

    def clearTextOverlayLesionStatistics(self):
        self.overlayDataMain["Lesion ID"] = "NA"
        self.overlayDataMain["Centroid"] = "NA"
        self.overlayDataMain["Voxel Count"] = "NA"
        self.overlayDataMain["Elongation"] = "NA"
        self.overlayDataMain["Lesion Perimeter"] = "NA"
        self.overlayDataMain["Lesion Spherical Radius"] = "NA"
        self.overlayDataMain["Lesion Spherical Perimeter"] = "NA"
        self.overlayDataMain["Lesion Flatness"] = "NA"
        self.overlayDataMain["Lesion Roundness"] = "NA"

    def resetToDefaultViewLesions(self):
        #self.lesionMapper.lesionMappingLh = np.empty(shape=(0))
        #self.lesionMapper.lesionMappingRh = np.empty(shape=(0))
        for actor in self.lesionvis.lesionActors:
            if(self.lesionvis.pushButton_Discrete.isChecked() == True):
                #actor.GetMapper().ScalarVisibilityOff()
                self.lesionvis.updateLesionColorsDiscrete()
                break
                #updateLesionColorsDiscrete()
            else:
                actor.GetMapper().ScalarVisibilityOn()
        self.LastPickedActor = None
        self.clickedLesionActor
        #self.currentLesionID = None
        #self.currentParcellationLabel = None

    def mouseMoveEvent(self,obj,event):
        self.MouseMotion = 1
        self.OnMouseMove()
        return

    def leftButtonPressEvent(self,obj,event):
        self.MouseMotion = 0
        self.OnLeftButtonDown()


'''
##########################################################################
    Compute Lesion Properties using ITK Connected Component Analysis.
    Returns: Connected Component Output Image, filter object.
##########################################################################
'''
def computeLesionProperties(subjectFolder):
    imageLesionMask = sitk.ReadImage(subjectFolder + "\\lesionMask\\Consensus.nii")
    # Binary threshold filter.
    binaryThresholdFilter = sitk.BinaryThresholdImageFilter()
    binaryThresholdFilter.SetOutsideValue(0)
    binaryThresholdFilter.SetInsideValue(1)
    binaryThresholdFilter.SetLowerThreshold(0.8)
    binaryThresholdFilter.SetUpperThreshold(1)
    binaryImage = binaryThresholdFilter.Execute(imageLesionMask)
    # Connected component filter.
    connectedComponentFilter = sitk.ConnectedComponentImageFilter()
    connectedComponentImage = connectedComponentFilter.Execute(binaryImage)
    return connectedComponentImage, connectedComponentFilter

'''
##########################################################################
    Compute streamlines using temperature scalars.
    Returns: Nothing
##########################################################################
'''
def computeStreamlines(subjectFolder, seedCenter = None, seedRadius = None, lesionPointDataSet = None):
    temperatureDataFileName = subjectFolder + "\\heatMaps\\aseg.auto_temperature.nii"
    niftiReaderTemperature = vtk.vtkNIFTIImageReader()
    niftiReaderTemperature.SetFileName(temperatureDataFileName)
    niftiReaderTemperature.Update()
    cellDerivatives = vtk.vtkCellDerivatives()
    cellDerivatives.SetInputConnection(niftiReaderTemperature.GetOutputPort())
    cellDerivatives.Update()
    cellDataToPointData = vtk.vtkCellDataToPointData()
    cellDataToPointData.SetInputConnection(cellDerivatives.GetOutputPort())
    cellDataToPointData.Update()

    # Transform for temperature/gradient data
    QFormMatrixTemperature = niftiReaderTemperature.GetQFormMatrix()
    qFormListTemperature = [0] * 16 #the matrix is 4x4
    QFormMatrixTemperature.DeepCopy(qFormListTemperature, QFormMatrixTemperature)
    transformGradient = vtk.vtkTransform()
    transformGradient.PostMultiply()
    transformGradient.SetMatrix(qFormListTemperature)
    transformGradient.Update()
    
    # Create point source and actor
    # psource = vtk.vtkPointSource()
    # if(seedCenter!=None):
    #     psource.SetNumberOfPoints(500)
    #     psource.SetCenter(seedCenter)
    #     psource.SetRadius(seedRadius)
    # else:
    #     psource.SetNumberOfPoints(500)
    #     psource.SetCenter(127,80,150)
    #     psource.SetRadius(80)
    #pointSourceMapper = vtk.vtkPolyDataMapper()
    #pointSourceMapper.SetInputConnection(psource.GetOutputPort())
    #pointSourceActor = vtk.vtkActor()
    #pointSourceActor.SetMapper(pointSourceMapper)

    # if(seedCenter!=None):
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(cellDataToPointData.GetOutputPort())
    transformFilter.SetTransform(transformGradient)
    transformFilter.Update()

    # Perform stream tracing
    streamers = vtk.vtkStreamTracer()
    streamers.SetInputConnection(transformFilter.GetOutputPort())
    # if(seedCenter!=None):
    #     streamers.SetInputConnection(transformFilter.GetOutputPort())
    # else:
    #     streamers.SetInputConnection(cellDataToPointData.GetOutputPort())
    streamers.SetIntegrationDirectionToForward()
    streamers.SetComputeVorticity(False)
    #streamers.SetSourceConnection(psource.GetOutputPort())
    streamers.SetSourceData(lesionPointDataSet)
    
    # streamers.SetMaximumPropagation(100.0)
    # streamers.SetInitialIntegrationStep(0.05)
    # streamers.SetTerminalSpeed(.51)

    streamers.SetMaximumPropagation(100.0)
    streamers.SetInitialIntegrationStep(0.2)
    streamers.SetTerminalSpeed(.01)
    streamers.Update()
    tubes = vtk.vtkTubeFilter()
    tubes.SetInputConnection(streamers.GetOutputPort())
    tubes.SetRadius(0.5)
    tubes.SetNumberOfSides(3)
    tubes.CappingOn()
    tubes.SetVaryRadius(0)
    lut = vtk.vtkLookupTable()
    lut.SetHueRange(.667, 0.0)
    lut.Build()
    streamerMapper = vtk.vtkPolyDataMapper()
    streamerMapper.SetInputConnection(tubes.GetOutputPort())
    streamerMapper.SetLookupTable(lut)
    streamerActor = vtk.vtkActor()
    streamerActor.SetMapper(streamerMapper)

    
    # if(seedCenter!=None):
    #     pass
    # else:
    #     streamerActor.SetUserTransform(transformGradient)
    streamerMapper.Update()

    # writer = vtk.vtkXMLPolyDataWriter()
    # writer.SetFileName("D:\\streamlines.vtp")
    # writer.SetInputData(tubes.GetOutput())
    # writer.Write()

    # plyWriter = vtk.vtkPLYWriter()
    # plyWriter.SetFileName("D:\\streamlines.ply")
    # plyWriter.SetInputData(tubes.GetOutput())
    # plyWriter.Write()

    return streamerActor

'''
##########################################################################
    Compute transformation matrix for json data
    Returns: JSON data transformation matrix
##########################################################################
'''
def getJsonDataTransformMatrix(subjectFolder):
    mrmlDataFileGradient2 = open (subjectFolder + "\\meta\\mrmlGradient2.txt" , 'r')
    arrayListGradient2 = list(np.asfarray(np.array(mrmlDataFileGradient2.readline().split(",")),float))
    arrayListGradient2[0]= arrayListGradient2[0] * -1 # A flip needed.
    transformMat = np.array(arrayListGradient2)
    matrix= np.reshape(transformMat, (4, 4))
    return matrix


'''
##########################################################################
    Use a color transfer Function to generate the colors in the lookup table.
    See: http://www.vtk.org/doc/nightly/html/classvtkColorTransferFunction.html
    :param: tableSize - The table size
    :return: The lookup table.
##########################################################################
'''
def MakeLUTFromCTF(tableSize):
    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()
    # Green to tan.
    ctf.AddRGBPoint(0.0, 1, 0, 0)
    ctf.AddRGBPoint(0.5, 0.865, 0.865, 0.865)
    ctf.AddRGBPoint(1.0, 0.677, 0.492, 0.093)

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(tableSize)
    lut.Build()

    for i in range(0, tableSize):
        rgb = list(ctf.GetColor(float(i) / tableSize)) + [1]
        lut.SetTableValue(i, rgb)

    return lut

'''
##########################################################################
    Use a color transfer Function to generate the colors in the lookup table.
    See: http://www.vtk.org/doc/nightly/html/classvtkColorTransferFunction.html
    :param: tableSize - The table size
    :return: The lookup table.
##########################################################################
'''
def MakeLUTFromCTFDistance(tableSize):
    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()
    # Green to tan.
    ctf.AddRGBPoint(0.0, 1, 0, 0)
    ctf.AddRGBPoint(0.5, 1, 1, 1)
    ctf.AddRGBPoint(1.0, 0, 1, 0)

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(tableSize)
    lut.Build()

    for i in range(0, tableSize):
        rgb = list(ctf.GetColor(float(i) / tableSize)) + [1]
        lut.SetTableValue(i, rgb)

    return lut

'''
##########################################################################
    Compute colors based on hyper, hyper and iso intensity classifications.
    Returns: None
##########################################################################
'''
def MakeCellData(min, max, colors, polyDataObject):
    '''
    Create the cell data using the colors from the lookup table.
    :param: tableSize - The table size
    :param: lut - The lookup table.
    :param: colors - A reference to a vtkUnsignedCharArray().
    '''
    pointCount = polyDataObject.GetPointData().GetScalars().GetNumberOfTuples()
    for i in range(pointCount):
        val = polyDataObject.GetPointData().GetScalars().GetTuple1(i)
        if(val < min): # HYPO sample
            colors.InsertNextTuple3(255,0,0)
        if(val > min and val < max): # ISO sample
            colors.InsertNextTuple3(255,255,255)
        if(val > max): # HYPER sample
            colors.InsertNextTuple3(0,255,0)

'''
##########################################################################
    Extract lesions by processing labelled lesion mask data.
    Returns: Lesion actors.
##########################################################################
'''
def extractLesions(subjectFolder, labelCount, informationKey, informationKeyID, requestedVisualizationType, lesionAverageIntensity, lesionAverageSurroundingIntensity, lesionRegionNumber, probeLesions=False):
    # Load lesion mask
    niftiReaderLesionMask = vtk.vtkNIFTIImageReader()
    niftiReaderLesionMask.SetFileName(subjectFolder + "\\lesionMask\\ConnectedComponents.nii")
    niftiReaderLesionMask.Update()

    # Read QForm matrix from mask data.
    QFormMatrixMask = niftiReaderLesionMask.GetQFormMatrix()
    qFormListMask = [0] * 16 #the matrix is 4x4
    QFormMatrixMask.DeepCopy(qFormListMask, QFormMatrixMask)

    lesionActors = []
    surface = vtk.vtkDiscreteMarchingCubes()
    surface.SetInputConnection(niftiReaderLesionMask.GetOutputPort())
    for i in range(labelCount):
        surface.SetValue(i,i+1)
    surface.Update()
    #component = vtk.vtkPolyData()
    #component.DeepCopy(surface.GetOutput())

    transform = vtk.vtkTransform()
    transform.Identity()
    transform.SetMatrix(qFormListMask)
    transform.Update()
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(surface.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    # Have a raw lesion surface view.
    if(requestedVisualizationType == "Full Data View - Raw"):
        for i in range(labelCount):
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(transformFilter.GetOutput())
            threshold.ThresholdBetween(i+1,i+1)
            threshold.Update()

            geometryFilter = vtk.vtkGeometryFilter()
            geometryFilter.SetInputData(threshold.GetOutput())
            geometryFilter.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputConnection(geometryFilter.GetOutputPort())
            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(lesionMapper)
            #information = vtk.vtkInformation()
            #information.Set(informationKey,"lesions")
            #lesionActor.GetProperty().SetInformation(information)
            informationID = vtk.vtkInformation()
            informationID.Set(informationKeyID,str(i+1))
            lesionActor.GetProperty().SetInformation(informationID)
            lesionActors.append(lesionActor)

    # Apply probe filtering also.
    if(requestedVisualizationType == "Lesion Colored - Continuous"):
        niftiReader = vtk.vtkNIFTIImageReader()
        niftiReader.SetFileName(subjectFolder + "\\structural\\T1IntensityDifference.nii")
        niftiReader.Update()
        QFormMatrixT1 = niftiReader.GetQFormMatrix() # Read QForm matrix from T1 data.
        qFormListT1 = [0] * 16 #the matrix is 4x4
        QFormMatrixT1.DeepCopy(qFormListT1, QFormMatrixT1)

        volumeTransform = vtk.vtkTransform()
        volumeTransform.SetMatrix(qFormListT1)
        volumeTransform.Update()
        # Set transformation for volume data.
        transformVolume = vtk.vtkTransformFilter()
        transformVolume.SetInputData(niftiReader.GetOutput())
        transformVolume.SetTransform(volumeTransform)
        transformVolume.Update()

        for i in range(labelCount):
            colorData = vtk.vtkUnsignedCharArray()
            colorData.SetName('colors') # Any name will work here.
            colorData.SetNumberOfComponents(3)

            threshold = vtk.vtkThreshold()
            threshold.SetInputData(transformFilter.GetOutput())
            threshold.ThresholdBetween(i+1,i+1)
            threshold.Update()

            geometryFilter = vtk.vtkGeometryFilter()
            geometryFilter.SetInputData(threshold.GetOutput())
            geometryFilter.Update()

            # Apply probeFilter
            probeFilter = vtk.vtkProbeFilter()
            probeFilter.SetSourceConnection(transformVolume.GetOutputPort())
            probeFilter.SetInputData(geometryFilter.GetOutput())
            probeFilter.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputConnection(probeFilter.GetOutputPort())

            MakeCellData(-50, 50, colorData, probeFilter.GetOutput())

            #lesionMapper.SetScalarRange(probeFilter.GetOutput().GetScalarRange())
            lesionMapper.GetInput().GetPointData().SetScalars(colorData)
            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(lesionMapper)
            #information = vtk.vtkInformation()
            #information.Set(informationKey,"lesions")
            #lesionActor.GetProperty().SetInformation(information)
            informationID = vtk.vtkInformation()
            informationID.Set(informationKeyID,str(i+1))
            lesionActor.GetProperty().SetInformation(informationID)
            lesionActors.append(lesionActor)

    # Lesion Colored - Discrete visualization.
    if(requestedVisualizationType == "Lesion Colored - Discrete"):
        mylookupTable = MakeLUTFromCTF(labelCount)
        intensityDifferenceDiscrete = np.subtract(lesionAverageSurroundingIntensity,lesionAverageIntensity)
        for i in range(labelCount):
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(transformFilter.GetOutput())
            threshold.ThresholdBetween(i+1,i+1)
            threshold.Update()

            geometryFilter = vtk.vtkGeometryFilter()
            geometryFilter.SetInputData(threshold.GetOutput())
            geometryFilter.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputConnection(geometryFilter.GetOutputPort())
            lesionMapper.ScalarVisibilityOff()

            myrgb = [0,0,0]
            mylookupTable.GetColor(intensityDifferenceDiscrete[i], myrgb)

            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(lesionMapper)
            lesionActor.GetProperty().SetColor(myrgb[0], myrgb[1], myrgb[2])
            #information = vtk.vtkInformation()
            #information.Set(informationKey,"lesions")
            #lesionActor.GetProperty().SetInformation(information)
            informationID = vtk.vtkInformation()
            informationID.Set(informationKeyID,str(i+1))
            lesionActor.GetProperty().SetInformation(informationID)
            lesionActors.append(lesionActor)

    # Lesion Colored - Distance visualization.
    if(requestedVisualizationType == "Lesion Colored - Distance"):
        mylookupTable = MakeLUTFromCTFDistance(labelCount)
        for i in range(labelCount):
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(transformFilter.GetOutput())
            threshold.ThresholdBetween(i+1,i+1)
            threshold.Update()

            geometryFilter = vtk.vtkGeometryFilter()
            geometryFilter.SetInputData(threshold.GetOutput())
            geometryFilter.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputConnection(geometryFilter.GetOutputPort())
            lesionMapper.ScalarVisibilityOff()

            myrgb = [0,0,0]
            mylookupTable.GetColor(lesionRegionNumber[i], myrgb)

            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(lesionMapper)
            lesionActor.GetProperty().SetColor(myrgb[0], myrgb[1], myrgb[2])
            #information = vtk.vtkInformation()
            #information.Set(informationKey,"lesions")
            #lesionActor.GetProperty().SetInformation(information)
            informationID = vtk.vtkInformation()
            informationID.Set(informationKeyID,str(i+1))
            lesionActor.GetProperty().SetInformation(informationID)
            lesionActors.append(lesionActor)

    return lesionActors

'''
##########################################################################
    Read streamlines multiblockdataset
    dataType = 0 #DTI.
    dataType = 1 #Heat Equation.
    dataType = 2 #Danielsson Distance.
    Returns: streamline actors. (one actor = one lesion)
##########################################################################
'''
def extractStreamlines(subjectFolder, informationKey, dataType):
    if(dataType == 0):
        streamlineDataFilePath = subjectFolder + "\\surfaces\\streamlinesMultiBlockDatasetDTI.xml"
    if(dataType == 1):
        streamlineDataFilePath = subjectFolder + "\\surfaces\\streamlinesMultiBlockDataset.xml"
    if(dataType == 2):
        streamlineDataFilePath = subjectFolder + "\\surfaces\\streamlinesMultiBlockDatasetDanielssonDM.xml"
    reader = vtk.vtkXMLMultiBlockDataReader()
    reader.SetFileName(streamlineDataFilePath)
    reader.Update()

    streamlineActors = []
    mb = reader.GetOutput()
    #print("DATACOUNT" , mb.GetNumberOfBlocks())
    for i in range(mb.GetNumberOfBlocks()):
        polyData = vtk.vtkPolyData.SafeDownCast(mb.GetBlock(i))
        if polyData and polyData.GetNumberOfPoints():
            if(dataType == 0):
                tubeFilter = vtk.vtkTubeFilter()
                tubeFilter.SetInputData(polyData)
                tubeFilter.SetRadius(0.4)
                tubeFilter.SetNumberOfSides(50)
                tubeFilter.Update()
            streamlineMapper = vtk.vtkOpenGLPolyDataMapper()
            
            if(dataType == 0):
                streamlineMapper.SetInputData(tubeFilter.GetOutput())
            if(dataType == 1 or dataType == 2):
                streamlineMapper.SetInputData(polyData)
            streamlineActor = vtk.vtkActor()
            streamlineActor.SetMapper(streamlineMapper)
            streamlineActor.GetMapper().ScalarVisibilityOff()
            streamlineActor.GetProperty().SetColor(1.0,0.0,0.1)
            information = vtk.vtkInformation()
            information.Set(informationKey,"structural tracts")
            streamlineActor.GetProperty().SetInformation(information)
            streamlineActors.append(streamlineActor)
    return streamlineActors

'''
##########################################################################
    Read lesion data and create actors.
    Returns: Lesion actors.
##########################################################################
'''
def extractLesions2(subjectFolder, informationKeyID, smoothingEnabled = True):
    lesionSurfaceDataFilePath = subjectFolder + "\\surfaces\\lesions.vtm"
    mbr = vtk.vtkXMLMultiBlockDataReader()
    mbr.SetFileName(lesionSurfaceDataFilePath)
    mbr.Update()

    lesionActors = []
    mb = mbr.GetOutput()
    # print("DATACOUNT" , mb.GetNumberOfBlocks())
    for i in range(mb.GetNumberOfBlocks()):
        polyData = vtk.vtkPolyData.SafeDownCast(mb.GetBlock(i))
        if polyData and polyData.GetNumberOfPoints():

            # smoothFilter = vtk.vtkSmoothPolyDataFilter()
            # smoothFilter.SetInputData(polyData)
            # smoothFilter.SetNumberOfIterations(5)
            # smoothFilter.SetRelaxationFactor(0.1)
            # smoothFilter.FeatureEdgeSmoothingOff()
            # smoothFilter.BoundarySmoothingOn()
            # smoothFilter.Update()

            # smoothFilter = vtk.vtkSmoothPolyDataFilter()
            # smoothFilter.SetInputData(polyData)
            # smoothFilter.SetNumberOfIterations(80)
            # smoothFilter.SetRelaxationFactor(0.1)
            # smoothFilter.FeatureEdgeSmoothingOn()
            # #smoothFilter.SetEdgeAngle(90)
            # smoothFilter.BoundarySmoothingOn()
            # smoothFilter.Update()

            smoother = vtk.vtkWindowedSincPolyDataFilter()
            #smoother.SetInputConnection(sphereSource->GetOutputPort())
            smoother.SetInputData(polyData)
            smoother.SetNumberOfIterations(8)
            smoother.BoundarySmoothingOff()
            smoother.FeatureEdgeSmoothingOff()
            smoother.SetFeatureAngle(120.0)
            smoother.SetPassBand(.001)
            smoother.NonManifoldSmoothingOn()
            smoother.NormalizeCoordinatesOn()
            smoother.Update()

            normalGenerator = vtk.vtkPolyDataNormals()
            normalGenerator.SetInputData(smoother.GetOutput())
            normalGenerator.ComputePointNormalsOn()
            normalGenerator.ComputeCellNormalsOff()
            normalGenerator.AutoOrientNormalsOn()
            normalGenerator.ConsistencyOn()
            normalGenerator.SplittingOff()
            normalGenerator.Update()

            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            if(smoothingEnabled == True):
                lesionMapper.SetInputData(normalGenerator.GetOutput())
            else:
                lesionMapper.SetInputData(polyData)
            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(lesionMapper)
            informationID = vtk.vtkInformation()
            informationID.Set(informationKeyID,str(i+1))
            lesionActor.GetProperty().SetInformation(informationID)
            lesionActor.GetProperty().SetInterpolationToGouraud()
            #lesionActor.GetProperty().SetInterpolationToPhong()
            lesionActors.append(lesionActor)

    return lesionActors

'''
##########################################################################
    Read a surface and smoothens it.
    Returns: Smoeethened surface.
##########################################################################
'''
def smoothSurface(surfaceActor):
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    #smoother.SetInputConnection(sphereSource->GetOutputPort())
    smoother.SetInputData(surfaceActor.GetMapper().GetInput())
    smoother.SetNumberOfIterations(10)
    smoother.BoundarySmoothingOff()
    smoother.FeatureEdgeSmoothingOff()
    smoother.SetFeatureAngle(120.0)
    smoother.SetPassBand(.001)
    smoother.NonManifoldSmoothingOn()
    smoother.NormalizeCoordinatesOn()
    smoother.Update()

    normalGenerator = vtk.vtkPolyDataNormals()
    normalGenerator.SetInputData(smoother.GetOutput())
    normalGenerator.ComputePointNormalsOn()
    normalGenerator.ComputeCellNormalsOff()
    normalGenerator.AutoOrientNormalsOn()
    normalGenerator.ConsistencyOn()
    normalGenerator.SplittingOff()
    normalGenerator.Update()

    mapper = vtk.vtkOpenGLPolyDataMapper()
    mapper.SetInputData(normalGenerator.GetOutput())
    #lesionActor = vtk.vtkActor()
    surfaceActor.SetMapper(mapper)

'''
#########################[OBSOLETE] NOT IN USE NOW #################################################
    Map colors to loaded lesions. 
    Returns: None.
##########################################################################
'''
def lesionColorMapping(subjectFolder, lesionActors):
    colorFilePath = subjectFolder + "\\surfaces\\colorArrayContT1.pkl"
    loadColorFileAndAssignToLesions(colorFilePath, lesionActors)

'''
##########################################################################
    Read a color file and assign to lesion actors.
    Returns: None.
##########################################################################
'''
def loadColorFileAndAssignToLesions(colorFilePath, lesionActors):
    with open(colorFilePath, "rb") as f:
        colorDataFile = pickle.load(f)
    for i in range(len(colorDataFile)):
        colorData = vtk.vtkUnsignedCharArray()
        colorData.SetName('Colors') # Any name will work here.
        lesionActors[i].GetMapper().GetInput().GetPointData().SetActiveScalars("Colors")
        colorData.SetNumberOfComponents(3)
        #colorData.SetArray(colorDataFile[i], int(colorDataFile[i].size/3), True)
        for j in range(len(colorDataFile[i])):
            colorData.InsertNextTuple3(colorDataFile[i][j][0],colorDataFile[i][j][1],colorDataFile[i][j][2])
        lesionActors[i].GetMapper().ScalarVisibilityOn()
        lesionActors[i].GetMapper().GetInput().GetPointData().SetScalars(colorData)


'''
##########################################################################
    Get lesion IDs that are falling below or equal to a specific threshold value
    Returns: Lesion actor indices.
##########################################################################
'''
def getThresholdLesionIndices(sliderValue, parameterArray, NewMax, NewMin):
    OldMin = 1
    OldMax = 1000
    OldValue = sliderValue
    OldRange = 999
    thresholdValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    removeIndices = []
    for index in range(1, len(parameterArray)+1):
        if (parameterArray[index-1] > thresholdValue):
            removeIndices.append(index)
    return removeIndices

'''
##########################################################################
    Refresh lesion display based on params.
    Returns: Lesion actor indices.
##########################################################################
'''
def filterLesionsAndRender(removeIndices, actorList, informationKeyID, renderer):
    removeIndicesString = [str(i) for i in removeIndices] 
    for actor in actorList:
        if(actor.GetProperty().GetInformation().Get(informationKeyID)!=None): # Check if this is a lesion.
            if(actor.GetProperty().GetInformation().Get(informationKeyID) in removeIndicesString):
                renderer.RemoveActor(actor)
            else:
                renderer.AddActor(actor)
        

'''
##########################################################################
    Compute slide numbers from 3D world coordinates.
    Returns: IJK coordinates (slice positions).
##########################################################################
'''
def computeSlicePositionFrom3DCoordinates(subjectFolder, pt):
    fileNameT1 = str(subjectFolder + "\\structural\\T1.nii")
    # Read T1 data.
    readerT1 = sitk.ImageFileReader()
    readerT1.SetFileName(fileNameT1)
    readerT1.LoadPrivateTagsOn()
    readerT1.ReadImageInformation()
    readerT1.LoadPrivateTagsOn()
    imageT1 = sitk.ReadImage(fileNameT1)
    return imageT1.TransformPhysicalPointToIndex(pt) # Return IJK coordinates

'''
##########################################################################
    Read annotation files from freesurfer.
    Returns: Color arrays for left and right hemispheres.
##########################################################################
'''
def initializeSurfaceAnnotationColors(subjectFolder, rhwhiteMapper, lhwhiteMapper):
    fileNameRhAnnot = str(subjectFolder + "\\surfaces\\rh.aparc.annot")
    fileNameLhAnnot = str(subjectFolder + "\\surfaces\\lh.aparc.annot")
    # Read annotation files.
    labelsRh, ctabRh, regionsRh = freesurfer.read_annot(fileNameRhAnnot, orig_ids=False)
    labelsLh, ctabLh, regionsLh = freesurfer.read_annot(fileNameLhAnnot, orig_ids=False)
    metaRh = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regionsRh, ctabRh)))
    metaLh = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regionsLh, ctabLh)))
    numberOfPointsRh = len(labelsRh)
    numberOfPointsLh = len(labelsLh)
    uniqueLabelsRh = np.unique(labelsRh)
    uniqueLabelsLh = np.unique(labelsLh)

    vertexIdsRh = np.arange(numberOfPointsRh)
    vertexIdsLh = np.arange(numberOfPointsLh)
    listOfSegmentedParcellationVerticesRh = []
    for val in uniqueLabelsRh:
        vertices = vertexIdsRh[labelsRh == val]
        listOfSegmentedParcellationVerticesRh.append(vertices)

    listOfSegmentedParcellationVerticesLh = []
    for val in uniqueLabelsLh:
        vertices = vertexIdsLh[labelsLh == val]
        listOfSegmentedParcellationVerticesLh.append(vertices)

    colorDataRh = vtk.vtkUnsignedCharArray()
    colorDataRh.SetNumberOfComponents(3)
    colorDataRh.SetName("ColorsFreeSurferRh")
    colorDataLh = vtk.vtkUnsignedCharArray()
    colorDataLh.SetNumberOfComponents(3)
    colorDataLh.SetName("ColorsFreeSurferLh")

    colorDataLightRh = vtk.vtkUnsignedCharArray()
    colorDataLightRh.SetNumberOfComponents(3)
    colorDataLightRh.SetNumberOfTuples(numberOfPointsRh)
    colorDataLightRh.SetName("ColorsFreeSurferRh")
    colorDataLightLh = vtk.vtkUnsignedCharArray()
    colorDataLightLh.SetNumberOfComponents(3)
    colorDataLightLh.SetNumberOfTuples(numberOfPointsLh)
    colorDataLightLh.SetName("ColorsFreeSurferLh")

    for index in range(numberOfPointsRh):
        if(labelsRh[index] == -1):
            clr = [25,5,25]
        else:
            clr = metaRh[labelsRh[index]]["color"]
        colorDataRh.InsertNextTuple3(clr[0], clr[1], clr[2])
        colorDataLightRh.SetTuple(index, tintColor([clr[0], clr[1], clr[2]], 0.1))

    for index in range(numberOfPointsLh):
        if(labelsLh[index] == -1):
            clr = [25,5,25]
        else:
            clr = metaLh[labelsLh[index]]["color"]
        colorDataLh.InsertNextTuple3(clr[0], clr[1], clr[2])
        colorDataLightLh.SetTuple(index, tintColor([clr[0], clr[1], clr[2]], 0.1))

    areaRh = {}
    polyDataRh = []
    for i in range(len(listOfSegmentedParcellationVerticesRh)):
        ids = vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        for elem in listOfSegmentedParcellationVerticesRh[i]:
            ids.InsertNextValue(elem)


        selectionNode = vtk.vtkSelectionNode()
        selectionNode.SetFieldType(vtk.vtkSelectionNode.POINT)
        selectionNode.SetContentType(vtk.vtkSelectionNode.INDICES)
        selectionNode.SetSelectionList(ids)
        selectionNode.GetProperties().Set(vtk.vtkSelectionNode.CONTAINING_CELLS(), 1)
        selection = vtk.vtkSelection()
        selection.AddNode(selectionNode)
        extractSelection = vtk.vtkExtractSelection()
        extractSelection.SetInputData(0,rhwhiteMapper.GetInput())
        extractSelection.SetInputData(1, selection)
        extractSelection.Update()

        selected = vtk.vtkUnstructuredGrid()
        selected.ShallowCopy(extractSelection.GetOutput())
        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputData(selected)
        geometryFilter.Update()
        mypolydata = geometryFilter.GetOutput()
        polyDataRh.append(mypolydata)

        measured_polydata = vtk.vtkMassProperties()
        measured_polydata.SetInputData(mypolydata)
        surfaceArea = measured_polydata.GetSurfaceArea()
        areaRh[i] = surfaceArea

    areaLh = {}
    polyDataLh = []
    for i in range(len(listOfSegmentedParcellationVerticesLh)):
        ids = vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        for elem in listOfSegmentedParcellationVerticesLh[i]:
            ids.InsertNextValue(elem)

        selectionNode = vtk.vtkSelectionNode()
        selectionNode.SetFieldType(vtk.vtkSelectionNode.POINT)
        selectionNode.SetContentType(vtk.vtkSelectionNode.INDICES)
        selectionNode.SetSelectionList(ids)
        selectionNode.GetProperties().Set(vtk.vtkSelectionNode.CONTAINING_CELLS(),1)
        selection = vtk.vtkSelection()
        selection.AddNode(selectionNode)
        extractSelection = vtk.vtkExtractSelection()
        extractSelection.SetInputData(0,lhwhiteMapper.GetInput())
        extractSelection.SetInputData(1, selection)
        extractSelection.Update()

        selected = vtk.vtkUnstructuredGrid()
        selected.ShallowCopy(extractSelection.GetOutput())
        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputData(selected)
        geometryFilter.Update()
        mypolydata = geometryFilter.GetOutput()
        polyDataLh.append(mypolydata)

        measured_polydata = vtk.vtkMassProperties()
        measured_polydata.SetInputData(mypolydata)
        surfaceArea = measured_polydata.GetSurfaceArea()
        areaLh[i] = surfaceArea
    
    print("Completed")
    
    return colorDataRh, colorDataLh, colorDataLightRh, colorDataLightLh, labelsRh, labelsLh, regionsRh, regionsLh, metaRh, metaLh, uniqueLabelsRh, uniqueLabelsLh, areaRh, areaLh, polyDataRh, polyDataLh

'''
##########################################################################
    Copy actor properties.
    Returns: propery collection
##########################################################################
'''
def saveActorProperties(actors):
    properties = []
    for actor in actors:
        actorProperty = vtk.vtkProperty()
        actorProperty.DeepCopy(actor.GetProperty())
        properties.append(actorProperty)
    return properties

'''
##########################################################################
    Copy actor sclalar data properties.
    Returns: propery collection
##########################################################################
'''
def saveActorScalarDataProperties(actors):
    properties = []
    scalarDataCollection = []
    for actor in actors:
        #actorProperty = vtk.vtkProperty()
        #actorProperty.DeepCopy(actor.GetProperty())
        scalarDataCollection.append(actor.GetMapper().GetInput().GetPointData().GetScalars())
        properties.append(actor.GetMapper().GetScalarVisibility())
    return properties, scalarDataCollection

'''
##########################################################################
    Apply actor properties from saved property.
    Returns: None
##########################################################################
'''
def restoreActorProperties(actors, properties):
    for index in range(len(properties)):
        actors[index].GetProperty().DeepCopy(properties[index])

'''
##########################################################################
    Apply scalr properties from saved property.
    Returns: None
##########################################################################
'''
def restoreActorScalarDataProperties(actors, properties, scalarDataCollection):
    for index in range(len(properties)):
        #actors[index].GetProperty().DeepCopy(properties[index])
        actors[index].GetMapper().SetScalarVisibility(properties[index])
        actors[index].GetMapper().GetInput().GetPointData().SetScalars(scalarDataCollection[index])

'''
##########################################################################
    Blend MRI volume with mask data using the specified opacity
    Returns: blendedVolume
##########################################################################
'''
def computeVolumeMaskBlend(currentSliceVolume, voxelSpaceCorrectedMask, opacity):
    thresholdFilter = vtk.vtkImageThreshold()
    thresholdFilter.SetInputConnection(voxelSpaceCorrectedMask.GetOutputPort())
    thresholdFilter.ThresholdByUpper(1)
    thresholdFilter.SetInValue(255)
    thresholdFilter.Update()

    thresholdImageCastFilter = vtk.vtkImageCast()
    thresholdImageCastFilter.SetInputData(thresholdFilter.GetOutput())
    thresholdImageCastFilter.SetOutputScalarTypeToShort()
    thresholdImageCastFilter.Update() 

    currentSliceVolumeCastFilter = vtk.vtkImageCast()
    currentSliceVolumeCastFilter.SetInputData(currentSliceVolume.GetOutput())
    currentSliceVolumeCastFilter.SetOutputScalarTypeToShort()
    currentSliceVolumeCastFilter.Update() 

    imgBlender = vtk.vtkImageBlend()
    imgBlender.SetOpacity(0, 0)
    imgBlender.SetOpacity(1, opacity)
    imgBlender.AddInputConnection(currentSliceVolumeCastFilter.GetOutputPort())
    imgBlender.AddInputConnection(thresholdImageCastFilter.GetOutputPort())
    imgBlender.Update()

    return imgBlender



'''
##########################################################################
    Set legend properties based on visualization type(continuous, discrete and distance)
    Returns: Nothing
##########################################################################
'''
def setLegend(legendBox, legend, legendDistance, vis):
    if(vis == "continuous" or vis == "discrete"):
        legend.SetEntryString(0, "HYPO-INTENSE")
        legend.SetEntryString(1, "ISO-INTENSE")
        legend.SetEntryString(2, "HYPER-INTENSE")
        legend.SetEntrySymbol(0, legendBox.GetOutput())
        legend.SetEntrySymbol(1, legendBox.GetOutput())
        legend.SetEntrySymbol(2, legendBox.GetOutput())
        legend.SetEntryColor(0, [103/255,169/255,207/255])
        legend.SetEntryColor(1, [247/255,247/255,247/255])
        legend.SetEntryColor(2, [239/255,138/255,98/255])
        legend.SetPosition(0.9, 0.01)
        legend.SetPosition2(0.1,0.1)
        legend.BoxOff()
        legend.BorderOff()
    if(vis == "distance"):
        legendDistance.SetEntryString(0, "REGION 0")
        legendDistance.SetEntryString(1, "REGION 1")
        legendDistance.SetEntryString(2, "REGION 2")
        legendDistance.SetEntryString(3, "REGION 3")
        legendDistance.SetEntrySymbol(0, legendBox.GetOutput())
        legendDistance.SetEntrySymbol(1, legendBox.GetOutput())
        legendDistance.SetEntrySymbol(2, legendBox.GetOutput())
        legendDistance.SetEntrySymbol(3, legendBox.GetOutput())
        legendDistance.SetEntryColor(0, [254/255,237/255,222/255])
        legendDistance.SetEntryColor(1, [253/255,190/255,133/255])
        legendDistance.SetEntryColor(2, [253/255,141/255,60/255])
        legendDistance.SetEntryColor(3, [217/255,71/255,1/255])   
        legendDistance.SetPosition(0.92, 0.01)     
        legendDistance.SetPosition2(0.08,0.1)
        legendDistance.BoxOff()
        legendDistance.BorderOff()

'''
##########################################################################
    Compute lesion overlay data for the current modality (T1/T2/FLAIR)
    Returns: Nothing
##########################################################################
'''
def computeLesionOverlayData(fileName):
    pass
        
'''
##########################################################################
    extract a lesion overlay for the current slice.
    Returns: Nothing
##########################################################################
'''
def getSliceLesionOverlayActor(voxelCorrectedFileName, resliceImageViewer, mc, plane):
    reader2 = vtk.vtkNIFTIImageReader()
    reader2.SetFileName(voxelCorrectedFileName)
    reader2.Update()

    mc.SetInputConnection(reader2.GetOutputPort())
    mc.SetValue(0, 0.1)
    mc.Update()

    spacing = reader2.GetDataSpacing()
    # lesionMapper = vtk.vtkPolyDataMapper()
    # lesionMapper.SetInputConnection(mc.GetOutputPort())
    # lesionMapper.ScalarVisibilityOff()
    # lesionActor = vtk.vtkActor()
    # lesionActor.SetMapper(lesionMapper)
    # lesionActor.GetProperty().SetOpacity(.2)
    # lesionActor.GetProperty().SetColor(.9, 0, 0)

    #plane = vtk.vtkPlane()
    # plane.SetOrigin(0,0,resliceImageViewer.GetSlice()+.75)
    # plane.SetNormal(0, 0, 1)

    #plane.SetOrigin(planeOrigin)
    #plane.SetNormal(planeNormal)

    cutter = vtk.vtkCutter()
    cutter.SetCutFunction(plane)
    cutter.SetInputConnection(mc.GetOutputPort())
    cutter.Update()

    tubes = vtk.vtkTubeFilter()
    tubes.SetInputConnection(cutter.GetOutputPort())
    tubes.SetRadius(1)
    tubes.SetNumberOfSides(32)
    tubes.CappingOn()

    cutterMapper = vtk.vtkPolyDataMapper()
    cutterMapper.SetInputConnection(tubes.GetOutputPort())
    cutterMapper.Update()

    cutterActor = vtk.vtkActor()
    cutterActor.GetProperty().SetColor(0,1,0)
    cutterActor.SetMapper(cutterMapper)
    return cutterActor

'''
##########################################################################
    Check if data folder contains DTI data
    Returns: True if DTI data present; false otherwise
##########################################################################
'''
def checkForDTIData(subjectFolder):
    return os.path.isdir(subjectFolder + "/fibertracts")

def MakeCellData(min, max, colors, polyDataObject):
    '''
    Create the cell data using the colors from the lookup table.
    :param: tableSize - The table size
    :param: lut - The lookup table.
    :param: colors - A reference to a vtkUnsignedCharArray().
    '''
    pointCount = polyDataObject.GetPointData().GetScalars().GetNumberOfTuples()
    for i in range(pointCount):
        val = polyDataObject.GetPointData().GetScalars().GetTuple1(i)
        if(val < min): # HYPO sample
            colors.InsertNextTuple3(103,169,207)
        if(val >= min and val <= max): # ISO sample
            colors.InsertNextTuple3(247,247,247)
        if(val > max): # HYPER sample
            colors.InsertNextTuple3(239,138,98)

'''
##########################################################################
    Update Color Data Values with new intensity Threshold
    Returns: Nothing
##########################################################################
'''
def updateContinuousColorData(subjectFolder, sliderVal, isDTIDataActive):
    #rootPath = "D:\\OneDrive - University of Bergen\Datasets\\MS_SegmentationChallengeDataset\\"
    #listOfSubjects = ["DTIDATA"]
    #contVolumeFileNames = ["T1IntensityDifference.nii"]
    if(isDTIDataActive == True):
        contVolumeFileNames = ["T1IntensityDifference.nii", "T2IntensityDifference.nii"]
    else:
        contVolumeFileNames = ["T1IntensityDifference.nii", "T2IntensityDifference.nii", "3DFLAIRIntensityDifference.nii"]

    structureInfo = None
    with open(subjectFolder + "\\structure-def3.json") as fp: 
        structureInfo = json.load(fp)
    numberOfLesionElements = len(structureInfo)

    connectedComponentsMaskFile = subjectFolder + "\\lesionMask\\ConnectedComponents.nii"
    # Load lesion mask
    niftiReaderLesionMask = vtk.vtkNIFTIImageReader()
    niftiReaderLesionMask.SetFileName(connectedComponentsMaskFile)
    niftiReaderLesionMask.Update()

    # Read QForm matrix from mask data.
    QFormMatrixMask = niftiReaderLesionMask.GetQFormMatrix()
    qFormListMask = [0] * 16 #the matrix is 4x4
    QFormMatrixMask.DeepCopy(qFormListMask, QFormMatrixMask)

    surface = vtk.vtkDiscreteMarchingCubes()
    surface.SetInputConnection(niftiReaderLesionMask.GetOutputPort())
    for i in range(numberOfLesionElements):
        surface.SetValue(i,i+1)
    surface.Update()

    transform = vtk.vtkTransform()
    transform.Identity()
    transform.SetMatrix(qFormListMask)
    transform.Update()
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(surface.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    for contVolumeFileName in contVolumeFileNames:
        contVolumeFilePath = subjectFolder + "\\structural\\" + contVolumeFileName

        # Read continuous Intensity difference volume file
        # Load T1 volume
        niftiReader = vtk.vtkNIFTIImageReader()
        niftiReader.SetFileName(contVolumeFilePath)
        niftiReader.Update()
        QFormMatrixT1 = niftiReader.GetQFormMatrix() # Read QForm matrix from T1 data.
        qFormListT1 = [0] * 16 #the matrix is 4x4
        QFormMatrixT1.DeepCopy(qFormListT1, QFormMatrixT1)
        volumeTransform = vtk.vtkTransform()
        volumeTransform.SetMatrix(qFormListT1)
        volumeTransform.Update()
        # Set transformation for volume data.
        transformVolume = vtk.vtkTransformFilter()
        transformVolume.SetInputData(niftiReader.GetOutput())
        transformVolume.SetTransform(volumeTransform)
        transformVolume.Update()

        colorList = []
        #intensityDifferenceDiscrete = np.subtract(lesionAverageSurroundingIntensity,lesionAverageIntensity)
        #colorDataDiscrete = vtk.vtkUnsignedCharArray()
        #colorDataDiscrete.SetName('Colors') # Any name will work here.
        #colorDataDiscrete.SetNumberOfComponents(3)
        #MakeCellDataDiscrete(-50, 50, colorDataDiscrete, intensityDifferenceDiscrete)
        #print("NUMBER OF LESIONS", numberOfLesionElements)
        for i in range(numberOfLesionElements):
            colorData = vtk.vtkUnsignedCharArray()
            colorData.SetName('Colors') # Any name will work here.
            colorData.SetNumberOfComponents(3)

            threshold = vtk.vtkThreshold()
            threshold.SetInputData(transformFilter.GetOutput())
            threshold.ThresholdBetween(i+1,i+1)
            threshold.Update()

            geometryFilter = vtk.vtkGeometryFilter()
            geometryFilter.SetInputData(threshold.GetOutput())
            geometryFilter.Update()

            # Apply probeFilter
            probeFilter = vtk.vtkProbeFilter()
            probeFilter.SetSourceConnection(transformVolume.GetOutputPort())
            probeFilter.SetInputData(geometryFilter.GetOutput())
            probeFilter.Update()
            MakeCellData(-sliderVal, sliderVal, colorData, probeFilter.GetOutput()) 
            colorList.append(np.array(colorData))
            
            #multiBlockDataset.SetBlock(i,lesionMapper.GetInput())
            #print(subject, "PROCESSING LESION", i,"/",numberOfLesionElements)
            #print("COLOR list length", colorData.GetNumberOfTuples())

        writeItem = None
        if("T1" in contVolumeFileName):
            writeItem = "T1"
        if("T2" in contVolumeFileName):
            writeItem = "T2"
        if("FLAIR" in contVolumeFileName):
            writeItem = "FLAIR"
        writeContFileName = subjectFolder + "\\surfaces\\colorArrayCont" + writeItem + ".pkl"
        with open(writeContFileName, "wb") as f:
            pickle.dump(colorList, f)

'''
##########################################################################
    UNUSED FUNCTION > REMOVE IF REALLY NOT NEEDED. Update Color Data Values with new intensity Threshold
    Returns: Nothing
##########################################################################
'''
def renderActiveRenderer(lesionvis):
    if(lesionvis.buttonGroupModes.checkedId() == -2): # Normal Mode
        lesionvis.iren.Render()

    if(lesionvis.buttonGroupModes.checkedId() == -3): # Dual Mode
        lesionvis.iren_LesionMapDualLeft.Render()

    if(lesionvis.buttonGroupModes.checkedId() == -4): # 2D Mode
        pass #TODO IMPLEMENT AS NEEDED

    if(lesionvis.buttonGroupModes.checkedId() == -5): # Reports Mode
        pass #TODO IMPLEMENT AS NEEDED

'''
##########################################################################
    Function to read the vtk files that stores signed distance map scalars for every lesion.
    Returns: Polydata objects for both hemispheres.
##########################################################################
'''
def readDistanceMapPolyData(dataFolder):
    fileNameLh = dataFolder + "mappingLh.vtk"
    fileNameRh = dataFolder + "mappingRh.vtk"
    readerLh = vtk.vtkPolyDataReader()
    readerLh.SetFileName(fileNameLh)
    readerLh.Update()
    readerRh = vtk.vtkPolyDataReader()
    readerRh.SetFileName(fileNameRh)
    readerRh.Update()
    return readerLh.GetOutput(), readerRh.GetOutput()

'''
##########################################################################
    Function to check if a folder exists or not. If absent, a folder will be created.
    Returns: None
##########################################################################
'''
def checkAndCreateFolder(folderName):
    if not os.path.exists(folderName):
        os.makedirs(folderName)

'''
##########################################################################
    Apply tint to an existing color.
    Returns: tinted RGB color triplet.
##########################################################################
'''
def tintColor(clr, p=0.5):
    r = 255 - int(p * (255 - clr[0]))
    g = 255 - int(p * (255 - clr[1]))
    b = 255 - int(p * (255 - clr[2]))
    return [r,g,b]

'''
##########################################################################
    Highlight specified actors in the array
    Returns: None
##########################################################################
'''
def highlightActors(actors, informationIDList, informationUniqueKey):
    for actor in actors:
        lesionID = actor.GetProperty().GetInformation().Get(informationUniqueKey)
        actor.GetMapper().ScalarVisibilityOn()
        if int(lesionID) in informationIDList:
            actor.GetMapper().ScalarVisibilityOff()
            actor.GetProperty().SetColor(0.4627, 0.4627, 0.9568) # blueish color.
            actor.GetProperty().SetDiffuse(1.0)
            actor.GetProperty().SetSpecular(0.0)

'''
##########################################################################
    Refresh active Renderer.
    Returns: None
##########################################################################
'''
def refreshActiveRenderer(self):
    if(self.buttonGroupModes.checkedId() == -2): # Normal Mode
        self.iren.Render()

    if(self.buttonGroupModes.checkedId() == -3): # Dual Mode
        self.lesionMapperDual.Refresh()

    if(self.buttonGroupModes.checkedId() == -4): # 2D Mode
        pass # not implemented yet.

    if(self.buttonGroupModes.checkedId() == -5): # Reports Mode
        pass


'''
##########################################################################
    Clear Capture Folder.
    Returns: None
##########################################################################
'''
def clearCaptureFolder():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    imageDir = application_path + "\\captures\\"
    if not os.path.exists(imageDir):
        os.makedirs(imageDir)
    filelist = [ f for f in os.listdir(imageDir) if f.endswith(".jpg") ]
    for f in filelist:
      os.remove(os.path.join(imageDir, f))
