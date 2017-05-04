
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

class CalibrationConclusionPage(QtGui.QWizardPage):
    """This is the final page of the wizard. The collected data is saved as a conf file in this page"""
    def __init__(self, calibrationWizard, parent = None):
        super(CalibrationConclusionPage, self).__init__(parent)
        self.calibrationWizard = calibrationWizard
        self.setTitle("Congratulations!")
        self.setSubTitle("Calibration Completed")   
        self.label = QtGui.QLabel()
        self.errorLabel = QtGui.QLabel()
        self.errorLabel.setText("Could Not save the following parameters:\n")
    def initializePage(self, *args, **kwargs):
        if self.calibrationWizard.depthCamera:
            self.calibrationWizard.depthCamera.stop()
        self.layout = QtGui.QVBoxLayout()
        for calib, value in self.calibrationWizard.calibParams.iteritems():
            self.setParam("calib", calib, value)
        if not self.calibrationWizard.depthCamera:
            self.calibrationWizard.profileName+= '.conf'
            self.calibrationWizard.currentConfiguration.write(self.calibrationWizard.profileName)
        else:
            self.calibrationWizard.currentConfiguration.write()
        text = "Successfully written files to %s"%(self.calibrationWizard.profileName)
        self.label.setText(text)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.errorLabel)
        self.errorLabel.hide()
    def setParam(self, section, name, value):
        if isinstance(value, int):
            ret = self.calibrationWizard.currentConfiguration.setInteger(section, name, value)
            if not ret:
                text = self.errorLabel.text() + str(name) + str(value) + "\n"
                self.errorLabel.setText(text)
                self.errorLabel.show()
        if isinstance(value,float):
            ret = self.calibrationWizard.currentConfiguration.setFloat(section, name, value)
            if not ret:
                text = self.errorLabel.text() + str(name) + str(value) + "\n"
                self.errorLabel.setText(text)
                self.errorLabel.show()
        if isinstance(value, str):
            ret = self.calibrationWizard.currentConfiguration.set(section, name, value)
            if not ret:
                text = self.errorLabel.text() + str(name) + str(value) + "\n"
                self.errorLabel.setText(text)
                self.errorLabel.show()