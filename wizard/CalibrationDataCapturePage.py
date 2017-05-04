
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
import glob
import Voxel
from wizard.CalibrationPage import CalibrationPage
from models.DepthCameraStreamController import DepthCameraStreamController
from models.DataEngine import DataEngine
from views.DataViewContainer import DataViewContainer
import os
             
class CalibrationDataCapturePage(CalibrationPage):
    #Capture Data Only for FlatWall Method: Captures Phase Data Only
    STATE_START = 0
    STATE_NEAR_CAPTURED = 1
    STATE_FAR_CAPTURED = 2
    
    DISTANCE_READONLY = [False, True, True]
    DISTANCE_ENABLED = [True, False, False]
    BUTTON_TEXTS = ["Capture Near View", "Capture Far View", "Calibrate"]
    MESSAGE_TEXTS = {'lens':[
        "Step 1: Point the depth camera flat to a wall. Make sure you only see the flat wall in the camera view below and nothing else. This will be for near view capture (usually about 25cm). Later you'll need to capture far view. Now, for near view click on the capture button to the right.",
        "Step 2: Maintain the depth camera orientation to the flat wall but move it farther away by about 35cm (usually to about 60cm). Make sure you only see the flat wall in the camera view below and nothing else. Now, click on the capture button to the right.",
        "Step 3: Great! You've got both near and far views captured. Now, click on the calibrate button to the right to compute the calibration coefficents."], 
                     'commonPhase': "Point the depth camera flat to a wall. Make sure you only see the flat wall in the camera view below and nothing else.", 
                     'perPixel': 'Point the camera to a vxl and capture data for calculating per pixel offsets.'}
    def __init__(self, calibrationWizard):
        super (CalibrationDataCapturePage, self).__init__()
        self.calibrationWizard = calibrationWizard
        self.setMinimumHeight(200)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.setTitle("Capture Data For Calibration")
        self.setSubTitle("Follow the instructions to save data")
        self.layout = QtGui.QVBoxLayout(self)
        self.nearPhase = None
        self.farPhase = None
        self.currentFrameCount = 0
        self.phaseAverage = None
        self.phaseData = None
        self.captureFrames = False

        
    def setState(self, state):
        self.state = state
        self.calibrateButton.setText(CalibrationDataCapturePage.BUTTON_TEXTS[state])
        self.message.setText(CalibrationDataCapturePage.MESSAGE_TEXTS['lens'][state])
        if self.depthCamera.chipset() == self.calibrationWizard.CHIPSET_CALCULUS:
            self.distance.setReadOnly(CalibrationDataCapturePage.DISTANCE_READONLY[state])
            self.distance.setEnabled(CalibrationDataCapturePage.DISTANCE_ENABLED[state])
        
    def setCenterPoint(self, value = 0):
        self.center = [self.cx.value(), self.cy.value()]
    
    def setNumberOfFrames(self, value):
        self.numberOfFrames = value
        
    def getMousePosition(self, pos):
        p = self.dataView.dataView.imageItem.mapFromScene(pos)
        
        if self.frameSize is not None and self.phaseData is not None:
            if p.x() < 0 or p.x() >= self.frameSize[1] or p.y() < 0 or p.y() >= self.frameSize[0]:
                return
          
            x = int(p.x())
            y = int(p.y())
          
            self.progressText.setText('Current point (%d, %d). Phase = %d'%(x, y, self.phaseData[x, y]))
      
    def reset(self):
        self.setState(CalibrationDataCapturePage.STATE_START)
