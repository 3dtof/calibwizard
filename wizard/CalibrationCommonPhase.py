
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
from calibration.CommonPhaseOffsetRawDataSimpleAverage import commonPhaseOffset
from functools import partial
from CalibrationPage import CalibrationPage

class CalibrationCommonPhasePage(CalibrationPage):
    """Returns the common phase offsets for a particular chipset
    
    Uses a vxl file of a flat wall and returns the common phase offset. The file can be recorded using Voxel Viewer. 
    
    **Parameters**:
        -dealias_en: If the parameter dealias_en is true or false
        -fileName1: VXL file pointing to the flat wall, captured using voxel viewer
        -modFreq1: Modulation Frequency 1, corresponding to the frequency used in fileName1
        -distance: Distance of the camera from the flat wall
        -fileName2: VXL file pointing to the flat wall, captured using voxel viewer
        -modFreq2: Modulation Frequency 2, corresponding to the frequency used in fileName2
        
    .. note:: 
        If dealias_en is true, capture the first vxl using the following method for saving vxl files:
            - Open Voxel Viewer
            - Set ind_freq_data_en True
            - Set ind_freq_data_sel as False
            - Capture data (at least 200 frames)
        
        For second modulation frequency, turn ind_freq_data_sel to True and capture data again.
        
    - Make sure that the distance of the camera does **not** change while capturing data
    """
    def __init__(self, calibrationWizard):
        super (CalibrationCommonPhasePage, self).__init__()
        self.calibrationWizard = calibrationWizard
        self.calibrated = False
        self.setTitle('Common Phase Calibration')
        self.setSubTitle('Please provide the two files, distances and modulation frequencies.')
        self.fileName = None
        self.fileName2 = None
        self.doShow  = False
        self.mainLayout = QtGui.QVBoxLayout(self)
#         If file2 and modulation frequency 2 are not selected, ')
    def initializePage(self):
        self.calibLayout = 'self.' + self.calibrationWizard.calibs['commonPhase'] + '()'
        self.calibrateType = 'self.' + self.calibrationWizard.calibs['commonPhase'] + 'Calib()'

        eval(self.calibLayout)                                
        self.calibrateButton = QtGui.QPushButton('Calibrate')
        self.calibrateButton.setDisabled(True)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.calibrateButton)
        hlayout.addStretch()
        self.layout.addLayout(hlayout)
        self.calibrateButton.clicked.connect(self.calibrate)
        
    def FlatWall(self):
        helperText = QtGui.QLabel("If you're using just one modulation frequency, enter the data under fileName1, modulation frequency 1 and distance 1")
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
        self.frequency1 = QtGui.QSpinBox()
        self.frequency1.setRange(0,100)
        self.frequency1.setValue(40)
        self.freqLabel2 = QtGui.QLabel('ModFreq2')
        self.frequency2 = QtGui.QSpinBox()
        self.frequency2.setValue(60)
        self.frequency2.setRange(1,100)
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
        
    def cleanupPage(self, *args, **kwargs):
        self.clearLayout(self.layout)    
        
    def selectFileDialog(self, key):

        name, _  = QtGui.QFileDialog.getOpenFileName(self, 'Select VXL file', filter = 'VXL files (*.vxl)')    
#         name, filter = QtGui.QFileDialog.getOpenFileName(self, 'Select CSV File', filter = '*.csv (CSV Files)')
        if name:
            if key == 1:
                self.fileName = str(name)
                self.calibrationWizard.paths['flatWall'] = str(name)
                if not self.dealiasEn.isChecked():
                    self.calibrateButton.setEnabled(True)
                self.line.setText(self.fileName)
                self.line.show()
            
            if key == 2:
                self.fileName2 = str(name)
                if self.fileName == self.fileName2:
                    self.fileName2 = None
                    self.selectFileDialog(2)
                else:
                    self.line2.setText(self.fileName2)
                    self.line2.show()    
                    self.calibrateButton.setEnabled(True)
#             if len(name)>1:
#                 self.fileName2 = str(name[1])
#                 self.calibrationWizard.paths['flatWall'].append(str(name[1]))
    def showSecondFrequency(self):
        if self.dealiasEn.isChecked():
            self.button2.setEnabled(True)
            self.frequency2.setEnabled(True)
            if not self.fileName2:
                self.calibrateButton.setDisabled(True)
        else:
            self.button2.setDisabled(True)
            self.frequency2.setDisabled(True)
            if (self.fileName):
                self.calibrateButton.setEnabled(True)
    def calibrate(self):
        eval(self.calibrateType)
        self.calibrated = True
        self.completeChanged.emit()
#     
    def FlatWallCalib(self):
        
        ret = commonPhaseOffset(self.fileName, self.distance1, self.modFreq1, 0, 0, self.fileName2, self.modFreq2, 4, self.calibrationWizard.camera)
        if not self.valueLabel:
            self.valueLabel = QtGui.QLabel()
        if not ret:
            QtGui.QMessageBox.critical("Cannot get the correct phaseCorr value. Please Check data")
            
        else: 
            boo, self.phaseCorr1, self.phaseCorr2, rows, cols = ret
            text = "phaseCorr1 = %d\n"%(self.phaseCorr1)
            if self.phaseCorr2:
                text +=  "phaseCorr2 = %d"%(self.phaseCorr2)
            self.valueLabel.setText(text)
            self.layout.addWidget(self.valueLabel)
            self.calibrationWizard.calibParams['phase_corr_1'] = self.phaseCorr1
            self.calibrationWizard.calibParams['phase_corr_2'] = self.phaseCorr2
            self.calibrated = True
        
    def getValues(self, value):
        self.modFreq1 = self.frequency1.value()
        self.modFreq2 = self.frequency2.value()    
        self.distance1 = self.dist1.value()        
    def isComplete(self, *args, **kwargs):
        return self.calibrated    
        