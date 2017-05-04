
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
from functools import partial
from Calibrations import CALIB_DICT, CALIB_SHOW
from wizard.Calibrations import CALIB_NAME


class CalibrationSelectPage(QtGui.QWizardPage):
    def __init__(self, calibrationWizard):
        super (CalibrationSelectPage, self).__init__()
        self.calibrationWizard = calibrationWizard
        self.setTitle('Choose the type of calibration')
        self.setSubTitle('Select one calibration method for each calibration')
        self.mainLayout = QtGui.QVBoxLayout(self)
        
    def initializePage(self):
        self.calibrationWizard.calibs.clear()
        self.layout = QtGui.QVBoxLayout()
        self.calibs = {}
        for key in CALIB_SHOW:
            if CALIB_SHOW[key] == True:
                self.radioGroupBox = QtGui.QGroupBox(CALIB_NAME[key] + ' Calibration')
                self.radioButtons = QtGui.QButtonGroup(self)
                self.radioButtonList = []
                for calibrations in CALIB_DICT[key]:
                    self.radioButtonList.append(QtGui.QRadioButton(calibrations))
                self.radioButtonList[0].setChecked(True)
                self.calibrationWizard.calibs[key] = self.radioButtonList[0].text()
                 
                layout = QtGui.QVBoxLayout()
                 
                counter = 0
                for each in self.radioButtonList:
                    layout.addWidget(each)
                    self.radioButtons.addButton(each)
                    self.radioButtons.setId(each, counter)
                    counter += 1
                if not self.radioGroupBox.layout():    
                    self.radioGroupBox.setLayout(layout)
                self.layout.addWidget(self.radioGroupBox) 
                self.calibs[key] = self.radioButtons
                self.calibs[key].buttonClicked[int].connect(partial(self.buttonClicked, key)) 
        self.dataGroupBox = QtGui.QGroupBox("Data Required:")
        self.dataLabel = QtGui.QLabel()
        vlayout = QtGui.QVBoxLayout()
        self.dataGroupBox.setLayout(vlayout)
        vlayout.addWidget(self.dataLabel)
        self.setDataLabelText()
        self.layout.addWidget(self.dataGroupBox)
        self.mainLayout.addLayout(self.layout)
            
    def cleanupPage(self, *args, **kwargs):
        self.clearLayout(self.layout)
    
    
    def buttonClicked(self, key, id):
        text = self.calibs[key].checkedButton().text()
        self.calibrationWizard.calibs[key] = text
        self.setDataLabelText()
    
    def setDataLabelText(self):
        dataRequired = []
        dataLabelText = ''
        for key, value in self.calibrationWizard.calibs.iteritems():
            if value not in dataRequired:
                dataRequired.append(value)
                dataLabelText += '\n'+value
        self.dataLabel.setText(dataLabelText)
        if 'FlatWall' in dataRequired and self.calibrationWizard.depthCamera:
            self.calibrationWizard.pages['capture'].doShow = True
        
            for calib in self.calibrationWizard.calibs:
                if self.calibrationWizard.calibs[calib] == 'FlatWall':
                    self.calibrationWizard.pages[calib].doShow = False
                else:
                    self.calibrationWizard.pages[calib].doShow = True
        else:
            for calib in self.calibrationWizard.calibs:
                self.calibrationWizard.pages[calib].doShow = True
            self.calibrationWizard.pages['capture'].doShow = False
        
    def clearLayout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
    
            if isinstance(item, QtGui.QWidgetItem):
                item.widget().deleteLater()
                # or
                # item.widget().setParent(None)
            elif isinstance(item, QtGui.QSpacerItem):
                pass
                # no need to do extra stuff
            else:
                self.clearLayout(item.layout())
    
            # remove the item from layout
        layout.deleteLater()    