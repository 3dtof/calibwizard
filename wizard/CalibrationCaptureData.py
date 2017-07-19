
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
import os
from calibration.FlatWallLensCalib import flatWallLensCalibration
from calibration.CommonPhaseOffsetRawDataSimpleAverage import commonPhaseOffset
from calibration.PerPixelOffset import perPixelOffset
from models.DataEngine import DataEngine
from models.DepthCameraStreamController import DepthCameraStreamController
from views.DataViewContainer import DataViewContainer
from CalibrationPage import CalibrationPage
import Voxel

class CalibrationDataCapturePage(CalibrationPage):
    """This code is used for live capture
    
     This code  captures data and calibrates, saving files into the profile path. Profile path = /path/to/.Voxel/profiles. """
    STATE_START = 0
    STATE_NEAR_CAPTURED = 1
    STATE_FAR_CAPTURED = 2
    STATE_COMMON_PHASE_CAPTURED = 3
    STATE_PER_PIXEL_CAPTURED = 4
    STRATEGY = 'FlatWall'
    BUTTON_TEXTS = {'lens':["Capture Far View", "Capture Near View","Capture Common Phase OFfset Data", "Capture Per Pixel Data", "Calibrate"], 
                    'commonPhase': ["Capture Phase Data", "Capture Phase Data for Second Modulation Frequency","Capture Per Pixel Offset Data", "Calibrate"], 
                    'perPixel': ["Capture Pixel Data", "Calibrate"]}
    
    MESSAGE_TEXTS = {'lens':[
        "Point the depth camera flat to a wall. Make sure you only see the flat wall in the camera view below and nothing else. This will be for far view capture. Later you'll need to capture near view. Now, for far view click on the capture button.",
        "Maintain the depth camera orientation to the flat wall but move it closer. Make sure you only see the flat wall in the camera view below and nothing else. Now, click on the capture button to the right.", 
        "Capture Data for Common Phase and Per Pixel Offset Calculation. ",
         "Capture Data for Per Pixel Offset Calculation", 
         "Great! You've got all views captured. Now, click on the calibrate button to compute the calibration coefficents."], 
                     'commonPhase': ["Point the depth camera flat to a wall. Make sure you only see the flat wall in the camera view below and nothing else.",
                                     "dealias_en is turned on. Please click on capture to record data with the second modulation frequency.",
                                     "Capture Data for Per Pixel Offset Calculation",
                                     "All views captured. Click on calibrate to calibrate"], 
                     'perPixel': ['Point the camera to a flat wall and capture data for calculating per pixel offsets.',
                                "Great! you have all the data captured. CLick on calibrate. "]}
    def __init__(self, calibrationWizard):
        super (CalibrationDataCapturePage, self).__init__()
        self.calibrationWizard = calibrationWizard
        self.setTitle("Capture Data and Calibrate Using Depth Camera")
        self.setSubTitle("Please Follow the instructions to calibrate the camera")
        self.layout = QtGui.QVBoxLayout(self)
        self.captureGroupBox = QtGui.QGroupBox("Data Capture")
        self.layout.addWidget(self.captureGroupBox)
        self.dataView = None
        self.progressBar = None
        self.progressText = None
        self.hlayout = None
        self.dataEngine = None
        self.depthCameraController = None
        self.lensCaptured = False
        self.farCaptured = False
        self.nearCaptured = False
        self.commonPhaseCaptured = False
        self.perPixelCaptured = False
        self.nearFileName = None
        self.farFileName = None
        self.commonPhaseFileName = None
        self.perPixelFileName = None
        self.complete = False
        self.state = CalibrationDataCapturePage.STATE_START
        #layouts for groupboxes
        captureLayout = QtGui.QVBoxLayout()
        self.captureGroupBox.setLayout(captureLayout)
        hlayout = QtGui.QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignTop)
        self.message = QtGui.QLabel()
        self.message.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.message.setWordWrap(True)
        self.message.setAlignment(QtCore.Qt.AlignTop)
        hlayout.addWidget(self.message)
        captureLayout.addLayout(hlayout)
        self.captureButton = QtGui.QPushButton()
        captureLayout.addWidget(self.captureButton)
        self.captureButton.clicked.connect(self.captureDataAndCalibrate)
        self.paramsGroupBox = None    
        self.paramsText = ''
        
    def initializePage(self, *args, **kwargs):
        self.depthCamera = self.calibrationWizard.depthCamera
        self.calibrations = []
        for calibration in self.calibrationWizard.calibs:
            if self.calibrationWizard.calibs[calibration] == CalibrationDataCapturePage.STRATEGY:
                self.calibrations.append(calibration)
        if 'lens' in self.calibrations:
            self.calibrationToDo = 'lens'
            self.buttonTexts = CalibrationDataCapturePage.BUTTON_TEXTS['lens']
            self.messageTexts = CalibrationDataCapturePage.MESSAGE_TEXTS['lens']
        elif 'commonPhase' in self.calibrations:
            self.calibrationToDo = 'commonPhase'
            self.buttonTexts = CalibrationDataCapturePage.BUTTON_TEXTS['commonPhase']
            self.messageTexts = CalibrationDataCapturePage.MESSAGE_TEXTS['commonPhase']
        elif 'perPixel' in self.calibrations:
            self.calibrationToDo = 'perPixel'
            self.buttonTexts =  CalibrationDataCapturePage.BUTTON_TEXTS['perPixel']
            self.messageTexts = CalibrationDataCapturePage.MESSAGE_TEXTS['perPixel']
        self.captureButton.setText(self.buttonTexts[0])
        self.message.setText(self.messageTexts[0])
        
        if not self.hlayout:
            self.hlayout = QtGui.QHBoxLayout()
            self.numberOfFrames = 100
            self.hlayout.addWidget(QtGui.QLabel('Number of frames to capture: '))
            self.frameCount = QtGui.QSpinBox()
            self.frameCount.setRange(50, 1000)
            self.frameCount.setValue(self.numberOfFrames)
            self.frameCount.valueChanged.connect(self.setNumberOfFrames)
            self.hlayout.addWidget(self.frameCount)
            self.hlayout.addStretch()
             
            self.hlayout.addWidget(QtGui.QLabel(' Distance from flat wall: '))
           
            self.distance = QtGui.QDoubleSpinBox()
            self.distance.setRange(0.1, 5000)
            self.distance.setSingleStep(0.1)
            self.distance.setValue(25.0)
            self.distanceValue = self.distance.value()
            self.distance.setDecimals(1)
            self.distance.valueChanged.connect(self.setDistance)
            self.hlayout.addWidget(self.distance)
            self.hlayout.addWidget(QtGui.QLabel('cm'))
            self.layout.addLayout(self.hlayout)
        if not self.dataEngine:   
            self.depthCameraController = DepthCameraStreamController(self.calibrationWizard.cameraSystem, self.calibrationWizard.depthCamera)
            self.dataEngine = DataEngine(self.depthCameraController)
            self.dataEngine.disableStatistics()
        
        self.captureRunning = False
        self.dataEngine.connectData("phase", self.captureData, QtCore.Qt.QueuedConnection)
        if not self.dataView:
            self.dataView = DataViewContainer(self.dataEngine, 'phase', shouldLinkViewBox = False, showFormatMenu = True)
            self.layout.addWidget(self.dataView)
        
        if not self.progressBar:
            self.progressBar = QtGui.QProgressBar()
            self.currentProgressValue = 0
            self.progressBar.setValue(0)
            
            self.layout.addWidget(self.progressBar)
        if not self.progressText:
            self.progressText = QtGui.QLabel()
            self.layout.addWidget(self.progressText)
        
        if not self.paramsGroupBox:
            self.paramsGroupBox = QtGui.QGroupBox("Calibration Parameters")
        vlayout = QtGui.QVBoxLayout()
        self.paramsGroupBox.setLayout(vlayout)
        self.paramsLabel = QtGui.QLabel()
        vlayout.addWidget(self.paramsLabel) 
        self.paramsGroupBox.hide()
        self.layout.addWidget(self.paramsGroupBox)
        
        self.depthCameraController.start()
        
    def captureData(self, value):
        if not self.captureRunning:
            return
        
        self.profilePath = self.calibrationWizard.profilePath\
             + os.sep + self.calibrationWizard.depthCamera.name() + os.sep + self.calibrationWizard.depthCamera.id().split(":")[-1].split(')')[0]
        if not os.path.exists(self.profilePath):
			os.makedirs(self.profilePath)
        
        fileNames = {'lens':["far.vxl", "near.vxl", "commonPhase.vxl", "perPixel.vxl"], 
                     'commonPhase': ["commonPhase.vxl" ,"commonPhase2.vxl"], 
                     'perPixel': ["perPixel.vxl"]}
        files = fileNames[self.calibrationToDo]
        self.files = [self.profilePath + os.sep + f for f in files]
        if self.currentFrameCount > self.numberOfFrames:
            self.depthCamera.closeFrameStream()
            self.stopCapture()
        else:
            if self.depthCamera.isSavingFrameStream():
                self.currentFrameCount +=1
                self.progressBar.setValue(self.currentFrameCount*100/self.numberOfFrames)
            else:
                ret, self.modFreq1 = self.depthCamera.getf("mod_freq1")
                ret, self.modFreq2 = self.depthCamera.getf("mod_freq2")
                self.fileName = self.files[value]
                if not self.depthCamera.saveFrameStream(self.files[value]):
                    QtGui.QMessageBox.critical(self, "Can't save stream", "Cannot save the current stream")

    def startCapture(self):
        self.captureButton.setDisabled(True)
        self.frameCount.setDisabled(True)
        self.average = None
        self.captureRunning = True
        self.currentFrameCount = 0
        
    def captureDataAndCalibrate(self):
        r, self.dealiasedPhaseMask = self.depthCamera.geti("dealiased_ph_mask")
        r, dealiasEnabled = self.depthCamera.getb("dealias_en")
        if not r:
            QtGui.QMessageBox.critical(self, "Can't get parameter", "Cannot get the dealias_en parameter")
        if dealiasEnabled:
            r = self.depthCamera.setb('ind_freq_data_en', True)
            r1 = self.depthCamera.setb('ind_freq_data_sel', False)
        if self.calibrationToDo == 'lens':
            if self.farCaptured == False:
                self.startCapture()
                self.captureData(0)
                self.farFileName = self.fileName
                self.farDistance = self.distanceValue
                self.farCaptured = True
                self.message.setText(self.messageTexts[1])
                self.captureButton.setText(self.buttonTexts[1])
            elif self.nearCaptured == False:                
                self.startCapture()
                self.captureData(1)
                self.nearFileName = self.fileName
                self.nearDistance = self.distanceValue
                if 'commonPhase' in self.calibrations:
                    self.commonPhaseDistance = self.distanceValue
                    self.commonPhaseFileName = self.fileName
                    self.commonPhaseFileName1 = None
                    if not dealiasEnabled:
                        self.commonPhaseCaptured = True
                        self.nearCaptured = True
                if 'perPixel' in self.calibrations:
                    self.perPixelFileName = self.nearFileName
                    self.perPixelCaptured = True
                    self.message.setText(self.messageTexts[4])
                    self.captureButton.setText(self.buttonTexts[4])
                if 'commonPhase' in self.calibrations and dealiasEnabled is True and self.commonPhaseCaptured ==False:
                    self.message.setText(self.messageTexts[2])
                    self.captureButton.setText(self.buttonTexts[2])
                    self.nearCaptured = True
                else:
                    self.message.setText(self.messageTexts[4])
                    self.captureButton.setText(self.buttonTexts[4])
            
            elif self.commonPhaseCaptured is False and 'commonPhase' in self.calibrations:                
                r1 = self.depthCamera.setb('ind_freq_data_sel', True)
                self.startCapture()
                self.captureData(2)
                self.commonPhaseFileName1 = self.fileName
                self.commonPhaseCaptured = True
                self.message.setText(self.messageTexts[4])
                self.captureButton.setText(self.buttonTexts[4])
            elif self.perPixelCaptured is False and 'perPixel' in self.calibrations:
                self.startCapture()
                self.captureData(3)
                self.perPixelFileName = self.fileName
                self.message.setText(self.messageTexts[4])
                self.captureButton.setText(self.buttonTexts[4])
            else:
                self.calibrate()
                
                
        elif self.calibrationToDo == "commonPhase":
            if self.commonPhaseCaptured == False:
                self.startCapture()
                if not self.commonPhaseFileName:
                    self.captureData(0)
                    self.commonPhaseFileName = self.fileName
                    self.commonPhaseFileName1 = None
                    if not dealiasEnabled:
                        self.commonPhaseCaptured = True
                        self.message.setText(self.messageTexts[3])
                        self.captureButton.setText(self.buttonTexts[3])
                    else:
                        self.message.setText(self.messageTexts[1])
                        self.captureButton.setText(self.buttonTexts[1])
                        r1 = self.depthCamera.setb('ind_freq_data_sel', True)
                elif dealiasEnabled:
                    self.captureData(1)
                    self.commonPhaseFileName1 = self.fileName
                    self.message.setText(self.messageTexts[3])
                    self.captureButton.setText(self.buttonTexts[3])
                    self.commonPhaseCaptured = True
                self.commonPhaseDistance = self.distanceValue

                   
                    
                if 'perPixel' in self.calibrations:
                    self.perPixelFileName = self.fileName
                    self.perPixelCaptured = True
                    
            elif self.perPixelCaptured is False and 'perPixel' in self.calibrations:
                self.startCapture()
                self.captureData(1)
                self.perPixelFileName = self.fileName
                self.perPixelCaptured = True
                self.message.setText(self.messageTexts[2])
                self.captureButton.setText(self.buttonTexts[2])
            else:
                self.message.setText(self.messageTexts[3])
                self.captureButton.setText(self.buttonTexts[3])
                self.calibrate()
                
        elif self.calibrationToDo == 'perPixel':
            
            if self.perPixelCaptured == False:
                self.startCapture()
                self.captureData(0)
                self.perPixelCaptured = True
                self.perPixelFileName = self.fileName
                self.message.setText(self.messageTexts[1])
                self.captureButton.setText(self.buttonTexts[1])
            else:
                self.calibrate()
                
                
    def calibrate(self):
        if self.nearCaptured and self.farCaptured:
            try:
                ret, mtx, dist = flatWallLensCalibration(self.nearFileName, self.nearDistance/100, self.farFileName, self.farDistance/100)
            except Exception, e:
                ret = False
            if ret: 
                self.paramsText += "cx = %f\n cy = %f/n fx = fy = %f/n k1 = %f\n k2 = %f/n k3 = %f\n"\
                                    %(mtx[0,2], mtx[1,2], mtx[0,0], dist[0], dist[1], dist[2])
                self.message.setText("Calibration Done. Click on next to proceed")
                self.calibrationWizard.calibParams['cx'] = mtx[0,2]
                self.calibrationWizard.calibParams['cy'] = mtx[1,2]
                self.calibrationWizard.calibParams['fx'] = mtx[0,0]
                self.calibrationWizard.calibParams['fy'] = mtx[0,0]
                self.calibrationWizard.calibParams['k1'] = dist[0]
                self.calibrationWizard.calibParams['k2'] = dist[1]
                self.calibrationWizard.calibParams['k3'] = dist[2]
                self.calibrationWizard.calibParams['p1'] = 0
                self.calibrationWizard.calibParams['p1'] = 0
                self.completed = True
                self.completeChanged.emit()
            else:
                QtGui.QMessageBox.critical(self, "Check Data", "Can't get the coefficients")
         
        if self.commonPhaseCaptured:
            try:
                if 'cx' in self.calibrationWizard.calibParams:\
                    cx = self.calibrationWizard.calibParams['cx']
                else:
                    cx = 0
                if 'cy' in self.calibrationWizard.calibParams:
                    cy = self.calibrationWizard.calibParams['cy']
                else:
                    cy = 0
                ret, phaseCorr1, phaseCorr2, _, _ = commonPhaseOffset(self.commonPhaseFileName, self.commonPhaseDistance/100, self.modFreq1, cx, cy, self.commonPhaseFileName1, self.modFreq2, chipset = self.depthCamera.chipset())
            except Exception, e:
                print(e)
                ret = False
            if ret:
                self.paramsText += "phase_corr_1 = %d\n phase_corr_2 = %d\n"%(phaseCorr1, phaseCorr2)
                self.calibrationWizard.calibParams['phase_corr1'] = phaseCorr1
                self.calibrationWizard.calibParams['phase_corr2'] = phaseCorr2
            else:
                QtGui.QMessageBox.critical(self, "Check Data", "Can't get the coefficients")
        if self.perPixelCaptured:
            try:
                c = Voxel.Configuration()
                r, path = c.getLocalConfPath()
                ret, phaseOffsetFileName, _, _ = perPixelOffset(self.perPixelFileName, pathToSave=path, profileName = self.calibrationWizard.profileName, dealiasedPhaseMask = self.dealiasedPhaseMask)
            except Exception, e:
                ret = False
                print e
            if ret:
                self.paramsText += "phaseOffsetFileName: %s"%(phaseOffsetFileName)
                self.calibrationWizard.calibParams['phasecorrection'] = 'file:'+os.path.basename(phaseOffsetFileName)
            else:
                QtGui.QMessageBox.critical(self, "Check Data", "Can't get the coefficients")
             
        self.paramsLabel.setText(self.paramsText)
        self.paramsGroupBox.show()
        if self.paramsText:
            self.complete = True
            self.completeChanged.emit()    
    def isComplete(self, *args, **kwargs):
        return self.complete
    
    def setNumberOfFrames(self, value):
        self.numberOfFrames = value
        
    def stopCapture(self):
        self.captureRunning = False
        self.captureButton.setEnabled(True)
        if self.captureButton.text()!='Calibrate':
            self.frameCount.setEnabled(True)
            self.progressBar.setValue(0)
            
    def cleanupPage(self, *args, **kwargs):
        self.depthCameraController.stop()
        self.nearCaptured =False
        self.farCaptured = False
        self.commonPhaseCaptured = False
        self.perPixelCaptured = False
    
    def closeEvent(self, *args, **kwargs):
        self.depthCameraController.stop()
        
    def setDistance(self, value):
        self.distanceValue = value