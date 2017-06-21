

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
from CalibrationPage import CalibrationPage

import os
import csv

import numpy as np
from wizard.Calibrations import CALIB_SHOW
# from wizard import CalibrationPage

class CalibratePhaseTableDelegate(QtGui.QItemDelegate):
  def __init__(self, parent = None):
    super(CalibratePhaseTableDelegate, self).__init__(parent)
  
  def createEditor(self, parent, option, index):
    spinbox = QtGui.QSpinBox(parent)
    
    if index.column() == 2 or index.column() == 3:
      spinbox.setRange(0, 4095)
    else:
      spinbox.setRange(0, 200) # 200 degree celcius
      
    return spinbox

class CalibrationTemperaturePage(CalibrationPage):
  
  CSV_FILE_NAME = 'temperature-phase-offset.csv'
  MAX_PHASE_VALUE = 4096
  
  def __init__(self, calibrationWizard):
    super(CalibrationTemperaturePage, self).__init__()
          
    self.calibrationWizard = calibrationWizard
    if CALIB_SHOW['temperature'] ==True:
        self.doShow = True
    self.setTitle('Temperature Calibration')
    self.setSubTitle('Computation of influence of temperature on phase. Please measure the phase value at cx, cy')
    
    self.layout = QtGui.QVBoxLayout(self)
    
    hlayout = QtGui.QHBoxLayout()
    self.centerPointText = QtGui.QLabel()
    hlayout.addWidget(self.centerPointText)
    
    hlayout.addStretch()
    
    self.calibrateButton = QtGui.QPushButton('&Calibrate')
    self.calibrateButton.pressed.connect(self.calibrate)
    self.calibrateButton.setShortcut('Alt+C')
    hlayout.addWidget(self.calibrateButton)
    
    self.layout.addLayout(hlayout)
    
    groupbox = QtGui.QGroupBox()
    groupbox.setTitle('Temperature Measurements')
    self.layout.addWidget(groupbox)
    vglayout = QtGui.QVBoxLayout()
    groupbox.setLayout(vglayout)
    
    self.temperatureMeasurements = QtGui.QTableWidget()
    self.calibParams = {}

