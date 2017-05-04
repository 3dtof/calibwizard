
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


from PySide import QtGui
from PySide import QtCore
import sys
import os
import Voxel
from wizard.CalibrationInitPage import CalibrationInitPage
from wizard.CalibrationSelectPage import CalibrationSelectPage
from wizard.CalibrationLensPage import CalibrationLensPage
from wizard.CalibrationConclusionsPage import CalibrationConclusionPage
from wizard.CalibrationTemperaturePage import CalibrationTemperaturePage
# from CalibrationCommonPhase import CalibrationCommonPhasePage
from wizard.CalibrationPerPixelOffsetPage import CalibrationPerPixelOffsetPage
from wizard.CalibrationCommonPhase import CalibrationCommonPhasePage
from wizard.CalibrationNonLinearityPage import CalibrationNonLinearityPage
# from CalibrationDataCaptureDialog import CalibrationDataCaptureDialog
from wizard.CalibrationHDRCommonPhaseOffset import CalibrationHDRCommonPhasePage
from wizard.CalibrationCaptureData import CalibrationDataCapturePage
from wizard.CalibrationPage import CalibrationPage
from collections import OrderedDict
# import ConfigParser


class CalibrationWizard (QtGui.QWizard):
    """ Run this file to start the wizard
    
    This file contains the main code which runs the wizard. Includes all calibrations and all calibration pages
    """
    def __init__(self):
        super (CalibrationWizard, self).__init__()
#         self.depthCamera = Voxel.DepthCamera()
        self.cameraSystem = Voxel.CameraSystem()
        self.devices = self.cameraSystem.scan()
        if self.devices:
            self.depthCamera = self.cameraSystem.connect(self.devices[0])
        else:
            self.depthCamera = None    
        ret, self.profilePath = Voxel.Configuration().getLocalPath('profiles')
        
        self.configPath = os.getcwd() + os.sep +  '..'
#         self.editIndex = editIndex
        self.setMinimumHeight(600)
        self.setMinimumWidth(400)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle('Calibration Wizard')
        self.addPage (CalibrationInitPage(self))
        self.addPage(CalibrationSelectPage(self))
        self.profileName = None
        self.calibs = OrderedDict()
        self.paths = {}
        self.dataCapture = []
        self.pages = {}
        self.calibParams = {}
        self.chipset = None
        
        self.previousConfiguration = []
        self.previousConfigurations = {}
        self.calibPages = [
      ('lens', CalibrationLensPage(self)),  
      ('capture', CalibrationDataCapturePage(self)),
      ('nonLinearity', CalibrationNonLinearityPage(self)), 
      ('temperature', CalibrationTemperaturePage(self)),
      ('commonPhase', CalibrationCommonPhasePage(self)),
      ('hdrCommonPhase', CalibrationHDRCommonPhasePage(self)),
    ('perPixel', CalibrationPerPixelOffsetPage(self))
    ]
        for name, page in self.calibPages:
            self.addCalibrationPage(name, page)
        self.addPage(CalibrationConclusionPage(self))
    def addCalibrationPage(self, name, page):
        self.pages[name] = page
        self.addPage(page)
        
    def setPreviousConfiguration(self, id):
        c = self.depthCamera.configFile.getCameraProfile(id)
    
        if not c:
            QtGui.QMessageBox.critical(self, 'Calibration Wizard', 'Could not get configuration for camera profile "' + self.depthCamera.getCurrentCameraProfileID() + '"')
            return
    
        self.previousConfiguration = Voxel.ConfigurationFile(c)
        self.previousProfileID = self.depthCamera.getCurrentCameraProfileID()
    
    
    def nextId(self):
        id = self.currentId() + 1
        nextPage = self.page(id)
        if not nextPage:
            return -1
        if not isinstance(nextPage, CalibrationPage):
            return id
        while nextPage and not nextPage.doShow:
            id = id + 1
            nextPage = self.page(id)
            if not isinstance(nextPage, CalibrationPage):
                return id
        if not nextPage:
            return -1
        else:
            return id    
        
    def close(self, *args, **kwargs):
        if self.depthCamera:
            self.depthCamera.stop()
a = QtGui.QApplication(sys.argv)
app = CalibrationWizard()
app.show()
a.exec_()

                    