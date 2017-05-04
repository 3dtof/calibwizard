
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
#  -- Borrowed from https://github.com/mkilling/QxtSpanSlider.py with modifications (MIT license)


from PySide.QtCore import QRect, QPoint
from PySide.QtGui import QWidget, QAbstractSlider, QSlider, QStyle, QGridLayout, QLabel, QDoubleSpinBox, QGridLayout, QStylePainter, QStyleOption, QStyleOptionSlider, QPen, QPalette, QLinearGradient, QStyleFactory
from PySide import QtCore, QtGui

def clamp(v, lower, upper):
    return min(upper, max(lower, v))

class QxtSpanSlider(QSlider):
    NoHandle = None
    LowerHandle = 1
    UpperHandle = 2
    
    FreeMovement = None
    NoCrossing = 1
    NoOverlapping = 2
    
    spanChanged = QtCore.Signal(int, int)
    lowerValueChanged = QtCore.Signal(int)
    upperValueChanged = QtCore.Signal(int)
    lowerPositionChanged = QtCore.Signal(int)
    upperPositionChanged = QtCore.Signal(int)
    floatLowerPositionChanged = QtCore.Signal(float)
    floatUpperPositionChanged = QtCore.Signal(float)
    sliderPressed = QtCore.Signal(object)
    
    def __init__(self, parent = None):
        QSlider.__init__(self, QtCore.Qt.Horizontal, parent)
        self.rangeChanged.connect(self.updateRange)
        self.sliderReleased.connect(self.movePressedHandle)
        
        self.setStyle(QStyleFactory.create('Plastique'))
        
        
        self.floatMin = 0
        self.floatMax = 0
        self.floatStep = 0
        
        self.lower = 0
        self.upper = 0
        self.lowerPos = 0
        self.upperPos = 0
        self.offset = 0
        self.position = 0
        self.lastPressed = QxtSpanSlider.NoHandle
        self.upperPressed = QStyle.SC_None
        self.lowerPressed = QStyle.SC_None
        self.movement = QxtSpanSlider.FreeMovement
        self.mainControl = QxtSpanSlider.LowerHandle
        self.firstMovement = False
        self.blockTracking = False
        p = self.palette()
        p.setColor(QPalette.Dark, QtGui.QColor('black'))
        self.setPalette(p)
        self.gradientLeft = self.palette().color(QPalette.Dark).lighter(100)
        self.gradientRight = self.palette().color(QPalette.Dark).darker(200)
        
    def setFloatRange(self, min, max, step):
        self.floatMin = min
        self.floatMax = max
        self.floatStep = step
        try:
            self.setRange(min/step, max/step)
            self.setSpan(min/step, max/step)
            self.updateToolTip()
        except RuntimeError:
            pass

    def updateToolTip(self):
        if self.floatStep != 0:
            self.message = "Current = [%f, %f], Maximum = [%f, %f]"%(self.lowerPos*self.floatStep, self.upperPos*self.floatStep, self.minimum()*self.floatStep, self.maximum()*self.floatStep)
        else:
            self.message = "Current = [%d, %d], Maximum = [%d, %d]"%(self.lowerPos, self.upperPos, self.minimum(), self.maximum())
        self.setToolTip(self.message)

    def lowerValue(self):
        return min(self.lower, self.upper)
        
    @QtCore.Slot(int)
    def setLowerValue(self, lower):
        self.setSpan(lower, self.upper)
        
    def upperValue(self):
        return max(self.lower, self.upper)
        
    @QtCore.Slot(int)
    def setUpperValue(self, upper):
        self.setSpan(self.lower, upper)

    def handleMovementMode(self):
        return self.movement
    
    def setHandleMovementMode(self, mode):
        self.movement = mode

    @QtCore.Slot(int, int)
    def setSpan(self, lower, upper):
        low = clamp(min(lower, upper), self.minimum(), self.maximum())
        upp = clamp(max(lower, upper), self.minimum(), self.maximum())
        changed = False
        if low != self.lower:
            self.lower = low
            self.lowerPos = low
            changed = True
        if upp != self.upper:
            self.upper = upp
            self.upperPos = upp
            changed = True
        if changed:
            self.updateToolTip()
            self.spanChanged.emit(self.lower, self.upper)
            self.update()

    def lowerPosition(self):
        return self.lowerPos

    @QtCore.Slot(int)
    def setLowerPosition(self, lower):
        if self.lowerPos != lower:
            lower = clamp(lower, self.minimum(), self.maximum())
            self.lowerPos = lower
            self.updateToolTip()
            if not self.hasTracking():
                self.update()
            if self.isSliderDown():
                self.lowerPositionChanged.emit(lower)
                if self.floatStep != 0:
                    self.floatLowerPositionChanged.emit(lower*self.floatStep)
                    
            if self.hasTracking() and not self.blockTracking:
                main = (self.mainControl == QxtSpanSlider.LowerHandle)
                self.triggerAction(QxtSpanSlider.SliderMove, main)

    def upperPosition(self):
        return self.upperPos

    @QtCore.Slot(int)
    def setUpperPosition(self, upper):
        if self.upperPos != upper:
            upper = clamp(upper, self.minimum(), self.maximum())
            self.upperPos = upper
            self.updateToolTip()
            if not self.hasTracking():
                self.update()
            if self.isSliderDown():
                self.upperPositionChanged.emit(upper)
                if self.floatStep != 0:
                    self.floatUpperPositionChanged.emit(upper*self.floatStep)
            if self.hasTracking() and not self.blockTracking:
                main = (self.mainControl == QxtSpanSlider.UpperHandle)
                self.triggerAction(QxtSpanSlider.SliderMove, main)

    def gradientLeftColor(self):
        return self.gradientLeft
    
    @QtCore.Slot(object)
    def setGradientLeftColor(self, color):
        self.gradientLeft = color
        self.update()
    
    def gradientRightColor(self):
        return self.gradientRight
    
    @QtCore.Slot(object)
    def setGradientRightColor(self, color):
        self.gradientRight = color
        self.update()
    
    @QtCore.Slot()
    def movePressedHandle(self):
        if self.lastPressed == QxtSpanSlider.LowerHandle:
            if self.lowerPos != self.lower:
                main = (self.mainControl == QxtSpanSlider.LowerHandle)
                self.triggerAction(QAbstractSlider.SliderMove, main)
        elif self.lastPressed == QxtSpanSlider.UpperHandle:
            if self.upperPos != self.upper:
                main = (self.mainControl == QxtSpanSlider.UpperHandle)
                self.triggerAction(QAbstractSlider.SliderMove, main)

    def pick(self, p):
        if self.orientation() == QtCore.Qt.Horizontal:
            return p.x()
        else:
            return p.y()
    
    def triggerAction(self, action, main):
        value = 0
        no = False
        up = False
        my_min = self.minimum()
        my_max = self.maximum()
        altControl = QxtSpanSlider.LowerHandle
        if self.mainControl == QxtSpanSlider.LowerHandle:
            altControl = QxtSpanSlider.UpperHandle

        self.blockTracking = True
        
        isUpperHandle = (main and self.mainControl == QxtSpanSlider.UpperHandle) or (not main and altControl == QxtSpanSlider.UpperHandle)
        
        if action == QAbstractSlider.SliderSingleStepAdd:
            if isUpperHandle:
                value = clamp(self.upper + self.singleStep(), my_min, my_max)
                up = True
            else:
                value = clamp(self.lower + self.singleStep(), my_min, my_max)
        elif action == QAbstractSlider.SliderSingleStepSub:
            if isUpperHandle:
                value = clamp(self.upper - self.singleStep(), my_min, my_max)
                up = True
            else:
                value = clamp(self.lower - self.singleStep(), my_min, my_max)
        elif action == QAbstractSlider.SliderToMinimum:
            value = my_min
            if isUpperHandle:
                up = True
        elif action == QAbstractSlider.SliderToMaximum:
            value = my_max
            if isUpperHandle:
                up = True
        elif action == QAbstractSlider.SliderMove:
            if isUpperHandle:
                up = True
            no = True
        elif action == QAbstractSlider.SliderNoAction:
            no = True

        if not no and not up:
            if self.movement == QxtSpanSlider.NoCrossing:
                value = min(value, self.upper)
            elif self.movement == QxtSpanSlider.NoOverlapping:
                value = min(value, self.upper - 1)

            if self.movement == QxtSpanSlider.FreeMovement and value > self.upper:
                self.swapControls()
                self.setUpperPosition(value)
            else:
                self.setLowerPosition(value)
        elif not no:
            if self.movement == QxtSpanSlider.NoCrossing:
                value = max(value, self.lower)
            elif self.movement == QxtSpanSlider.NoOverlapping:
                value = max(value, self.lower + 1)

            if self.movement == QxtSpanSlider.FreeMovement and value < self.lower:
                self.swapControls()
                self.setLowerPosition(value)
            else:
                self.setUpperPosition(value)

        self.blockTracking = False
        self.setLowerValue(self.lowerPos)
        self.setUpperValue(self.upperPos)
    
    def swapControls(self):
        self.lower, self.upper = self.upper, self.lower
        self.lowerPressed, self.upperPressed = self.upperPressed, self.lowerPressed

        if self.lastPressed == QxtSpanSlider.LowerHandle:
            self.lastPressed = QxtSpanSlider.UpperHandle
        else:
            self.lastPressed = QxtSpanSlider.LowerHandle
            
        if self.mainControl == QxtSpanSlider.LowerHandle:
            self.mainControl = QxtSpanSlider.UpperHandle
        else:
            self.mainControl = QxtSpanSlider.LowerHandle

    @QtCore.Slot(int, int)
    def updateRange(self, min, max):
        # setSpan() takes care of keeping span in range
        self.setSpan(self.lower, self.upper)
    
    def paintEvent(self, event):
        painter = QStylePainter(self)
        
        # ticks
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.subControls = QStyle.SC_SliderTickmarks
        painter.drawComplexControl(QStyle.CC_Slider, opt)

        # groove
        opt.sliderPosition = 20
        opt.sliderValue = 0
        opt.subControls = QStyle.SC_SliderGroove
        painter.drawComplexControl(QStyle.CC_Slider, opt)

        # handle rects
        opt.sliderPosition = self.lowerPos
        lr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        lrv  = self.pick(lr.center())
        opt.sliderPosition = self.upperPos
        ur = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        urv  = self.pick(ur.center())

        # span
        minv = min(lrv, urv)
        maxv = max(lrv, urv)
        c = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self).center()
        spanRect = QRect(QPoint(c.x() - 2, minv), QPoint(c.x() + 1, maxv))
        if self.orientation() == QtCore.Qt.Horizontal:
            spanRect = QRect(QPoint(minv, c.y() - 2), QPoint(maxv, c.y() + 1))
        self.drawSpan(painter, spanRect)

        # handles
        if self.lastPressed == QxtSpanSlider.LowerHandle:
            self.drawHandle(painter, QxtSpanSlider.UpperHandle)
            self.drawHandle(painter, QxtSpanSlider.LowerHandle)
        else:
            self.drawHandle(painter, QxtSpanSlider.LowerHandle)
            self.drawHandle(painter, QxtSpanSlider.UpperHandle)

    def setupPainter(self, painter, orientation, x1, y1, x2, y2):
        highlight = self.palette().color(QPalette.Highlight)
        gradient = QLinearGradient(x1, y1, x2, y2)
        gradient.setColorAt(0, highlight.darker(120))
        gradient.setColorAt(1, highlight.lighter(108))
        painter.setBrush(gradient)

        if orientation == QtCore.Qt.Horizontal:
            painter.setPen(QPen(highlight.darker(130), 0))
        else:
            painter.setPen(QPen(highlight.darker(150), 0))

    def drawSpan(self, painter, rect):
        opt = QStyleOptionSlider()
        QSlider.initStyleOption(self, opt)

        # area
        groove = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        if opt.orientation == QtCore.Qt.Horizontal:
            groove.adjust(0, 0, -1, 0);
        else:
            groove.adjust(0, 0, 0, -1);

        # pen & brush
        painter.setPen(QPen(self.gradientLeftColor, 0))
        if opt.orientation == QtCore.Qt.Horizontal:
            self.setupPainter(painter, opt.orientation, groove.center().x(), groove.top(), groove.center().x(), groove.bottom())
        else:
            self.setupPainter(painter, opt.orientation, groove.left(), groove.center().y(), groove.right(), groove.center().y())

        # draw groove
        intersected = QtCore.QRectF(rect.intersected(groove))
        gradient = QLinearGradient(intersected.topLeft(), intersected.topRight())
        gradient.setColorAt(0, self.gradientLeft)
        gradient.setColorAt(1, self.gradientRight)
        painter.fillRect(intersected, gradient)
    
    def drawHandle(self, painter, handle):
        opt = QStyleOptionSlider()
        self._initStyleOption(opt, handle)
        opt.subControls = QStyle.SC_SliderHandle
        pressed = self.upperPressed
        if handle == QxtSpanSlider.LowerHandle:
            pressed = self.lowerPressed
        
        if pressed == QStyle.SC_SliderHandle:
            opt.activeSubControls = pressed
            opt.state |= QStyle.State_Sunken
        painter.drawComplexControl(QStyle.CC_Slider, opt)
    
    def _initStyleOption(self, option, handle):
        self.initStyleOption(option)

        option.sliderPosition = self.upperPos
        if handle == QxtSpanSlider.LowerHandle:
            option.sliderPosition = self.lowerPos

        option.sliderValue = self.upper
        if handle == QxtSpanSlider.LowerHandle:
            option.sliderPosition = self.lower
    
    def handleMousePress(self, pos, control, value, handle):
        opt = QStyleOptionSlider()
        self._initStyleOption(opt, handle)
        oldControl = control
        control = self.style().hitTestComplexControl(QStyle.CC_Slider, opt, pos, self)
        sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        if control == QStyle.SC_SliderHandle:
            self.position = value
            self.offset = self.pick(pos - sr.topLeft())
            self.lastPressed = handle
            self.setSliderDown(True)
            self.sliderPressed.emit(handle)
        if control != oldControl:
            self.update(sr)
        return control
    
    def mousePressEvent(self, event):
        if self.minimum() == self.maximum() or event.buttons() ^ event.button():
            event.ignore()
            return

        self.upperPressed = self.handleMousePress(event.pos(), self.upperPressed, self.upper, QxtSpanSlider.UpperHandle)
        if self.upperPressed != QStyle.SC_SliderHandle:
            self.lowerPressed = self.handleMousePress(event.pos(), self.lowerPressed, self.lower, QxtSpanSlider.LowerHandle)

        self.firstMovement = True
        event.accept()
    
    def mouseMoveEvent(self, event):
        if self.lowerPressed != QStyle.SC_SliderHandle and self.upperPressed != QStyle.SC_SliderHandle:
            event.ignore()
            return

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        m = self.style().pixelMetric(QStyle.PM_MaximumDragDistance, opt, self)
        newPosition = self.pixelPosToRangeValue(self.pick(event.pos()) - self.offset)
        if m >= 0:
            r = self.rect().adjusted(-m, -m, m, m)
            if not r.contains(event.pos()):
                newPosition = self.position

        # pick the preferred handle on the first movement
        if self.firstMovement:
            if self.lower == self.upper:
                if newPosition < self.lowerValue:
                    self.swapControls()
                    self.firstMovement = False
            else:
                self.firstMovement = False

        if self.lowerPressed == QStyle.SC_SliderHandle:
            if self.movement == QxtSpanSlider.NoCrossing:
                newPosition = min(newPosition, self.upper)
            elif self.movement == QxtSpanSlider.NoOverlapping:
                newPosition = min(newPosition, self.upper - 1)

            if self.movement == QxtSpanSlider.FreeMovement and newPosition > self.upper:
                self.swapControls()
                self.setUpperPosition(newPosition)
            else:
                self.setLowerPosition(newPosition)
        elif self.upperPressed == QStyle.SC_SliderHandle:
            if self.movement == QxtSpanSlider.NoCrossing:
                newPosition = max(newPosition, self.lowerValue)
            elif self.movement == QxtSpanSlider.NoOverlapping:
                newPosition = max(newPosition, self.lowerValue + 1);

            if self.movement == QxtSpanSlider.FreeMovement and newPosition < self.lower:
                self.swapControls()
                self.setLowerPosition(newPosition)
            else:
                self.setUpperPosition(newPosition)
        event.accept()
    
    def mouseReleaseEvent(self, event):
        QSlider.mouseReleaseEvent(self, event)
        self.setSliderDown(False)
        self.lowerPressed = QStyle.SC_None
        self.upperPressed = QStyle.SC_None
        self.update()
    
    def pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        sliderMin = 0
        sliderMax = 0
        sliderLength = 0
        gr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        if self.orientation() == QtCore.Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), pos - sliderMin, sliderMax - sliderMin, opt.upsideDown)
    
    lowerValue = QtCore.Property("int", lowerValue, setLowerValue)
    upperValue = QtCore.Property("int", upperValue, setUpperValue)
    upperPosition = QtCore.Property("int", upperPosition, setUpperPosition)
    lowerPosition = QtCore.Property("int", lowerPosition, setLowerPosition)
    handleMovementMode = QtCore.Property("PyQt_PyObject", handleMovementMode, setHandleMovementMode)
    gradientLeftColor = QtCore.Property("PyQt_PyObject", gradientLeftColor, setGradientLeftColor)
    gradientRightColor = QtCore.Property("PyQt_PyObject", gradientRightColor, setGradientRightColor)

