
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

from DataView import DataView

from models.DataEngine import DataFormat

from CustomAction import CustomAction

class DataViewContainer(QtGui.QGroupBox):
  
  def __init__(self, dataEngine, dataFormatName, shouldLinkViewBox = False, showFormatMenu = True, parent = None):
    super(DataViewContainer, self).__init__(parent)
    
    self.dataEngine = dataEngine
    self.statusBar = None
    
    self.shouldLinkViewBox = shouldLinkViewBox
    
    self.setDataFormat(dataFormatName)
    
    if showFormatMenu:
      self.menuActions = []
      self.setContextMenu()
      
      self.dataEngine.statisticsChanged.connect(self.setContextMenu)
      self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    
  def removeAllActions(self):
    if hasattr(self, 'menuActions'):
      for a in self.menuActions:
        self.removeAction(a)
      self.menuActions = []
    
  def setContextMenu(self):
    self.removeAllActions()
    
    df = self.dataEngine.getDataFormats()
    
    for d in df:
      a = CustomAction(self.dataEngine.dataFormats[d].title, d, self)
      a.triggeredObject.connect(self.setDataFormat)
      self.addAction(a)
      self.menuActions.append(a)
      
  def setStatusBar(self, statusBar):
    self.statusBar = statusBar
    
    if hasattr(self, 'dataView'):
      self.dataView.setStatusBar(self.statusBar)
      
  def setDataFormat(self, dataFormatName):
    
    if not self.dataEngine.dataFormats.has_key(dataFormatName):
      QtGui.QMessageBox('DataView failed', 'Failed to show data of format "' + dataFormatName + '"')
    
    self.dataFormat = self.dataEngine.dataFormats[dataFormatName]
    
    self.setTitle(self.dataFormat.title)
    
    if hasattr(self, 'dataView') and self.dataView.dataFormat.dataType == self.dataFormat.dataType:
      #self.dataView.unlink()
      #QtGui.QWidget().setLayout(self.layout)
      #print 'Linking new data...'
      self.dataView.setDataFormat(self.dataFormat)
    else:
      
      if hasattr(self, 'dataView'):
        self.dataView.cleanup()
        QtGui.QWidget().setLayout(self.layout)
      
      self.layout = QtGui.QVBoxLayout()
      self.dataView = DataView.getDataView(self.dataFormat, self.dataEngine)
      if self.statusBar:
        self.dataView.setStatusBar(self.statusBar)
        
      self.layout.addWidget(self.dataView)
      self.setLayout(self.layout)
      
      if self.dataFormat.dataType == DataFormat.DATA_2D and self.shouldLinkViewBox:
        self.dataView.linkViewBox()
    