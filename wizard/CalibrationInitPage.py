
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
from Calibrations import CALIB_SHOW, CALIB_DICT, CHIPSETS, CALIB_NAME
from PySide.QtGui import QHBoxLayout, QLabel
from views.SelectDepthCameraDialog import SelectDepthCameraDialog
import Voxel
import copy


class CalibrationInitPage(QtGui.QWizardPage):
    """Initial Calibration Wizard Page. Here you can select the calibrations to perform"""
    def __init__(self, calibrationWizard, editIndex = -1, parent = None):
        self.calibrations = []
        self.complete = False
        for key in CALIB_DICT:
            self.calibrations.append(key)  
      
        super(CalibrationInitPage, self).__init__(parent)
        self.calibrationWizard = calibrationWizard
#         self.depthCamera = self.calibrationWizard.depthCamera
        self.editIndex = editIndex
        
        self.setTitle('Calibration Wizard for Depth Camera')
        self.setSubTitle('Choose types of calibrations to perform')
    
    
        self.vlayout = QtGui.QVBoxLayout(self)
        # Adding profiles
        self.groupbox = QtGui.QGroupBox()
        self.vlayout.addWidget(self.groupbox)
        
        self.groupbox.setTitle('Calibrations to perform')
        vglayout = QtGui.QVBoxLayout()
        
        self.groupbox.setLayout(vglayout)
        self.newProfileName = None
        
        for p in self.calibrations:
            c = QtGui.QCheckBox()
            c.setText(CALIB_NAME[p] + " Calibration")
            c.stateChanged.connect(partial(self.addCalibs, p))
            vglayout.addWidget(c)
        
        #Data Capture Method - Using files or using Camera
        self.captureDataGroupBox = QtGui.QGroupBox("Select Data Capture Method")
        hlayout = QtGui.QHBoxLayout()
        self.captureDataGroupBox.setLayout(hlayout)
        radioCapture = QtGui.QRadioButton("Capture From Camera")
        radioSelect = QtGui.QRadioButton("Select Files From PC")
        hlayout.addWidget(radioCapture)
        hlayout.addWidget(radioSelect)
        self.vlayout.addWidget(self.captureDataGroupBox)
        self.radioGroup = QtGui.QButtonGroup()
        self.radioGroup.addButton(radioCapture)
        self.radioGroup.setId(radioCapture, 1)
        self.radioGroup.addButton(radioSelect)
        self.radioGroup.setId(radioSelect,2)
        radioSelect.setChecked(True)
        
        
        #If files, select the chipset
        self.chipsetGroupBox = QtGui.QGroupBox("Select Chipset")
        self.selectChipset = QtGui.QComboBox()
        for camera in CHIPSETS:
            self.selectChipset.addItem(CHIPSETS[camera])
        hlayout = QtGui.QHBoxLayout()
        label = QtGui.QLabel("Select Chipset Type")
        hlayout.addWidget(label)
        hlayout.addStretch()
        hlayout.addWidget(self.selectChipset)
        hlayout.addStretch()
        self.chipsetGroupBox.setLayout(hlayout)
        self.vlayout.addWidget(self.chipsetGroupBox)
        
        self.chipsetGroupBox.hide()

        #Camera Profile
        self.profileGroupBox = QtGui.QGroupBox("Camera Profile")
        self.vlayout.addWidget(self.profileGroupBox)
        self.profileGroupBox.hide()
        vglayout = QtGui.QVBoxLayout()
        self.profileGroupBox.setLayout(vglayout)
        hlayout = QtGui.QHBoxLayout()
        label = QtGui.QLabel("Select Camera Profile")
        hlayout.addWidget(label)
        self.profiles = QtGui.QComboBox()
        hlayout.addWidget(self.profiles)    
        vglayout.addLayout(hlayout)
        self.newProfileName = QtGui.QWidget()
            
        vlayout = QtGui.QVBoxLayout()
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(QtGui.QLabel('New Camera Profile Name:'))
        
        newProfileNameEdit = QtGui.QLineEdit()
        newProfileNameEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[A-Za-z0-9 ]*')))           
        newProfileNameEdit.setToolTip('Only alphanumeric characters are allowed')
        hlayout.addWidget(newProfileNameEdit)
        self.newProfileNameEdit = newProfileNameEdit
        self.newProfileNameEdit.textChanged.connect(self.setProfileName)
        vlayout.addLayout(hlayout)
        
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(QtGui.QLabel('Parent Camera Profile:'))
        self.parentProfiles = QtGui.QComboBox()        
        hlayout.addWidget(self.parentProfiles)
        vlayout.addLayout(hlayout)
        
        self.newProfileName.setLayout(vlayout)
        vglayout.addWidget(self.newProfileName)
        
        #Local Profile
        self.localGroupBox = QtGui.QGroupBox("Select Local Conf File")
        self.vlayout.addWidget(self.localGroupBox)
        self.localGroupBox.hide()
        vlayout = QtGui.QVBoxLayout()
        self.profileSelectButtons = QtGui.QButtonGroup()
        newProfileButton = QtGui.QRadioButton("Create New Profile")
        editProfileButton = QtGui.QRadioButton("Edit Existing Profile")
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(newProfileButton)
        hlayout.addWidget(editProfileButton)
        vlayout.addLayout(hlayout)
        self.profileSelectButtons.addButton(newProfileButton)
        self.profileSelectButtons.setId(newProfileButton, 0)
        self.profileSelectButtons.addButton(editProfileButton)
        self.profileSelectButtons.setId(editProfileButton, 1)
        self.profileSelectButtons.button(0).setChecked(True)
        self.newProfileNameOffline = QtGui.QWidget()   
        label = QtGui.QLabel("Profile Name:")
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(label)
        self.newProfileNameEditLocal = QtGui.QLineEdit()
        self.newProfileNameEditLocal.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[A-Za-z0-9 ]*')))
        self.newProfileNameEditLocal.setToolTip('Only alphanumeric characters are allowed')
        self.newProfileNameEditLocal.textChanged.connect(self.setProfileNameLocal)
        hlayout.addWidget(self.newProfileNameEditLocal)
        self.newProfileNameOffline.setLayout(hlayout)
        vlayout.addWidget(self.newProfileNameOffline)
        self.localGroupBox.setLayout(vlayout)  
        hlayout = QtGui.QHBoxLayout()          
        label = QtGui.QLabel()
        label.setText("Select Conf file")
        hlayout.addWidget(label)
        self.confButton = QtGui.QPushButton("Pick Conf File")
        hlayout.addWidget(self.confButton)
        hlayout.addStretch()
        self.confLine = QtGui.QLineEdit()
        self.confLine.setEnabled(False)
        self.confLine.hide()
        vlayout.addLayout(hlayout)
        lhlayout = QtGui.QHBoxLayout()
        lhlayout.addWidget(self.confLine)
        lhlayout.addStretch()
        vlayout.addLayout(lhlayout)
    
        self.makeConnections()
        
    #initialize connections so that all components are up to date    
    def makeConnections(self):
        self.showNewProfileName()
        self.setDepthCamera()
        self.radioGroup.buttonClicked.connect(self.setDepthCamera)    
        self.selectChipset.currentIndexChanged.connect(self.selectChipsetType)
    def addCalibs(self, title, state):      
        
        if (state == QtCore.Qt.Checked):
            CALIB_SHOW[title] = True
            self.calibrationWizard.pages[title].doShow = True
        else:
            CALIB_SHOW[title] = False
            self.calibrationWizard.pages[title].doShow = False
                        
    def setProfileName(self):
        text = self.newProfileNameEdit.text()
        self.calibrationWizard.profileName = text
        self.complete = True 
        self.completeChanged.emit()  
        
    def setProfileNameLocal(self):
        text = self.newProfileNameEditLocal.text()
        if text:
            self.calibrationWizard.profileName = text
            self.confButton.setEnabled(True)
        else:
            self.confButton.setDisabled(True)
        
    def selectChipsetType(self, i):
        self.calibrationWizard.camera = self.selectChipset.currentText()
        
    def setDepthCamera(self):
        if self.radioGroup.checkedId() ==1 and len(self.calibrationWizard.devices) == 1:
            self.calibrationWizard.depthCamera = self.calibrationWizard.cameraSystem.connect(self.calibrationWizard.devices[0])     
            self.chipsetGroupBox.hide()
            self.setCameraProfileGroupBox()
        
        elif self.radioGroup.checkedId() ==1 :
            self.chipsetGroupBox.hide()
            self.calibrationWizard.depthCamera = SelectDepthCameraDialog.showDialog(self.calibrationWizard.cameraSystem, self)
            if not self.calibrationWizard.depthCamera:    
                self.radioGroup.button(2).setChecked(True)
                self.setDepthCamera()
            self.setCameraProfileGroupBox()
        elif self.radioGroup.checkedId() == 2:
            self.calibrationWizard.depthCamera = None
            self.chipsetGroupBox.show()
            self.selectChipsetType(self.selectChipset.currentIndex())
            self.setCameraProfileGroupBox()
        
    def showHideNewProfileName(self, index):
        if index == 0:
            self.newProfileName.show()
        else:
            self.newProfileName.hide()
            self.depthCamera.setCameraProfile(self.profileIDs[index-1])
            self.calibrationWizard.setPreviousConfiguration(self.depthCamera.getCurrentCameraProfileID())
            self.calibrationWizard.profileName = self.profileNamesAndID[self.depthCamera.getCurrentCameraProfileID()]
            self.complete = True
            self.completeChanged.emit()        
    
    def setParentProfile(self, index):
        self.calibrationWizard.parentProfile = self.parentProfiles.itemText(index)
        self.depthCamera.setCameraProfile(self.profileIDs[index])
        self.calibrationWizard.setPreviousConfiguration(self.profileIDs[index])
    
    def showNewProfileName(self):
        if self.profileSelectButtons.checkedId() == 0:
            self.newProfileNameOffline.show()
            if not self.newProfileNameEditLocal.text():
                self.confButton.setDisabled(True)
            
        else:
            self.newProfileNameOffline.hide()
            self.confButton.setEnabled(True)
        self.completeChanged.emit()
        
    def setCameraProfileGroupBox(self):
        if self.calibrationWizard.depthCamera:
            self.calibrationWizard.depthCamera.start()
            self.depthCamera = self.calibrationWizard.depthCamera
            self.profileNamesAndID = self.depthCamera.getCameraProfileNames()
        
            currentProfileID = self.depthCamera.getCurrentCameraProfileID()
            
            self.profileNames = []
            self.profileIDs = []
            
            i = 0
            index = 0
            editIndex = 0
            
            for k, v in self.profileNamesAndID.items():
                profile = self.depthCamera.configFile.getCameraProfile(k)
              
                if profile:
                    if profile.getLocation() == Voxel.ConfigurationFile.IN_CAMERA:
                        v += " (HW)";
                if not k in self.profileIDs:
                    self.profileIDs.append(k)
                    self.profileNames.append(v)
              
                if k == currentProfileID:
                    index = i
                
                if k == self.editIndex:
                    editIndex = i + 1
              
                i += 1
            
            profileNames = copy.deepcopy(self.profileNames)
            profileNames.insert(0, 'Add New')
            
            self.profiles.clear()
            self.parentProfiles.clear()
            self.profiles.addItems(profileNames)
            self.parentProfiles.addItems(self.profileNames)
            self.parentProfiles.setCurrentIndex(index)
            self.parentProfiles.currentIndexChanged.connect(self.setParentProfile)
            self.profiles.currentIndexChanged.connect(self.showHideNewProfileName)
            self.localGroupBox.hide()
            self.profileGroupBox.show()
            
            
        else:
            self.profileGroupBox.hide()
            self.localGroupBox.show()
            self.confLine.hide()
            self.confButton.clicked.connect(self.selectConfFile)
            
            self.profileSelectButtons.buttonClicked.connect(self.showNewProfileName)
            
    def selectConfFile(self):
        self.confFile, _ = QtGui.QFileDialog.getOpenFileName(self, "Select Conf File", filter = 'Conf files (*.conf)')
        if self.confFile:
            config = Voxel.ConfigurationFile()
            ret = config.read(str(self.confFile))
            if ret:
                self.calibrationWizard.previousConfiguration = config
                self.complete = True
                self.completeChanged.emit()
        
    def isComplete(self):
            return self.complete
        
    def validatePage(self):
        createNew = False
        if self.calibrationWizard.depthCamera:
            if self.profiles.currentIndex() == 0:
                createNew = True
                profileName = str(self.calibrationWizard.profileName)
            if createNew:
                print profileName
                id = self.depthCamera.addCameraProfile(profileName, self.depthCamera.getCurrentCameraProfileID())
                
                if id < 0:
                    QtGui.QMessageBox.critical('Failed to create a new profile "' + profileName + '". See logs for more details.')
                    return False
                self.calibrationWizard.currentProfileID = id
                self.calibrationWizard.currentConfiguration = self.depthCamera.configFile.getCameraProfile(id)
                self.calibrationWizard.currentProfileName = profileName
            
            else:
                self.calibrationWizard.currentConfiguration = self.calibrationWizard.previousConfiguration
                self.calibrationWizard.currentProfileName = self.profileNames[self.profiles.currentIndex() - 1]
                self.calibrationWizard.currentProfileID = self.depthCamera.getCurrentCameraProfileID()
            return True
        else:
            if self.profileSelectButtons.checkedId() == 1:
                self.calibrationWizard.currentConfiguration = self.calibrationWizard.previousConfiguration
                self.calibrationWizard.profileName = self.calibrationWizard.currentConfiguration.getProfileName()
                
            else:
                self.calibrationWizard.currentConfiguration = Voxel.ConfigurationFile()
                self.calibrationWizard.currentConfiguration.setParentID(self.calibrationWizard.previousConfiguration.getID())
                self.calibrationWizard.profileName = str(self.calibrationWizard.profileName)
                self.calibrationWizard.currentConfiguration.setProfileName((self.calibrationWizard.profileName))
                self.calibrationWizard.currentConfiguration.setID(150) #change this id in the actual conf file
            return True