#     if self.chipset == CalibrationPage.CHIPSET_HADDOCK:
#       self.temperatureMeasurements.setColumnCount(4)
#       self.temperatureMeasurements.setHorizontalHeaderLabels(['Tsensor', 'Tillum', 'Phase 1', 'Phase 2'])
#     else:
    self.temperatureMeasurements.setColumnCount(3)
    self.temperatureMeasurements.setHorizontalHeaderLabels(['Tsensor', 'Tillum', 'Phase 1'])
      
    self.temperatureMeasurements.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    self.temperatureMeasurements.setToolTip('Please ensure that entries are in increasing order of temperature values')
    self.temperatureMeasurements.setItemDelegate(CalibratePhaseTableDelegate())
    vglayout.addWidget(self.temperatureMeasurements)
    
    insertRowAction = QtGui.QAction('Insert Row', self.temperatureMeasurements)
    insertRowAction.setShortcut('Insert')
    insertRowAction.triggered.connect(self.insertRow)
    self.temperatureMeasurements.addAction(insertRowAction)
    
    removeRowAction = QtGui.QAction('Remove Row', self.temperatureMeasurements)
    removeRowAction.setShortcut('Del')
    removeRowAction.triggered.connect(self.removeRow)
    self.temperatureMeasurements.addAction(removeRowAction)
    
    removeAllRowsAction = QtGui.QAction('Remove All Rows', self.temperatureMeasurements)
    removeAllRowsAction.setShortcut('Shift+Del')
    removeAllRowsAction.triggered.connect(self.removeAllRows)
    self.temperatureMeasurements.addAction(removeAllRowsAction)
    
    self.importCSVButton = QtGui.QPushButton('&Import From CSV')
    self.importCSVButton.setShortcut('Alt+I')
    self.importCSVButton.pressed.connect(self.importCSV)
    vglayout.addWidget(self.importCSVButton)
    
    self.paramsGroupbox = QtGui.QGroupBox()
    self.paramsGroupbox.setTitle('Temperature Parameters')
    self.layout.addWidget(self.paramsGroupbox)
    
    self.paramsText = QtGui.QLabel()
    
    vglayout = QtGui.QVBoxLayout()
    vglayout.addWidget(self.paramsText)
    self.paramsGroupbox.setLayout(vglayout)
    
    self.paramsGroupbox.hide()
    
    self.calibrated = False
    
  def isComplete(self):
    return self.calibrated
    
  def insertRow(self):
    i = self.temperatureMeasurements.currentRow()
    
    if i >= 0 and i < self.temperatureMeasurements.rowCount():
      self.temperatureMeasurements.insertRow(i + 1)
    elif self.temperatureMeasurements.rowCount() == 0:
      self.temperatureMeasurements.insertRow(0)
      
  def removeRow(self):
    i = self.temperatureMeasurements.currentRow()
    
    if i >= 0 and i < self.temperatureMeasurements.rowCount():
      
      r = QtGui.QMessageBox.question(self, 'Remove Row', 'Are you sure you want to remove the current row?', \
            buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
      
      if r == QtGui.QMessageBox.Yes:
        self.temperatureMeasurements.removeRow(i)
        
  def removeAllRows(self):
    r = QtGui.QMessageBox.question(self, 'Remove All Rows', 'Are you sure you want to remove all rows?', \
            buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
      
    if r == QtGui.QMessageBox.Yes:
      for i in range(0, self.temperatureMeasurements.rowCount()):
        self.temperatureMeasurements.removeRow(0)
    
  def writeCSV(self, data, csvFile):
    with open(csvFile, 'w') as f:
      for r in data:
        f.write(','.join(format(c, ".0f") for c in r) + '\n')
    
  def importCSV(self, csvFile = None):
    
    if csvFile is None:
      name, filter = QtGui.QFileDialog.getOpenFileName(self, 'Select CSV File', filter = 'CSV Files (*.csv)')
      
      if name:
        csvFile = str(name)
      else:
        return
      
    if not os.path.exists(csvFile):
      return
    
    with open(csvFile, 'rb') as f:
      reader = csv.reader(f)
      
      c = 0
      for row in reader:
        if len(row) != self.temperatureMeasurements.columnCount():
          QtGui.QMessageBox.critical(self, 'Invalid row count', ('Expected %d columns per row,' + \
                                     ' but got %d for row %d.')%(self.temperatureMeasurements.columnCount(), len(row), c))
          return
        
        r = self.temperatureMeasurements.rowCount()
        self.temperatureMeasurements.insertRow(self.temperatureMeasurements.rowCount())
        
        for i in range(0, len(row)):
          self.temperatureMeasurements.setItem(r, i, QtGui.QTableWidgetItem(row[i]))
        
        c += 1
      
  
  def initializePage(self):
    super(CalibrationTemperaturePage, self).initializePage()
    
#     if os.path.exists(self.basePath + os.sep + CalibrationTemperaturePage.CSV_FILE_NAME):
#       self.importCSV(self.basePath + os.sep + CalibrationTemperaturePage.CSV_FILE_NAME)
    
  def getData(self):
    d = []
    for r in range(0, self.temperatureMeasurements.rowCount()):
      x = []
      for c in range(0, self.temperatureMeasurements.columnCount()):
        t = self.temperatureMeasurements.item(r, c).text()
        
        if len(t) == 0:
          QtGui.QMessageBox.critical(self, 'Data Missing', 'Data at row = %d, column = %d is empty'%(r, c))
          return []
        x.append(float(t))
      
      d.append(x)
      
    return d
      
    
  def calibrate(self):
    
    d1 = self.getData()
    
    if len(d1) == 0:
      QtGui.QMessageBox.critical(self, 'Data Missing', 'Cannot perform calibration with missing data')
      return
    
    d = np.array(d1)
    
    d = d[d[:,0].argsort()]
    
    A = d[:,0:2]
    
    b1 = d[:,2]
    
    tSensorCalib = A[0, 0]
    tIllumCalib = A[0, 1]
    phaseCorr1 = b1[0]
    
    A[:,0] -= tSensorCalib
    A[:,1] -= tIllumCalib
    
    b1 -= phaseCorr1
    
#     if self.chipset == CalibrationPage.CHIPSET_HADDOCK:
#       b2 = d[:,3]
#       phaseCorr2 = b2[0]
#       b2 -= phaseCorr2
    
    At = np.transpose(A)
    
    try:
      APsuedo = np.dot(At, A)
      
      if np.linalg.det(APsuedo) < 1E-6: # singular?
        if APsuedo[0, 0] < 1E-6:
          raise Exception('Invalid data')
        else:
          t1 = np.array([np.dot(1/APsuedo[0, 0]*At[0,:], b1), 0])
          
#           if self.chipset == CalibrationPage.CHIPSET_HADDOCK:
#             t2 = np.array([np.dot(1/APsuedo[0, 0]*At[0,:], b2), 0])
      else:
        APsuedoInv = np.dot(np.linalg.inv(APsuedo), At)
        t1 = np.dot(APsuedoInv, b1)
        
#         if self.chipset == CalibrationPage.CHIPSET_HADDOCK:
#           t2 = np.array([np.dot(1/APsuedo[0, 0]*At[0,:], b2), 0])
          
    except Exception, e:
      QtGui.QMessageBox.critical(self, 'Data Singularity', 'Temperature data provided is singular. Please provide more indepedent measurements.')
      return
    
#     if self.chipset == CalibrationPage.CHIPSET_HADDOCK:
#       self.calibParams['coeff_illum_1'] = int(round(t1[1], 0))
#       self.calibParams['coeff_sensor_1'] = int(round(t1[0], 0))
#       self.calibParams['coeff_illum_2'] = int(round(t2[1], 0))
#       self.calibParams['coeff_sensor_2'] = int(round(t2[0], 0))
#       
#       self.paramsText.setText(('coeff_illum_1 = %d, coeff_sensor_1 = %d,' +\
#         '\ncoeff_illum_2 = %d, coeff_sensor_2 = %d,\n')%\
#           (int(round(t1[1], 0)), int(round(t1[0], 0)), int(round(t2[1], 0)), int(round(t2[0], 0))))
#     else:
    if self.calibrationWizard.camera == 'TintinCDKCamera':
        t1 *= 16 # for calib_prec = 1
        calibPrec = 1
        if np.any(t1 >= 2048) or np.any(t1 < -2048):
          t1 /= 16
          calibPrec = 0
        
          
    if self.calibrationWizard.camera == 'CalculusCDKCamera':
        calibPrec = 8
        t1 *= -16
        calibPrecDummy = calibPrec
        while (calibPrecDummy < 12):
            if np.any(t1 >= 2048) or np.any(t1 < -2048):
                t1 /= 2
                calibPrec += 1
            calibPrecDummy += 1
    
    
    self.calibrationWizard.calibParams['coeff_illum'] = int(round(t1[1], 0))
    self.calibrationWizard.calibParams['coeff_sensor'] = int(round(t1[0], 0))
    self.calibrationWizard.calibParams['calib_prec'] = calibPrec
    
    self.paramsText.setText(('coeff_illum = %d, coeff_sensor = %d,\n' +
                            'calib_prec = %d')%\
        (int(round(t1[1], 0)), int(round(t1[0], 0)), calibPrec))

      
    self.paramsGroupbox.show()
    self.calibrated = True
    
#     self.writeCSV(d1, self.basePath + os.sep + CalibrationTemperaturePage.CSV_FILE_NAME)
    
    self.completeChanged.emit()
  
  def wrapPhaseToSignedInteger(self, phase):
    if phase >= CalibrationTemperaturePage.MAX_PHASE_VALUE/2:
      return -1*(CalibrationTemperaturePage.MAX_PHASE_VALUE - phase)
    else:
      return phase