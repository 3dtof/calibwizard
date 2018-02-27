

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
from calibration.HDRcommonphaseoffset import hdrCommonPhaseOffset
from functools import partial
from CalibrationCommonPhase import CalibrationCommonPhasePage

class CalibrationHDRCommonPhasePage(CalibrationCommonPhasePage):
    """CalibrationHDRCommonPhasePage: This page is similar to CalibrationCommonPhasePage. HDR coefficients are required when HDR is enabled. """
    
    #TODO: Create a live capture method
    def __init__(self, calibrationWizard):
        super (CalibrationHDRCommonPhasePage, self).__init__(calibrationWizard)
        self.calibrated = False
        self.setTitle('HDR Common Phase Calibration')
        self.setSubTitle('Please provide the two files, distances and modulation frequencies.')
        self.fileName = None
        self.fileName2 = None
        
#         If file2 and modulation frequency 2 are not selected, ')
    def initializePage(self):
        self.calibLayout = 'self.' + self.calibrationWizard.calibs['hdrCommonPhase'].replace(' ', '') + '()'
        eval(self.calibLayout)   
        self.calibrateButton = QtGui.QPushButton('Calibrate')
        self.calibrateButton.setDisabled(True)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.calibrateButton)
        hlayout.addStretch()
        self.layout.addLayout(hlayout)
        self.calibrateButton.clicked.connect(self.calibrate)       
			
    def FlatWallHDR(self):
        helperText = QtGui.QLabel()
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(helperText)
        helperText.setWordWrap(True)
        self.dealiasEn = QtGui.QCheckBox("Dealias Enabled")
        self.dealiasEn.stateChanged.connect(self.showSecondFrequency)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.dealiasEn)
        hlayout.addStretch()
        self.layout.addLayout(hlayout)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch()
        self.button = QtGui.QPushButton('Select File1')
        self.line = QtGui.QLineEdit()
        self.line.setEnabled(False)
        self.line.hide()
        hlayout.addWidget(self.button)
        hlayout.addStretch()
        self.layout.addLayout(hlayout)
        self.button2 = QtGui.QPushButton('Select File2')
        self.button2.setDisabled(True)
        hlayout.addWidget(self.button2)
        hlayout.addStretch()
        lineLayout = QtGui.QHBoxLayout()
        lineLayout.addWidget(self.line)
        lineLayout.addStretch()
        self.line2 = QtGui.QLineEdit()
        self.line2.setEnabled(False)
        self.line2.hide()
        lineLayout.addWidget(self.line2)
        lineLayout.addStretch()
        self.layout.addLayout(lineLayout)
        #         if self.calibrationWizard.paths['flatWall'] is not None:
        #             self.button.setDisabled()
        #             self.label = QtGui.QLabel()
        #             pathText = 'Path to vxl' +  self.calibrationWizard.paths['flatWall']    
        #             self.label.setText(pathText)
        #             self.layout.addWidget(self.label)
        self.button.clicked.connect(partial(self.selectFileDialog, 1))
        self.button2.clicked.connect(partial(self.selectFileDialog, 2))
        freqLabel1 = QtGui.QLabel('ModFreq1')
        self.frequency1 = QtGui.QDoubleSpinBox()
        self.frequency1.setRange(0,100)
        self.frequency1.setValue(40)
        self.frequency1.setSingleStep(0.01)
        self.freqLabel2 = QtGui.QLabel('ModFreq2')
        self.frequency2 = QtGui.QDoubleSpinBox()
        self.frequency2.setValue(60)
        self.frequency2.setRange(1,100)
        self.frequency1.setSingleStep(0.01)
        self.frequency2.setDisabled(True)
        self.modFreq1 = self.frequency1.value()
        self.modFreq2 = self.frequency2.value()   
        freqLayout= QtGui.QHBoxLayout()
        freqLayout.addStretch()
        freqLayout.addWidget(freqLabel1)
        freqLayout.addWidget(self.frequency1)
        freqLayout.addStretch()
        freqLayout.addWidget(self.freqLabel2)
        freqLayout.addWidget(self.frequency2)
        freqLayout.addStretch()
        self.layout.addLayout(freqLayout)
        self.frequency1.valueChanged.connect(self.getValues)
        self.frequency2.valueChanged.connect(self.getValues)
        distLabel1 = QtGui.QLabel('Distance')
        self.dist1 = QtGui.QDoubleSpinBox()
        self.dist1.setRange(0.1, 8)
        self.dist1.setValue(0.7)
        self.dist1.setSingleStep(0.05)
        self.distance1 = self.dist1.value()   
        distLayout= QtGui.QHBoxLayout()
        distLayout.addStretch()
        distLayout.addWidget(distLabel1)
        distLayout.addWidget(self.dist1)
        distLayout.addStretch()
        self.layout.addLayout(distLayout)
        self.dist1.valueChanged.connect(self.getValues)
        self.valueLabel = None
        self.mainLayout.addLayout(self.layout)
# #     
    def calibrate(self):
        
        ret = hdrCommonPhaseOffset(fileName1 = self.fileName, distance = self.distance1, modFreq1 = self.modFreq1, cx = 0, cy = 0, fileName2 = self.fileName2, modFreq2 = self.modFreq2, chipset = self.calibrationWizard.camera)
        self.valueLabel = QtGui.QLabel()
        self.layout.addWidget(self.valueLabel)
        if not ret:
            self.valueLabel.setText('Cannot calibrate with the given file(s). Choose a different file')
            self.line.clear()
            self.line2.clear()
            self.line.hide()
            self.line2.hide()
            self.calibrateButton.setEnabled(False)
        if ret:
            ret1, self.hdrphaseCorr1, self.hdrphaseCorr2 = ret
            text = "hdr_phase_corr1 = %d\n"%(self.hdrphaseCorr1)
            if self.hdrphaseCorr2:
                text +=  "hdr_phase_corr_2 = %d"%(self.hdrphaseCorr2)
                self.calibrationWizard.calibParams['hdr_phase_corr_2'] = self.hdrphaseCorr2 
            self.valueLabel.setText(text)
            self.calibrationWizard.calibParams['hdr_phase_corr_1'] = self.hdrphaseCorr1
            self.calibrated = True
            self.completeChanged.emit()