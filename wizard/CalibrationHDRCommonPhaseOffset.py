
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
        self.calibLayout = 'self.' + self.calibrationWizard.calibs['hdrCommonPhase'] + '()'
        eval(self.calibLayout)   
        self.calibrateButton = QtGui.QPushButton('Calibrate')
        self.calibrateButton.setDisabled(True)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.calibrateButton)
        hlayout.addStretch()
        self.layout.addLayout(hlayout)
        self.calibrateButton.clicked.connect(self.calibrate)                             
# #     
    def calibrate(self):
        
        ret = hdrCommonPhaseOffset(self.fileName, self.distance1, self.modFreq1,0, 0, self.fileName2, self.modFreq2)
        if not ret:
            self.valueLabel = QtGui.QLabel()
            self.valueLabel.setText('Cannot calibrate with the given file(s). Choose a different file')
            self.line.clear()
            self.line2.clear()
            self.layout.addWidget(self.valueLabel)
            self.calibrateButton.setEnabled(False)
        if ret:
            ret1, self.hdrphaseCorr1, self.hdrphaseCorr2 = ret
            self.valueLabel = QtGui.QLabel()
            text = "hdr_phase_corr1 = %d\n"%(self.hdrphaseCorr1)
            if self.phaseCorr2:
                text +=  "hdr_phase_corr_2 = %d"%(self.hdrphaseCorr2)
                self.calibrationWizard.calibParams['hdr_phase_corr_2'] = self.hdrphaseCorr2 
            self.valueLabel.setText(text)
            self.layout.addWidget(self.valueLabel)
            self.calibrationWizard.calibParams['hdr_phase_corr_1'] = self.hdrphaseCorr1
            self.calibrated = True