
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
from calibration.PerPixelOffset import perPixelOffset
from CalibrationPage import CalibrationPage
class CalibrationPerPixelOffsetPage(CalibrationPage):
    def __init__(self, calibrationWizard):
        super (CalibrationPerPixelOffsetPage, self).__init__()
        self.calibrationWizard = calibrationWizard
        self.calibrated = False
        self.setTitle('Per Pixel Offset Calibration')
        self.setSubTitle('Choose the per pixel off set file for calibration')
        self.mainLayout = QtGui.QVBoxLayout(self)
    def initializePage(self):
        
        self.layout = QtGui.QVBoxLayout()
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch()
        self.button = QtGui.QPushButton('Select VXL file')
        hlayout.addWidget(self.button)
        hlayout.addStretch()
        self.layout.addLayout(hlayout)
        self.line = QtGui.QLineEdit()
        self.line.setEnabled(False)
        self.line.hide()
        self.layout.addWidget(self.line)
        self.button.clicked.connect(self.selectFileDialog)
        self.calibrateButton = QtGui.QPushButton('Calibrate')
        self.calibrateButton.setDisabled(True)
        label = QtGui.QLabel("Dealiased Phase Mask")
        self.dealiasedPhaseMaskSpinBox = QtGui.QSpinBox()
        self.dealiasedPhaseMaskSpinBox.setRange(-10, 10)
        self.dealiasedPhaseMaskSpinBox.setValue(0)
        self.dealiasedPhaseMask = 0
        self.dealiasedPhaseMaskSpinBox.valueChanged.connect(self.setDealiasedPhaseMask)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(label)
        hlayout.addStretch()
        hlayout.addWidget(self.dealiasedPhaseMaskSpinBox)
        hlayout.addStretch()
        self.layout.addLayout(hlayout)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.calibrateButton)
        hlayout.addStretch()
        self.layout.addLayout(hlayout)
        self.calibrateButton.pressed.connect(self.calibrate)
        
        if 'flatWall' in self.calibrationWizard.paths:
            self.line.setText(self.calibrationWizard.paths['flatWall'])
            self.fileName = self.calibrationWizard.paths['flatWall']
            self.line.show()
            self.calibrateButton.setEnabled(True)
        self.label = QtGui.QLabel()
        self.layout.addWidget(self.label)
        self.mainLayout.addLayout(self.layout)
        
    def cleanupPage(self, *args, **kwargs):
        self.clearLayout(self.layout)    
    
    
    def selectFileDialog(self):
        name, _  = QtGui.QFileDialog.getOpenFileName(self, 'Select VXL file', filter = 'VXL files (*.vxl)')    
#         name, filter = QtGui.QFileDialog.getOpenFileName(self, 'Select CSV File', filter = '*.csv (CSV Files)')
        if name:
            self.fileName = str(name)
#             print self.fileName.type
            self.calibrationWizard.paths['flatWall'] = self.fileName
            self.line.setText(self.fileName)
            self.line.show()
            self.calibrateButton.setEnabled(True)
    
    def calibrate(self):
        self.calibrateButton.setDisabled(True)
        self.label.setText("Calibrating ...")
        boo, text, rows, cols = perPixelOffset(self.fileName,dealiasedPhaseMask = self.dealiasedPhaseMask, pathToSave = None, profileName = self.calibrationWizard.profileName)
        
        if boo:
            self.calibrated = True
            self.label.setText("Calibration Complete \n Successfully saved the phase offsets to %s"%(text))
            self.calibrateButton.setEnabled(True)
            self.calibrationWizard.calibParams['phasecorrection'] = 'file:'+ text  
            self.completeChanged.emit()
        else:
            self.label.setText("Could not complete calibration. Try with a different file") 
            self.calibrateButton.setEnabled(True)   

    def setDealiasedPhaseMask(self, value):
        self.dealiasedPhaseMask = value