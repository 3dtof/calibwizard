
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


from PySide import QtCore, QtGui

from models.DepthCameraStreamController import DepthCameraStreamController
from models.DataEngine import DataEngine
from views.DataViewContainer import DataViewContainer
import Voxel
import cv2

import numpy as np

import os

import math

class CalibrationDataCaptureDialog(QtGui.QDialog):
    
  """ Shows the dialog for capturing data used in the wizard

    This code is used to show and capture data. It can save VXL files or png files. 
    
    Args:
        cameraSystem: The camera system used. Generally, Voxel.CameraSystem() for TI cameras
        depthCamera: The depth camera connected to the device
        captureFileName: The name of the file where the captured data is stored
        numberOfFrames: Frames to capture
        
    Returns:
        Data (png or vxl or npy) file containing information about the captured data


  """
  
  def __init__(self, cameraSystem, depthCamera, captureFileName, captureType, numberOfFrames, parent = None, flags = 0):
    super(CalibrationDataCaptureDialog, self).__init__(parent, flags)
    
    self.captureTypes = {
      'phase': ['Phase', self.captureData],
      'amplitude': ['Amplitude', self.captureAmplitude]
    }
    
    self.setMinimumHeight(500)
    self.setMinimumWidth(600)
    
    self.depthCamera = depthCamera
    
    self.depthCameraController = DepthCameraStreamController(cameraSystem, depthCamera)
    self.dataEngine = DataEngine(self.depthCameraController)
    self.dataEngine.disableStatistics()
    
    self.captureType = captureType
    
    if not self.captureTypes.has_key(self.captureType) or not self.depthCamera:
      return
    
    self.captureFileName = captureFileName
    self.numberOfFrames = numberOfFrames
    
    layout = QtGui.QVBoxLayout()
    
    self.setWindowTitle('Data Capture')
    
    self.dataView = DataViewContainer(self.dataEngine, self.captureType, shouldLinkViewBox = False, showFormatMenu = True)
    
    layout.addWidget(self.dataView)
    
    hlayout = QtGui.QHBoxLayout()
    hlayout.addWidget(QtGui.QLabel('Filename: '))
    nameEdit = QtGui.QLineEdit() 
    hlayout.addWidget(nameEdit)
    nameEdit.setText(self.captureFileName)
    nameEdit.setDisabled(True)
    
    layout.addLayout(hlayout)
    
    self.progressBar = QtGui.QProgressBar()
    self.progressBar.setValue(0)
    
    layout.addWidget(self.progressBar)
    
    hlayout = QtGui.QHBoxLayout()
    hlayout.addWidget(QtGui.QLabel('Number of frames to capture: '))
    self.frameCount = QtGui.QSpinBox()
    self.frameCount.setRange(50, 500)
    self.frameCount.setValue(self.numberOfFrames)
    self.frameCount.valueChanged.connect(self.setNumberOfFrames)
    hlayout.addWidget(self.frameCount)

    self.captureButton = QtGui.QPushButton('Capture')
    self.captureButton.pressed.connect(self.startCapture)
    hlayout.addWidget(self.captureButton)
    
    self.cancelButton = QtGui.QPushButton('Cancel')
    self.cancelButton.pressed.connect(self.reject)
    hlayout.addWidget(self.cancelButton)
    
    layout.addLayout(hlayout)
    
    self.setLayout(layout)
    
    self.depthCameraController.start()
    self.captureFrames = False
    self.currentFrameCount = 0
    self.average = None
    self.data = None
    
    self.dataEngine.connectData(self.captureType, self.captureTypes[self.captureType][1], QtCore.Qt.QueuedConnection)
    
  def setNumberOfFrames(self, value):
    self.numberOfFrames = value
    
  @QtCore.Slot(object, object, object)
  def capturePhase(self, id, timestamp, frame):
    if not self.captureFrames:
      return
    
    if self.average is None:
      self.average = np.zeros(self.dataEngine.data['phase'].shape, dtype='complex')
    
    phase = self.dataEngine.data['phase']*np.pi/2048
    self.average += self.dataEngine.data['amplitude']*(np.cos(phase)+1j*np.sin(phase))
    self.currentFrameCount += 1
    self.progressBar.setValue(self.currentFrameCount*100/self.numberOfFrames)
    
    if self.currentFrameCount == self.numberOfFrames:
      self.average /= self.currentFrameCount
      self.average = np.angle(self.average)*(4096/(2*math.pi))
      np.save(self.captureFileName, self.average.T)
      self.stopCapture()
    
  @QtCore.Slot(object, object, object)
  def captureAmplitude(self, id, timestamp, frame):
    if not self.captureFrames:
      return
    
    if self.average is None:
      self.average = np.array(frame, copy = True).astype(float)
    else:
      self.average += np.array(frame)
    
    self.currentFrameCount += 1
    self.progressBar.setValue(self.currentFrameCount*100/self.numberOfFrames)
    
    if self.currentFrameCount == self.numberOfFrames:
      self.average /= self.currentFrameCount
      self.average.clip(0, 255, out = self.average)
      
      cv2.imwrite(self.captureFileName, self.average.transpose().astype(np.uint8))
      
      self.stopCapture()
     
  def captureData(self, id, timestamp, frame):
        if not self.captureFrames:
            return
        if self.depthCamera.isSavingFrameStream():
            self.currentFrameCount +=1
            self.progressBar.setValue(self.currentFrameCount*100/self.numberOfFrames)
        if self.currentFrameCount > self.numberOfFrames:
            self.stopCapture()
        else:
            if not self.depthCamera.saveFrameStream(self.captureFileName):
                QtGui.QMessageBox.critical(self, "Can't save stream", "Cannot save the current stream")
  def startCapture(self):
    self.captureButton.setDisabled(True)
    self.frameCount.setDisabled(True)
    self.average = None
    self.captureFrames = True
    
  def stopCapture(self):
    if self.average is not None:
      self.data = self.average
    self.average = None
    if self.depthCameraController.isRunning():
      self.depthCameraController.stop()
      self.accept()

    self.dataEngine.stop()
    
  # static method to create the dialog and return (date, time, accepted)
  @staticmethod
  def showDialog(cameraSystem, depthCamera, captureFileName, captureType, numberOfFrames, parent = None):
    dialog = CalibrationDataCaptureDialog(cameraSystem, depthCamera, captureFileName, captureType, numberOfFrames, parent)
    result = dialog.exec_()
    
    dialog.stopCapture()
    
    if result == QtGui.QDialog.Accepted:
      return dialog.data
    else:
      return None