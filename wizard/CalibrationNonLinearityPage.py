
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


import csv 
import os
from PySide import QtGui, QtCore
from PySide.QtGui import QComboBox
from calibration.NonLinearityCalibration import NonLinearityCalibration
from CalibrationPage import CalibrationPage
from wizard.Calibrations import CALIB_SHOW, CHIPSETS
class CalibrationNonLinearityTableDelegate(QtGui.QItemDelegate):
    def __init__(self, parent = None):
        super(CalibrationNonLinearityTableDelegate, self).__init__(parent)

class CalibrationNonLinearityPage (CalibrationPage):
    """Wizard page for non linearity calibration
    
    Takes CSV file as input and gives non linearity coefficients as output """
    
    CSV_FILE_NAME = 'non-linearity.csv'
    
    def __init__(self, calibrationWizard):
        super (CalibrationNonLinearityPage, self).__init__()
        self.calibrationWizard = calibrationWizard
        self.setTitle('Non-linearity Calibration')
        self.setSubTitle('Computation of non-linearity of phase vs distance. Please measure the phase value at cx, cy')
        self.mainLayout = QtGui.QVBoxLayout(self)
        
    def initializePage(self):
        
        self.layout = QtGui.QVBoxLayout()
        hlayout = QtGui.QHBoxLayout()
        self.phasePeriod = QtGui.QComboBox()
        hlayout.addWidget(self.phasePeriod)
        hlayout.addStretch()
        if self.calibrationWizard.depthCamera:
            self.chipset = CHIPSETS[self.calibrationWizard.depthCamera.chipset()]
        else:
            self.chipset = self.calibrationWizard.camera
        self.setChipsetParams()
        self.calibrateButton = QtGui.QPushButton('&Calibrate')
        self.calibrateButton.pressed.connect(self.calibrate)
        self.calibrateButton.setShortcut('Alt+C')
        hlayout.addWidget(self.calibrateButton)
        self.layout.addLayout(hlayout)
        self.calibrateButton.setDisabled(True)
        
        hlayout = QtGui.QHBoxLayout()
        
        modFreqLabel = QtGui.QLabel("Mod Frequency 1")
        self.modFreq = QtGui.QDoubleSpinBox()
        self.modFreq.setRange(0, 75)
        self.modFrequency = 48
        self.modFreq.setValue(48)
        self.modFreq.setSingleStep(0.05)
        hlayout.addWidget(modFreqLabel)
        hlayout.addWidget(self.modFreq)
        hlayout.addStretch()
        self.modFreq.valueChanged.connect(self.setModFrequency)
        modFreq2Label = QtGui.QLabel("Mod Frequency 2")
        self.modFreq2 = QtGui.QDoubleSpinBox()
        self.modFrequency2 = 60
        self.modFreq2.setSingleStep(0.05)
        self.modFreq2.setRange(0, 75)
        self.modFreq2.setValue(60)
        hlayout.addWidget(modFreq2Label)
        hlayout.addWidget(self.modFreq2)
        self.modFreq2.valueChanged.connect(self.setModFrequency2)
        self.layout.addLayout(hlayout)
        
        groupbox = QtGui.QGroupBox()
        groupbox.setTitle('Phase vs Distance Measurements')
        self.layout.addWidget(groupbox)
        vglayout = QtGui.QVBoxLayout()
        groupbox.setLayout(vglayout)
        
        self.phaseDistanceMeasurements = QtGui.QTableWidget()
    
        self.rowLength = 2
        self.phaseDistanceMeasurements.setColumnCount(self.rowLength)
        self.phaseDistanceMeasurements.setHorizontalHeaderLabels(['Actual Distance', 'Phase 1'])

        self.phaseDistanceMeasurements.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.phaseDistanceMeasurements.setToolTip('Please ensure that entries are in increasing order of distance')
        self.phaseDistanceMeasurements.setItemDelegate(CalibrationNonLinearityTableDelegate())
        vglayout.addWidget(self.phaseDistanceMeasurements)
        
        insertRowAction = QtGui.QAction('Insert Row', self.phaseDistanceMeasurements)
        insertRowAction.setShortcut('Insert')
        insertRowAction.triggered.connect(self.insertRow)
        self.phaseDistanceMeasurements.addAction(insertRowAction)
        
        removeRowAction = QtGui.QAction('Remove Row', self.phaseDistanceMeasurements)
        removeRowAction.setShortcut('Del')
        removeRowAction.triggered.connect(self.removeRow)
        self.phaseDistanceMeasurements.addAction(removeRowAction)
        
        removeAllRowsAction = QtGui.QAction('Remove All Rows', self.phaseDistanceMeasurements)
        removeAllRowsAction.setShortcut('Shift+Del')
        removeAllRowsAction.triggered.connect(self.removeAllRows)
        self.phaseDistanceMeasurements.addAction(removeAllRowsAction)
        
        self.importCSVButton = QtGui.QPushButton('&Import From CSV')
        self.importCSVButton.setShortcut('Alt+I')
        self.importCSVButton.pressed.connect(self.importCSV)
        vglayout.addWidget(self.importCSVButton)
        
        self.paramsGroupbox = QtGui.QGroupBox()
        self.paramsGroupbox.setTitle('Non-linearity Parameters')
        self.layout.addWidget(self.paramsGroupbox)
        
        self.paramsText = QtGui.QTextEdit()
        self.paramsText.setReadOnly(True)
        self.paramsText.setMinimumHeight(100)
        
        vglayout = QtGui.QVBoxLayout()
        vglayout.addWidget(self.paramsText)
        self.paramsGroupbox.setLayout(vglayout)
        
        self.paramsGroupbox.hide()
        self.mainLayout.addLayout(self.layout)
        self.calibrated = False
    
    def cleanupPage(self, *args, **kwargs):
        self.clearLayout(self.layout)
            
    def setChipsetParams(self): 
        if self.chipset == CHIPSETS["calculus.ti"]:
            self.phasePeriod.clear()
            self.phasePeriod.addItems(['90 degrees', '180 degrees'])
            self.phasePeriod.setCurrentIndex(1)
            self.modFreq2.setDisabled(True)
            self.modFrequency2 = 0
        else:
            self.phasePeriod.clear()
            self.phasePeriod.addItems(['90 degrees', '180 degrees', '360 degrees'])
            self.phasePeriod.setCurrentIndex(2)       
    
    def setModFrequency(self, value):
        
        self.modFrequency = value
    
    def setModFrequency2(self, value):
        self.modFrequency2 = value
        
    def insertRow(self):
        i = self.phaseDistanceMeasurements.currentRow()
        
        if i >= 0 and i < self.phaseDistanceMeasurements.rowCount():
            self.phaseDistanceMeasurements.insertRow(i + 1)
        elif self.phaseDistanceMeasurements.rowCount() == 0:
            self.phaseDistanceMeasurements.insertRow(0)
        self.calibrateButton.setEnabled(True)    
    
    def removeRow(self):
        i = self.phaseDistanceMeasurements.currentRow()
        
        if i >= 0 and i < self.phaseDistanceMeasurements.rowCount():
          
            r = QtGui.QMessageBox.question(self, 'Remove Row', 'Are you sure you want to remove the current row?', \
                buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
          
            if r == QtGui.QMessageBox.Yes:
                self.phaseDistanceMeasurements.removeRow(i)
        if self.phaseDistanceMeasurements.rowCount() == 0:
            self.calibrateButton.setDisabled(True)
    def removeAllRows(self):
        r = QtGui.QMessageBox.question(self, 'Remove All Rows', 'Are you sure you want to remove all rows?', \
                buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
          
        if r == QtGui.QMessageBox.Yes:
            for i in range(0, self.phaseDistanceMeasurements.rowCount()):
                self.phaseDistanceMeasurements.removeRow(0)
        self.calibrateButton.setDisabled(True)
            
    def writeCSV(self, data, csvFile):
        with open(csvFile, 'w') as f:
            for r in data:
                f.write(','.join(format(c, ".3f") for c in r) + '\n')    
            
            
    def importCSV(self, csvFile = None):
    
        if csvFile is None:
            name, filter = QtGui.QFileDialog.getOpenFileName(self, 'Select CSV File', filter = 'CSV Files (*.csv)')
          
            if name:
                for i in range(0, self.phaseDistanceMeasurements.rowCount()):
                    self.phaseDistanceMeasurements.removeRow(0)
                csvFile = str(name)
                self.calibrated = False
                self.paramsGroupbox.hide()
            else:
                return
          
        if not os.path.exists(csvFile):
            return
        
        with open(csvFile, 'rb') as f:
            reader = csv.reader(f)
          
            c = 0
            for row in reader:
                r = self.phaseDistanceMeasurements.rowCount()
                self.phaseDistanceMeasurements.insertRow(self.phaseDistanceMeasurements.rowCount())
                if self.phaseDistanceMeasurements.rowCount()>0:
                    self.calibrateButton.setEnabled(True)
            
                for i in range(0, len(row)):
                    self.phaseDistanceMeasurements.setItem(r, i, QtGui.QTableWidgetItem(row[i]))
            
                c += 1 
    
    def getData(self):
        d = []
        for r in range(0, self.phaseDistanceMeasurements.rowCount()):
            x = []
            for c in range(0, self.rowLength):
                t = self.phaseDistanceMeasurements.item(r, c).text()
            
                if len(t) == 0:
                    QtGui.QMessageBox.critical(self, 'Data Missing', 'Data at row = %d, column = %d is empty'%(r, c))
                    return []
                x.append(float(t))
          
            d.append(x)
          
        return d        
                       
    def calibrate (self):
        d1 = self.getData()
        csvFile = self.calibrationWizard.profilePath + "/%s %s"%(self.calibrationWizard.profileName, CalibrationNonLinearityPage.CSV_FILE_NAME)
        self.writeCSV(d1, csvFile)
        try:
            ret = NonLinearityCalibration(csvFile, self.modFrequency, self.modFrequency2)
            boo, y,y2 = ret
        except Exception, e:
            ret = False
            print e
        if ret:    
            self.calibrationWizard.calibParams["phase_lin_corr_period"] = self.phasePeriod.currentIndex()
            self.calibrationWizard.calibParams["phase_lin_corr_en"] = True
            data = ''
            for c in y:
                data += str(int(c)) + ' '
            self.calibrationWizard.calibParams["phase_lin_coeff0"] = data
            data = 'phase_lin_coeff0 ' + data
            data2 = ''
            if y2:
                for c in y2:
                    data2 += str(int(c)) + ' '
                self.calibrationWizard.calibParams["phase_lin_coeff1"] = data2
            if data2:
                data2 = '\nphase_lin_coeff1' + data2
            self.paramsText.setText(data+data2)
            self.paramsGroupbox.show()
        else:
            QtGui.QMessageBox.critical(self, "Cannot compute coefficients", "Check Data")
        self.calibrated = True    
        self.completeChanged.emit()
    
    def isComplete(self):    
        return self.calibrated