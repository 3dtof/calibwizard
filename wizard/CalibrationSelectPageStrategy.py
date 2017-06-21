
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
from Calibrations import CALIB_DICT, CALIB_SHOW, CALIB_NAME, DATA
from collections import OrderedDict

class CalibrationSelectPage(QtGui.QWizardPage):
    def __init__(self, calibrationWizard):
        super (CalibrationSelectPage, self).__init__()
        self.calibrationWizard = calibrationWizard
        self.setTitle('Choose the type of calibration')
        self.setSubTitle('Select one calibration method for each calibration')
        self.mainLayout = QtGui.QVBoxLayout(self)
        
    def initializePage(self):
        self.calibrationsSelected = False
        self.calibrationWizard.calibs.clear()
        self.layout = QtGui.QVBoxLayout()
        self.resetButton = QtGui.QPushButton("Reset")
        self.resetButton.clicked.connect(self.resetParameters)
        layout = QtGui.QHBoxLayout()
        self.layout.addLayout(layout)
        self.calibs = OrderedDict()
        self.calibrations = []
        self.strategies = set()
        self.strategyGroupBox = QtGui.QGroupBox("Strategies")
        self.calibrationsGroupBox = QtGui.QGroupBox("Calibrations")
        self.calibrationsLayout = QtGui.QVBoxLayout()
        self.calibrationsGroupBox.setLayout(self.calibrationsLayout)
        self.strategiesLayout =QtGui.QVBoxLayout()
        self.strategyGroupBox.setLayout(self.strategiesLayout)
        layout.addWidget(self.strategyGroupBox)
        layout.addWidget(self.calibrationsGroupBox)
        layout.addWidget(self.resetButton)
        self.resetButton.setEnabled(False)
        for key in CALIB_SHOW:
            if CALIB_SHOW[key] == True:
                self.strategies.update(CALIB_DICT[key])
                self.calibs[key] = CALIB_DICT[key]
        self.buttonDict = {}
        self.strategyButtonDict = OrderedDict()
        for strategy in self.strategies:
            p = QtGui.QCheckBox(strategy)
            self.strategyButtonDict[strategy] = p
            p.stateChanged.connect(self.buttonClicked)
            self.strategiesLayout.addWidget(p)
        for calibration in self.calibs:
            self.buttonDict[calibration] = (QtGui.QCheckBox(CALIB_NAME[calibration] + " Calibration"))
            self.buttonDict[calibration].setEnabled(False)
            self.buttonDict[calibration].setStyleSheet("QCheckBox::unchecked{ color:red; } QCheckBox::checked{ color:green;}")
            self.calibrationsLayout.addWidget(self.buttonDict[calibration])
        
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
    
    
    def buttonClicked(self, state):
        for key in self.calibs:
            for strategy in self.strategyButtonDict:
                if strategy in CALIB_DICT[key] and self.strategyButtonDict[strategy].isChecked() is True:
                    self.buttonDict[key].setChecked(True)
                    self.calibrationWizard.calibs[key] = strategy
                    self.setDataLabelText()
                    
                if strategy in CALIB_DICT[key] and self.strategyButtonDict[strategy].isChecked() is False:
                    if key in self.calibrationWizard.calibs and self.calibrationWizard.calibs[key] == strategy:
                        del self.calibrationWizard.calibs[key]
                        self.buttonDict[key].setChecked(False)
                    self.setDataLabelText()
            
        for strategy, button in self.strategyButtonDict.iteritems():
            check = False
            for key, strat in self.calibrationWizard.calibs.iteritems():
                if strat == strategy:
                    check = True
            if check == False:
                button.setChecked(False)
            else:
                button.setChecked(True)
        dummy = True
        for key in self.buttonDict:
            dummy = dummy and self.buttonDict[key].isChecked()
        self.calibrationsSelected = dummy
        if self.calibrationsSelected:
            for strategy, button in self.strategyButtonDict.iteritems():
                button.setEnabled(False)
                self.resetButton.setEnabled(True)
        self.completeChanged.emit()       
    
    def setDataLabelText(self):
        dataRequired = []
        dataLabelText = ''
        for key, value in self.calibrationWizard.calibs.iteritems():
            if value not in dataRequired:
                dataRequired.append(value)
                dataLabelText += '\n'+DATA[value]
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
        
    def resetParameters(self):
        for key, button in self.strategyButtonDict.iteritems():
            button.setChecked(False)
            button.setDisabled(False)
        
        for calib in self.calibrationWizard.calibs:
            del self.calibrationWizard.calibs[calib]
        
        for key, button in self.buttonDict.iteritems():
            button.setChecked(False)
        
        for key, button in self.strategyButtonDict.iteritems():
            button.setChecked(False)
        self.calibrationsSelected = False
        self.resetButton.setEnabled(False)
        self.completeChanged.emit()
        
        
    def isComplete(self, *args, **kwargs):
        return self.calibrationsSelected  