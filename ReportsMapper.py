import os
import vtk
import LesionUtils
import numpy as np
from nibabel import freesurfer
import json
from PyQt5 import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWebEngineWidgets import  QWebEngineView,QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject,pyqtSlot,pyqtSignal,QUrl

class CallHandler(QObject):
    @pyqtSlot(result=str)
    def myHello(self):
        print('call received')
        return 'hello, Python'

class ReportsMapper():
  def __init__(self, lesionvis):
    self.lesionvis = lesionvis


  def AddData(self):
    self.view = QWebEngineView()
    self.channel = QWebChannel()
    self.handler = CallHandler()
    self.channel.registerObject('handler', self.handler)
    self.view.page().setWebChannel(self.channel)
    self.view.loadFinished.connect(self._loadFinish)
    self.layout = Qt.QVBoxLayout()
    self.layout.addWidget(self.view)
    self.lesionvis.frame_Reports.setLayout(self.layout)
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "interaction.html"))
    htmlUrl = QUrl.fromLocalFile(file_path)
    self.view.load(QUrl(htmlUrl))
    self.view.show()
    
  def _loadFinish(self, *args, **kwargs):
    # self.view.page().runJavaScript("window.show()")
    #self.view.page().runJavaScript("call_python()")
    print("qt load finish view.loadFinished.connect(self._loadFinish)")

  def ClearData(self):
    pass

  def Refresh(self):
    pass



