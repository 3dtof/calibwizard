
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


import glob
from PySide import QtGui, QtCore
from calibration.CheckerboardLensCalibration import CheckerBoardLensCalibration
from functools import partial
from calibration.VxlToPng import vxltoPng
from CalibrationPage import CalibrationPage
from calibration.FlatWallLensCalib import flatWallLensCalibration
from capture.CalibrationDataCaptureDialog import CalibrationDataCaptureDialog
import cv2
import numpy as np
import os
import datetime

class CalibrationImage(QtGui.QListWidgetItem):
  
  def __init__(self, imageFile, calibrationLensPage):
    super(CalibrationImage, self).__init__(QtGui.QIcon(imageFile), os.path.basename(imageFile))
    
    self.imageFile = imageFile
    self.calibrationLensPage = calibrationLensPage
    self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
  def computeCorners(self):
    self.rows, self.cols = self.calibrationLensPage.getValues()

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    self.objpoints = np.zeros((self.rows*self.cols, 3), np.float32)
    self.objpoints[:,:2] = np.mgrid[0:self.cols, 0:self.rows].T.reshape(-1,2)
    
    self.img = cv2.imread(self.imageFile)
    gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)# images are converted to grayscale
    self.imageShape = gray.shape
    
    # Find the chess board corners
    self.ret, self.corners = cv2.findChessboardCorners(gray, (self.cols, self.rows),None)
    
    if self.corners is not None:
      cv2.cornerSubPix(gray, self.corners, (4, 4),(-1,-1), self.criteria)
      
  def showCorners(self):
    self.computeCorners()
    
    if self.corners is None:
      QtGui.QMessageBox.critical(self.calibrationLensPage, 'Corners not found', 'Necessary corners could not be computed')
      return
    
    cv2.drawChessboardCorners(self.img, (self.cols, self.rows), self.corners, self.ret)
    cv2.namedWindow(os.path.basename(self.imageFile), cv2.WINDOW_NORMAL)
    cv2.imshow(os.path.basename(self.imageFile), self.img)
    cv2.waitKey()
    cv2.destroyWindow(os.path.basename(self.imageFile))
    
    del self.img



class CalibrationLensPage(CalibrationPage):
    """Calibration Lens page for computation of the lens parameters"""
    def __init__(self, calibrationWizard):
        super (CalibrationLensPage, self).__init__()
        self.calibrationWizard = calibrationWizard
        self.setTitle('Lens Calibration')
        self.setSubTitle('Select files for calibration')
        self.calibrated = False
        self.calibrationImages = None
        
    def initializePage(self):    
        self.layout = QtGui.QVBoxLayout(self)
        self.calibrateButton = QtGui.QPushButton('Calibrate')
        self.calibrateButton.setDisabled(True)

        label = QtGui.QLabel('Select Data Source')
        self.calibLayout = 'self.' + self.calibrationWizard.calibs['lens'] + '()'
        self.calibrateType = 'self.' + self.calibrationWizard.calibs['lens'] + 'Calib()'
        self.lensPath = None
        self.groupbox = None
        self.paramsGroupBox = None
        if self.calibrationWizard.depthCamera:
            depthCamera = self.calibrationWizard.depthCamera
            self.lensPath = self.calibrationWizard.profilePath\
             + os.sep + depthCamera.name() + os.sep + depthCamera.id().split(":")[-1].split(')')[0]
        self.setLayout()
        self.calibrateButton.clicked.connect(self.calibrate)
        
    def cleanupPage(self, *args, **kwargs):
        self.clearLayout(self.layout)
        
    def setLayout(self):
        eval(self.calibLayout)
        
    def CheckerBoard(self):
        self.label = QtGui.QLabel('Select the directory for the images. Also, select the no of rows and colums')
        self.layout.addWidget(self.label)
        if self.lensPath is None: 
            hlayout = QtGui.QHBoxLayout()
            hlayout.addStretch()
            self.lensPathButton = QtGui.QPushButton('Select Image Path')
            hlayout.addWidget(self.lensPathButton)
            hlayout.addStretch()
            self.layout.addLayout(hlayout)
            self.lensPathButton.clicked.connect(self.setDirectory)    
        self.calibrationImages = None
        self.rows = QtGui.QSpinBox()
        self.rows.setMaximum(25)
        self.rows.setMinimum(3)
        self.rows.setValue(8)
        self.rowValue = self.rows.value()
        rowlabel = QtGui.QLabel('rows')
        collabel = QtGui.QLabel('cols')
        self.cols = QtGui.QSpinBox()
        self.cols.setMaximum(25)
        self.cols.setMinimum(3)
        self.cols.setValue(8)
        self.colValue = self.cols.value()
        self.rows.valueChanged.connect(self.setValues)
        self.cols.valueChanged.connect(self.setValues)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(rowlabel)
        hlayout.addWidget(self.rows)
