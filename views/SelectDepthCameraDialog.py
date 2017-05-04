
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
#

from PySide import QtGui, QtCore

class SelectDepthCameraDialog(QtGui.QDialog):
  def __init__(self, cameraSystem, parent = None):
    super(SelectDepthCameraDialog, self).__init__(parent)

    self.setWindowTitle('Select Depth Camera')
    self.cameraSystem = cameraSystem

    layout = QtGui.QVBoxLayout(self)

    # nice widget for editing the date
    self.listview = QtGui.QListWidget()
    layout.addWidget(self.listview)

    # OK and Cancel buttons
    buttons = QtGui.QDialogButtonBox(self)
    
    self.okButton = QtGui.QPushButton("&Ok", self)
    self.refreshButton = QtGui.QPushButton("&Refresh", self)
    
    self.refreshButton.clicked.connect(self.populateList)
    
    self.listview.setSelectionMode(QtGui.QListWidget.SingleSelection)
        
    buttons.addButton(self.okButton, QtGui.QDialogButtonBox.AcceptRole)
    buttons.addButton(self.refreshButton, QtGui.QDialogButtonBox.ResetRole)
    
    buttons.accepted.connect(self.accept)
    buttons.rejected.connect(self.reject)
    layout.addWidget(buttons)
    
    self.populateList()

  # get current date and time from the dialog
  def getDepthCamera(self):
    return self.cameraSystem.connect(self.devices[self.listview.currentRow()])
  
  @QtCore.Slot()
  def populateList(self):
    self.devices = self.cameraSystem.scan()
    
    names = []
    for d in self.devices:
      names.append(d.description() + " (" + d.id() + ")") ## Assuming that description is present for all devices
    
    self.listview.clear()
    
    if len(names) > 0:
      self.listview.addItems(names)
      self.listview.setCurrentRow(0)
      self.okButton.setEnabled(True)
    else:
      self.okButton.setDisabled(True)
    

  # static method to create the dialog and return (date, time, accepted)
  @staticmethod
  def showDialog(cameraSystem, parent = None):
    dialog = SelectDepthCameraDialog(cameraSystem, parent)
    result = dialog.exec_()
    
    if result == QtGui.QDialog.Accepted:
      return dialog.getDepthCamera()
    else:
      return None