
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

import pyqtgraph

import numpy as np

class CustomViewBox(pyqtgraph.ViewBox):
  
  resetView = QtCore.Signal()
  autoHistogram = QtCore.Signal()
  histogramToggle = QtCore.Signal()
  export = QtCore.Signal()
  
  def __init__(self):
    super(CustomViewBox, self).__init__()
    self.setMouseMode(pyqtgraph.ViewBox.RectMode)
    self.invertY()
    self.setAspectLocked(True)
    
  def mouseDragEvent(self, ev, axis = None):
    ## if axis is specified, event will only affect that axis.
    ev.accept()  ## we accept all buttons
    
    pos = ev.pos()
    lastPos = ev.lastPos()
    dif = pos - lastPos
    dif = dif * -1

    ## Ignore axes if mouse is disabled
    mouseEnabled = np.array(self.state['mouseEnabled'], dtype=np.float)
    mask = mouseEnabled.copy()
    if axis is not None:
      mask[1 - axis] = 0.0

    ## Scale or translate based on mouse button
    if (ev.button() & QtCore.Qt.LeftButton) and (ev.modifiers() & QtCore.Qt.ShiftModifier):
      tr = dif*mask
      tr = self.mapToView(tr) - self.mapToView(pyqtgraph.Point(0,0))
      x = tr.x() if mask[0] == 1 else None
      y = tr.y() if mask[1] == 1 else None
      
      self.translateBy(x = x, y = y)
      self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
    else:
      super(CustomViewBox, self).mouseDragEvent(ev, axis)
      
  def setMenu(self, menu):
    self.menu = menu
    
  def raiseContextMenu(self, ev):
    menu = self.getMenu(ev)
    #self.scene().addParentContextMenus(self, menu, ev) -- Not adding parent's context menus
    menu.popup(ev.screenPos().toPoint())
      
  def keyPressEvent(self, ev):
    if ev.key() == QtCore.Qt.Key_R:
      self.resetView.emit()
      ev.accept()
    elif ev.key() == QtCore.Qt.Key_A:
      self.autoHistogram.emit()
      ev.accept()
    elif ev.key() == QtCore.Qt.Key_H:
      self.histogramToggle.emit()
      ev.accept()
    elif ev.key() == QtCore.Qt.Key_E:
      self.export.emit()
      ev.accept()  
    
    else:
      super(CustomViewBox, self).keyPressEvent(ev)
    