#         self.calibrationPage.resetCalibrationParameters()
        if self.depthCamera.chipset() == self.calibrationWizard.CHIPSET_CALCULUS:
            self.distance.setValue(25.0)
      
    def calibrate(self):
        if self.state == CalibrationDataCapturePage.STATE_START:
            if not self.setExtraPhaseOffsetInCamera():
                QtGui.QMessageBox.critical(self, 'Extra Phase Offset', 'Failed to set extra phase offset')
                return
          
        if self.state == CalibrationDataCapturePage.STATE_START or self.state == CalibrationDataCapturePage.STATE_NEAR_CAPTURED: # Capture first and second view
            self.captureRunning = True
            self.currentFrameCount = 0
        elif self.state == CalibrationDataCapturePage.STATE_FAR_CAPTURED:
          
            if self.nearPhase is None or self.farPhase is None:
                QtGui.QMessageBox.critical(self, 'Invalid state', 'Cannot calibrate with near and far views captured.')
                return

    def captureData(self, id, timestamp, frame):
        if not self.captureFrames:
            return
        if self.depthCamera.isSavingFrameStream():
            self.currentFrameCount +=1
            self.progressBar.setValue(self.currentFrameCount*100/self.numberOfFrames)
        if self.currentFrameCount > self.numberOfFrames:
            self.stopCapture()
            self.currentFrameCount = 0
        else:
            if not self.depthCamera.saveFrameStream(self.captureFileName):
                QtGui.QMessageBox.critical(self, "Can't save stream", "Cannot save the current stream")    
    
    def initializePage(self, *args, **kwargs):
        hlayout = QtGui.QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignTop)
        self.message = QtGui.QLabel()
        self.message.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.message.setWordWrap(True)
        self.message.setAlignment(QtCore.Qt.AlignTop)
        hlayout.addWidget(self.message)
        self.layout.addLayout(hlayout)
        self.depthCamera = self.calibrationWizard.depthCamera
        self.lensPath =  self.calibrationWizard.profilePath + os.sep + self.depthCamera.name() + os.sep + self.depthCamera.id().split(':')[-1].split(')')[0]
        if not self.lensPath:
            os.makedirs(self.lensPath)
        hlayout = QtGui.QHBoxLayout()
        self.resetButton = QtGui.QPushButton('&Reset')
        self.resetButton.setShortcut('Alt+R')
        self.resetButton.pressed.connect(self.reset)
        self.calibrateButton = QtGui.QPushButton('&Calibrate')
        self.calibrateButton.pressed.connect(self.calibrate)
        self.calibrateButton.setShortcut('Alt+C')
        vlayout = QtGui.QVBoxLayout()
        vlayout.setAlignment(QtCore.Qt.AlignRight)
        vlayout.addWidget(self.calibrateButton)
        vlayout.addWidget(self.resetButton)
        hlayout.addLayout(vlayout)
         
        self.layout.addLayout(hlayout)
         
        r, size = self.calibrationWizard.depthCamera.getMaximumFrameSize()
         
        if not r:
            QtGui.QMessageBox.warning(self, 'Maximum Frame Size', 'Could not get maximum frame size')
            width = 1920
            height = 1080
        else:
            width = size.width
            height = size.height
         
        hlayout = QtGui.QHBoxLayout()
           
        hlayout.addWidget(QtGui.QLabel('Center pixel: cx = '))
        self.cx = QtGui.QSpinBox()
        self.cx.setRange(0, width - 1)
        self.cx.setValue(width/2)
        hlayout.addWidget(self.cx)
        self.cx.valueChanged.connect(self.setCenterPoint)
        hlayout.addWidget(QtGui.QLabel(', cy = '))
        self.cy = QtGui.QSpinBox()
        self.cy.setRange(0, height - 1)
        self.cy.setValue(height/2)
        self.cy.valueChanged.connect(self.setCenterPoint)
        hlayout.addWidget(self.cy)
        hlayout.addStretch()
         
        self.setCenterPoint()
         
        self.extraPhaseOffset = 0
        hlayout.addWidget(QtGui.QLabel('Introduce Phase Offset: '))
        self.phaseOffsetBox = QtGui.QSpinBox()
        self.phaseOffsetBox.setRange(-4095, 4095)
        self.phaseOffsetBox.setValue(self.extraPhaseOffset)
        self.phaseOffsetBox.valueChanged.connect(self.setExtraPhaseOffset)
        hlayout.addWidget(self.phaseOffsetBox)
         
        self.layout.addLayout(hlayout)
         
        hlayout = QtGui.QHBoxLayout()
        self.numberOfFrames = 1000
        hlayout.addWidget(QtGui.QLabel('Number of frames to capture: '))
        self.frameCount = QtGui.QSpinBox()
        self.frameCount.setRange(50, 1000)
        self.frameCount.setValue(self.numberOfFrames)
        self.frameCount.valueChanged.connect(self.setNumberOfFrames)
        hlayout.addWidget(self.frameCount)
        hlayout.addStretch()
         
        r, self.dealiasingEnabled = self.depthCamera.getb('dealias_en')
        r1, self.commonPhaseAdditive = self.depthCamera.getb('phase_corr_add')
         
        if self.depthCamera.chipset() == self.calibrationWizard.CHIPSET_CALCULUS or \
            r and not self.dealiasingEnabled:
            self.updateCommonPhase = True
            hlayout.addWidget(QtGui.QLabel('Camera Distance (near view) from flat wall: '))
           
            self.distance = QtGui.QDoubleSpinBox()
            self.distance.setRange(0.1, 5000)
            self.distance.setSingleStep(0.1)
            self.distance.setValue(25.0)
            self.distance.setDecimals(1)
            hlayout.addWidget(self.distance)
            hlayout.addWidget(QtGui.QLabel('cm'))
        else:
            self.updateCommonPhase = False
        self.layout.addLayout(hlayout)
        
        self.depthCameraController = DepthCameraStreamController(self.calibrationWizard.cameraSystem, self.calibrationWizard.depthCamera)
        self.dataEngine = DataEngine(self.depthCameraController)
        self.dataEngine.disableStatistics()
        
        self.captureRunning = False
        self.dataEngine.connectData("phase", self.captureData, QtCore.Qt.QueuedConnection)
        
        self.dataView = DataViewContainer(self.dataEngine, 'phase', shouldLinkViewBox = False, showFormatMenu = True)
        
        self.layout.addWidget(self.dataView)
        
        self.progressBar = QtGui.QProgressBar()
        self.currentProgressValue = 0
        self.progressBar.setValue(0)
        
        self.layout.addWidget(self.progressBar)
        
        self.progressText = QtGui.QLabel()
        self.layout.addWidget(self.progressText)
        
        self.dataView.dataView.graphicsWidget.scene().sigMouseMoved.connect(self.getMousePosition)
        
        self.setState(CalibrationDataCapturePage.STATE_START)
        self.depthCameraController.start()
    
    def setExtraPhaseOffset(self, value):
        self.extraPhaseOffset = value
    
    def setExtraPhaseOffsetInCamera(self):
        return self.depthCamera.setb('disable_offset_corr', False) and \
            self.depthCamera.seti('phase_corr_1', self.extraPhaseOffset)
#         self.camsys = Voxel.CameraSystem()
#         self.setTitle("Data Capture")
#         self.setSubTitle("Capture Data for calibration")
#         self.vlayout = QtGui.QVBoxLayout(self)
#         
#         self.lensCaptureGroupBox = QtGui.QGroupBox()
#         lensLayout = QtGui.QVBoxLayout()
#         self.lensCaptureGroupBox.setLayout(lensLayout)
#         
#         self.buttonData = ["Capture Near Phase", "Capture Far Phase", "Calibrate"]
#         self
#         
#     def initializePage(self, *args, **kwargs):
#         self.depthCamera = self.calibrationWizard.depthCamera    
#         
#     def captureImage(self):
#         data = CalibrationDataCaptureDialog.showDialog(self.camsys, self.depthCamera, "1.png", 'amplitude', 40)
#         
#         
#     def captureData(self):
#         data = CalibrationDataCaptureDialog.showDialog(self.camsys, self.depthCamera, 'something', 'phase', 100)
#         
    