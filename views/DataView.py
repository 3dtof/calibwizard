
 # 
 #
 # Copyright (C) {2017} Texas Instruments Incorporated - http://www.ti.com/ 
 # 
 # 
 #  Redistribution and use in source and binary forms, with or without 
 #  modification, are permitted provided that the following conditions 
 #  are met:
 #
 #    Redistributions of source code must retain the above copyright 
 #    notice, this list of conditions and the following disclaimer.
 #
 #    Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in the 
 #    documentation and/or other materials provided with the   
 #    distribution.
 #
 #    Neither the name of Texas Instruments Incorporated nor the names of
 #    its contributors may be used to endorse or promote products derived
 #    from this software without specific prior written permission.
 #
 #  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
 #  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
 #  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 #  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
 #  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
 #  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
 #  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 #  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 #  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 #  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
 #  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 #
#


from PySide import QtGui, QtCore
import pyqtgraph

import Voxel
import numpy as np

import time

from models.DataQueue import DataQueue

from QxtSpanSlider import QxtSpanSlider

from models.DataEngine import *

class DataViewCommunicator(QtCore.QObject):
  
  setCurrentPoint2D = QtCore.Signal(object)
  
  setShiftClickPoint2D = QtCore.Signal(object)
  
  viewRangeChanged = QtCore.Signal(object, object, object, object) # x1, y1, x2, y2
  
  thresholdsChanged = QtCore.Signal(str, object, object)
  
  def __init__(self, parent = None):
    super(DataViewCommunicator, self).__init__(parent)

class DataView(QtGui.QWidget):
  
  dataEnqueued = QtCore.Signal()
  
  communicator = DataViewCommunicator() # Static object for communication from and to DataView instances
  
  LinkedViewBoxes = {}
  
  def __init__(self, dataEngine, dataFormat, parent = None):
    super(DataView, self).__init__(parent)
    
    self.dataFormat = None
    self.dataEngine = dataEngine
    
    self.dataQueue = DataQueue()
    
    DataView.setDataFormat(self, dataFormat)
    
    self.dataEnqueued.connect(self.displayData, QtCore.Qt.QueuedConnection)
    
    self.spanKeyModifier = None
    
    self.statusBar = None
    
  @QtCore.Slot(object, object, object)
  def queueData(self, id, timestamp, frame):
    self.dataQueue.put(frame)
    self.dataEnqueued.emit()
      
  def setDataFormat(self, dataFormat):
    self.disconnectData()
    
    self.dataFormat = dataFormat
    self.dataEngine.connectData(self.dataFormat.name, self.queueData, QtCore.Qt.QueuedConnection)

  def disconnectData(self):
    if self.dataFormat:
      self.dataEngine.disconnectData(self.dataFormat.name, self.queueData)

  def cleanup(self):
    self.unlink()
    self.disconnectData()
      
  def setStatusBar(self, statusBar):
    self.statusBar = statusBar
    
  @staticmethod
  def updateViewBoxLinks():
    if len(DataView.LinkedViewBoxes) == 1:
      v = DataView.LinkedViewBoxes.values()[0]
      v.setXLink(None)
      v.setYLink(None)
      return
    
    v = DataView.LinkedViewBoxes.values()
    
    for i in range(0, len(DataView.LinkedViewBoxes) - 1):
      v[i].setXLink(v[-1])
      v[i].setYLink(v[-1])
      
  ## link() and unlink() are used to synchronize mouse/keyboard events between multiple viewboxes
  def link(self, viewBox):
    DataView.LinkedViewBoxes[self] = viewBox
    
    #print "Number of viewboxes = ", len(DataView.LinkedViewBoxes)    
    DataView.updateViewBoxLinks()
      
  def unlink(self):
    if self in DataView.LinkedViewBoxes:
      del DataView.LinkedViewBoxes[self]
      print "Number of viewboxes = ", len(DataView.LinkedViewBoxes)
      DataView.updateViewBoxLinks()
    
  # Implement in derived class
  @QtCore.Slot()
  def displayData(self):
    pass
    
  @staticmethod
  def getDataView(dataFormat, dataEngine, parent = None):
    if dataFormat.dataType == DataFormat.DATA_2D:
      return DataView2D(dataEngine, dataFormat, parent = parent)
#     else:
#       return DataView3D(dataEngine, dataFormat, parent = parent)
    
  def setSpanKeyModifier(self, m):
    self.spanKeyModifier = m
    
  def keyPressEvent(self, ev):
    if self.spanKeyModifier is not None and not ev.modifiers() & self.spanKeyModifier:
      ev.ignore()
      return
    
    if ev.key() == QtCore.Qt.Key_Left:
      self.spanSlider.setSliderDown(True)
      if ev.modifiers() & QtCore.Qt.ShiftModifier:
        self.spanSlider.setUpperPosition(self.spanSlider.upperPosition - self.spanSlider.singleStep())
      else:
        self.spanSlider.setLowerPosition(self.spanSlider.lowerPosition - self.spanSlider.singleStep())
      self.spanSlider.setSliderDown(False)
      ev.accept()
    elif ev.key() == QtCore.Qt.Key_Right:
      self.spanSlider.setSliderDown(True)
      if ev.modifiers() & QtCore.Qt.ShiftModifier:
        self.spanSlider.setUpperPosition(self.spanSlider.upperPosition + self.spanSlider.singleStep())
      else:
        self.spanSlider.setLowerPosition(self.spanSlider.lowerPosition + self.spanSlider.singleStep())
      self.spanSlider.setSliderDown(False)
      ev.accept()
    elif ev.key() == QtCore.Qt.Key_Down:
      self.spanSlider.setSliderDown(True)
      if ev.modifiers() & QtCore.Qt.ShiftModifier:
        self.spanSlider.setUpperPosition(self.spanSlider.upperPosition - self.spanSlider.pageStep())
      else:
        self.spanSlider.setLowerPosition(self.spanSlider.lowerPosition - self.spanSlider.pageStep())
      self.spanSlider.setSliderDown(False)
      ev.accept()
    elif ev.key() == QtCore.Qt.Key_Up:
      self.spanSlider.setSliderDown(True)
      if ev.modifiers() & QtCore.Qt.ShiftModifier:
        self.spanSlider.setUpperPosition(self.spanSlider.upperPosition + self.spanSlider.pageStep())
      else:
        self.spanSlider.setLowerPosition(self.spanSlider.lowerPosition + self.spanSlider.pageStep())
      self.spanSlider.setSliderDown(False)
      ev.accept()
    else:
      super(DataView, self).keyPressEvent(ev)


from DataView2D import DataView2D
# from DataView3D import DataView3D