#         hlayout.addStretch()
        hlayout.addWidget(collabel)
        hlayout.addWidget(self.cols)
        self.layout.addLayout(hlayout)
        if self.lensPath:
            if not os.path.exists(self.lensPath):
                os.makedirs(self.lensPath)
            self.populateImages()

    def setDirectory(self):   
        lensPath = QtGui.QFileDialog.getExistingDirectory(self, "Open the folder Containing Images", self.lensPath)
        if lensPath:
            if self.paramsGroupBox:
                self.paramsGroupBox.hide()
                self.calibrated = False
                self.completeChanged.emit()
            self.lensPath = lensPath
            self.lensPathButton.setText('Change Path')
            self.populateImages()
        
    def populateImages(self):
        if self.groupbox is None:
            self.groupbox = QtGui.QGroupBox()
            self.layout.addWidget(self.groupbox)
        self.groupbox.setTitle('Input Images showing Lens Distortion')
        if self.calibrationImages:
            self.calibrationImages.clear()
        if not self.calibrationImages:
            self.calibrationImages = QtGui.QListWidget()
            self.calibrationImages.keyPressEvent = self.calibratedImagesKeyPressEvent
            self.calibrationImages.setResizeMode(QtGui.QListView.Adjust)
            self.calibrationImages.setWordWrap(True)
            self.calibrationImages.setTextElideMode(QtCore.Qt.ElideNone)
            self.calibrationImages.itemDoubleClicked.connect(self.showImage)
            self.calibrationImages.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.calibrationImages.customContextMenuRequested.connect(self.showContextMenu)
        
            self.menu = QtGui.QMenu(self.calibrationImages)
            
            self.removeAction = QtGui.QAction('Remove', self.calibrationImages)
            self.removeAction.triggered.connect(self.deleteImage)
            self.removeAction.setShortcut('Del')
            self.menu.addAction(self.removeAction)
            
            self.showAction = QtGui.QAction('Show Corners', self.calibrationImages)
            self.showAction.triggered.connect(self.showImage)
            self.showAction.setShortcut('Return')
            self.menu.addAction(self.showAction)
            
            vglayout = QtGui.QVBoxLayout()
            vglayout.addWidget(self.calibrationImages)
            self.groupbox.setLayout(vglayout)
            
            self.calibrationImages.setViewMode(QtGui.QListView.IconMode)
            self.calibrationImages.setIconSize(QtCore.QSize(80, 60))
            self.calibrationImages.setSpacing(4)
        if self.calibrationWizard.depthCamera:
            self.calibrationImages.addItem(QtGui.QListWidgetItem(QtGui.QIcon("images/add.png"), 'Add'))
            self.calibrationImages.clear()
            self.calibrationImages.addItem(QtGui.QListWidgetItem(QtGui.QIcon("images/add.png"), 'Add'))
            
        if not os.path.exists(self.lensPath):
          os.makedirs(self.lensPath)
        
        self.calibrationImageFiles = glob.glob(self.lensPath + os.sep + '*.png')
        if not self.calibrationImageFiles:
            images = glob.glob(self.lensPath + os.sep + '*.vxl')
            if images:
                for image in images:
                    vxltoPng(str(image))
                self.calibrationImageFiles = glob.glob(self.lensPath + os.sep + '*.png')
            if not self.calibrationImageFiles and not self.calibrationWizard.depthCamera:
                QtGui.QMessageBox.critical(self, "No images found", "Select a different Directory")
        for f in self.calibrationImageFiles:
          self.calibrationImages.insertItem(self.calibrationImages.count() - 1, CalibrationImage(f, self))
        self.calibrateButton.setEnabled(True) 
        self.setCalibrateButton()
    def showContextMenu(self, point):
        item = self.calibrationImages.itemAt(point)
        
        if item:
          index = self.calibrationImages.row(item)
          
          if index < self.calibrationImages.count() - 1:
            self.menu.popup(self.calibrationImages.mapToGlobal(point))
            
    
    def calibratedImagesKeyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
          self.showImage()
          event.accept()
        elif event.key() == QtCore.Qt.Key_Delete:
          self.deleteImage()
          event.accept()
        else:
          QtGui.QListWidget.keyPressEvent(self.calibrationImages, event)


    def showImage(self, item = None):
        if not item:
          item = self.calibrationImages.currentItem()
          
        if isinstance(item, CalibrationImage):
          item.showCorners()
        else: # Capture and add image
            if self.calibrationWizard.depthCamera:
                newFileName = self.lensPath + os.sep + '%s.png'%(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
                data = CalibrationDataCaptureDialog.showDialog(self.calibrationWizard.cameraSystem, \
                  self.calibrationWizard.depthCamera, newFileName,
                  'amplitude', 200)
            else:
                errorMessage = QtGui.QMessageBox()
                errorMessage.setText("Can't capture Data. Please ensure that the camera is added correctly. ")
                errorMessage.setStandardButtons(QtGui.QMessageBox.Ok)
                errorMessage.exec_()
                return
            if data is None:
                return

            self.addImage(newFileName)
    
    def deleteImage(self):
        item = self.calibrationImages.currentItem()
        
        if not item:
            return
        
        if isinstance(item, CalibrationImage):
          
            d = QtGui.QMessageBox.question(self.calibrationWizard, 'Remove Image', \
                'Are you sure you want to remove the image?', buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
          
            if d == QtGui.QMessageBox.Yes:
                os.remove(item.imageFile)
        self.calibrationImages.takeItem(self.calibrationImages.row(item))
        
    def addImage(self, image):
        self.calibrationImages.insertItem(self.calibrationImages.count() - 1, CalibrationImage(image, self))    
                
    def CheckerBoardCalib(self):
        try:
            ret, mtx, dist, _, _ = CheckerBoardLensCalibration(self.lensPath, self.rowValue, self.colValue)
        except Exception, e:
            ret = False
        if ret:
            self.setCalibParams(mtx, dist)
            dist = dist[0]
            text = "cx = %f\ncy = %f\nfx = %f\nfy = %f\nk1 = %f\nk2 = %f\nk3 = %f\np1 = %f\np2 = %f\n"\
            %(mtx[0,2], mtx[1,2], mtx[0,0], mtx[1,1], dist[0], dist[1], dist[4], dist[2],dist[3])
            self.paramsText.setText(text)
            self.paramsGroupBox.show()
            self.calibrated = True
        else:
            QtGui.QMessageBox.critical(self, "Lens Calibration", "Cannot perform lens calibration")    
                
    def FlatWall(self): 
        nearLabel = QtGui.QLabel('Distance from the wall')
        fileLabel = QtGui.QLabel('Select near source file')
        self.nearDist = QtGui.QDoubleSpinBox()
        self.nearDist.setRange(0.2, 4)
        self.nearDist.setValue(0.4)
        self.nearValue = 0.4
        self.nearDist.setSingleStep(0.01)
        self.farDist = QtGui.QDoubleSpinBox()
        self.farDist.setRange(0.2, 4)
        self.farDist.setSingleStep(0.01)        
        self.farDist.setValue(0.8)
        self.farValue = 0.8
        layout = QtGui.QHBoxLayout()
        layout.addWidget(nearLabel)
        layout.addStretch()
        layout.addWidget(self.nearDist)
        self.layout.addLayout(layout)
        self.farDist.valueChanged.connect(self.setDistanceValues)
        self.nearDist.valueChanged.connect(self.setDistanceValues)
        
        fileButton = QtGui.QPushButton('Select File')
        layout = QtGui.QHBoxLayout()
        layout.addWidget(fileLabel)
        layout.addStretch()
        layout.addWidget(fileButton)
        self.layout.addLayout(layout)
        fileButton.clicked.connect(partial(self.selectFileDialog, 1))
        self.nearFileText = QtGui.QLineEdit()
        self.nearFileText.setEnabled(False)
        self.nearFileText.hide()
        self.layout.addWidget(self.nearFileText)
        
        farLabel = QtGui.QLabel('Distance from the wall')
        fileLabel2 = QtGui.QLabel('Select far source file')
        layout = QtGui.QHBoxLayout()
        layout.addWidget(farLabel)
        layout.addStretch()
        layout.addWidget(self.farDist)
        self.layout.addLayout(layout)
        
        fileButton2 = QtGui.QPushButton('Select File2')
        layout = QtGui.QHBoxLayout()
        layout.addWidget(fileLabel2)
        layout.addStretch()
        layout.addWidget(fileButton2)
        self.layout.addLayout(layout)
        fileButton2.clicked.connect(partial(self.selectFileDialog, 2))
        self.farFileText = QtGui.QLineEdit()
        self.farFileText.setEnabled(False)
        self.farFileText.hide()
        self.layout.addWidget(self.farFileText)    
        self.setCalibrateButton()
        
    def FlatWallCalib(self):
        ret, mtx, dist = flatWallLensCalibration(self.fileName, self.nearValue, self.fileName2, self.farValue)
        if ret: 
            self.setCalibParams(mtx, dist)
            self.calibrated = True
            
    def selectFileDialog(self, key):
        if not self.calibrationWizard.depthCamera:
            name, _  = QtGui.QFileDialog.getOpenFileName(self, 'Select VXL file','','VXL files (*.vxl)', None, QtGui.QFileDialog.DontUseNativeDialog)    
    #         name, filter = QtGui.QFileDialog.getOpenFileName(self, 'Select CSV File', filter = '*.csv (CSV Files)')
            if name:
                if key == 1:
                    self.fileName = str(name)
                    self.calibrationWizard.paths['flatWall'] = str(name)
    
                    self.nearFileText.setText(self.fileName)
                    self.nearFileText.show()
                
                if key == 2:
                    self.fileName2 = str(name)
                    if self.fileName == self.fileName2:
                        self.fileName2 = None
                        self.selectFileDialog(2)
                    else:
                        self.farFileText.setText(self.fileName2)
                        self.farFileText.show()    
                        self.calibrateButton.setEnabled(True)
        else:
            newFileName = self.lensPath + os.sep + 'FlatWall %s.vxl'%(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
            data = CalibrationDataCaptureDialog.showDialog(self.calibrationWizard.cameraSystem, \
                  self.calibrationWizard.depthCamera, newFileName,
                  'phase', 200)
#             if data is None:
#                 return 
            if key == 1:
                self.fileName = newFileName
                self.nearFileText.setText(self.fileName)
                self.nearFileText.show()
            if key == 2:
                self.fileName2 = newFileName
                self.calibrateButton.setEnabled(True)
                self.farFileText.setText(self.fileName2)
                self.farFileText.show()
    def setCalibrateButton(self):
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.calibrateButton)
        hlayout.addStretch()
        self.layout.addLayout(hlayout)
        if not self.paramsGroupBox:
            self.paramsGroupBox = QtGui.QGroupBox("Calibration Parameters")
            vlayout = QtGui.QVBoxLayout()
            self.paramsGroupBox.setLayout(vlayout)
            self.layout.addWidget(self.paramsGroupBox)
            self.paramsText = QtGui.QLabel()
            vlayout.addWidget(self.paramsText) 
            self.paramsGroupBox.hide()    
            
    def calibrate(self):
        eval(self.calibrateType)
        self.completeChanged.emit()
        
        
    def setValues(self, value):    
        self.rowValue = self.rows.value()
        self.colValue = self.cols.value()
   
    def setDistanceValues(self,value):
        self.nearValue = self.nearDist.value()
        self.farValue = self.farDist.value()    
    def getValues(self):
        return self.rows.value(), self.cols.value()    
        
    def setCalibParams(self, mtx, dist):
        dist = dist[0]
        fx = mtx[0,0]
        fy = mtx[1,1]
        cx = mtx[0,2]
        cy = mtx[1,2]
        if len(dist) == 5:
            k1 = dist[0]
            k2 = dist[1]
            p1 = dist[2]
            p2 = dist[3]
            k3 = dist[4]
        elif len(dist) == 3:
            k1 = dist[0]
            k2 = dist[1]
            k3 = dist[2]
            p1 = p2 = 0    
        else:
            k1 = k2 = k3 = 0
            p1 = p2 = 0
            
        self.calibrationWizard.calibParams['fx'] = fx
        self.calibrationWizard.calibParams['fy'] = fy
        self.calibrationWizard.calibParams['cx'] = cx
        self.calibrationWizard.calibParams['cy'] = cy
        self.calibrationWizard.calibParams['k1'] = k1
        self.calibrationWizard.calibParams['k2'] = k2
        self.calibrationWizard.calibParams['p1'] = p1
        self.calibrationWizard.calibParams['p2'] = p2
        self.calibrationWizard.calibParams['k3'] = k3
 