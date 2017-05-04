
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

from pyqtgraph.graphicsItems.PlotDataItem import dataType

import numpy as np

import weakref

class CustomHistogramLUTWidget(pyqtgraph.HistogramLUTWidget):
  
  resetView = QtCore.Signal()
  autoHistogram = QtCore.Signal()
  histogramToggle = QtCore.Signal()
  export = QtCore.Signal()
  
  def __init__(self, parent = None, fillHistogram = True):
    super(CustomHistogramLUTWidget, self).__init__(parent = parent, fillHistogram = fillHistogram)
    self.vb.setMouseEnabled(x=False, y=False) # Disable zoom in viewbox
    self.item.gradientChanged = self.gradientChanged
    
    # Disable right click and other mouse events on gradient
    self.gradient.mouseClickEvent = self.gradientMouseClickEvent 
    #self.plot.setData = self.setData
    
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
      super(CustomHistogramLUTWidget, self).keyPressEvent(ev)

  def gradientMouseClickEvent(self, ev):
    pass
  
  def setImageItem(self, img):
    if self.item.imageItem() is not None:
      self.item.imageItem().sigImageChanged.disconnect(self.imageChanged)
    
    if img is not None:
      self.item.imageItem = weakref.ref(img)
      img.sigImageChanged.connect(self.imageChanged)
    else:
      self.item.imageItem = lambda: None
      
  def setMenu(self, menu):
    self.item.vb.menu = menu
    
  def gradientChanged(self):
    pass
    
  @QtCore.Slot()
  def imageChanged(self, autoLevel=False, autoRange=False):
    h = self.imageItem().getHistogram(bins = 100)
    if h[0] is None:
        return
    self.plot.setData(*h)
    
  def setData(self, *args, **kargs):
    self.updateItems(args[0], args[1])
    self.plot.informViewBoundsChanged()
    self.plot.sigPlotChanged.emit(self.plot)
    
  def updateItems(self, x, y):
    curveArgs = {}
    for k,v in [('pen','pen'), ('shadowPen','shadowPen'), ('fillLevel','fillLevel'), ('fillBrush', 'brush'), ('antialias', 'antialias'), ('connect', 'connect'), ('stepMode', 'stepMode')]:
        curveArgs[v] = self.plot.opts[k]
    
    if curveArgs['pen'] is not None or (curveArgs['brush'] is not None and curveArgs['fillLevel'] is not None):
        self.plot.curve.setData(x=x, y=y, **curveArgs)
        self.plot.curve.show()
    else:
        self.plot.curve.hide()