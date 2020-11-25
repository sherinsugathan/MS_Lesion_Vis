import os
import sys
import vtk
import LesionUtils
import numpy as np
from nibabel import freesurfer
import json
from PyQt5 import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWebEngineWidgets import  QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject,pyqtSlot,pyqtSignal,QUrl
from PyQt5 import QtCore
import pathlib

class CallHandler(QObject):
    @pyqtSlot(result=str)
    def myHello(self):
        print('call received')
        return 'hello, Python'

class WebEnginePage(QWebEnginePage):

  def acceptNavigationRequest(self, qUrl, requestType, isMainFrame):
    # return True to allow navigation, False to block it
    return True

  def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
    return


class ReportsMapper():
  def __init__(self, lesionvis):
    self.lesionvis = lesionvis
    self.webpage = WebEnginePage()
    self.view = QWebEngineView()
    self.layout = Qt.QVBoxLayout()
    self.layout.addWidget(self.view)
    self.lesionvis.frame_Reports.setLayout(self.layout)

  def AddData(self):
    
    self.channel = QWebChannel()
    self.handler = CallHandler()
    self.channel.registerObject('handler', self.handler)
    self.view.page().setWebChannel(self.channel)
    self.view.loadFinished.connect(self._loadFinish)

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    file_path = os.path.abspath(os.path.join(application_path, "interactionSorry.html"))
    htmlUrl = QUrl.fromLocalFile(file_path)
    self.view.load(QUrl(htmlUrl))
    self.view.show()

  def SaveReport(self):
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    self.PDFPath = "file:///" + os.path.abspath(os.path.join(application_path, "report.pdf"))
    
    self.PDFPath = self.PDFPath.replace('\\', '/')
    QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
    QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
    #self.view = QWebEngineView()
    self.view.setPage(self.webpage)
    self.view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

    #self.layout = Qt.QVBoxLayout()
    #self.layout.addWidget(self.view)
    #self.lesionvis.frame_Reports.setLayout(self.layout)
    self.view.setUrl(QtCore.QUrl(self.PDFPath))
    self.view.show()
    
  def _loadFinish(self, *args, **kwargs):
    # self.view.page().runJavaScript("window.show()")
    #self.view.page().runJavaScript("call_python()")
    #print("qt load finish view.loadFinished.connect(self._loadFinish)")
    pass

  def ClearData(self):
    pass

  def Refresh(self):
    pass



