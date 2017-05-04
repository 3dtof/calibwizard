
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


import numpy as np
import Voxel

class DataCapture(object):
    
    def __init__(self):
        super (DataCapture, self).__init__()
#         camsys = Voxel.CameraSystem()
        
#  
    def captureData(self, numFrames, fileName):
        camsys = Voxel.CameraSystem()

        CHIPSET_TINTIN = 'tintin.ti'
        CHIPSET_HADDOCK = 'haddock.ti'
        CHIPSET_CALCULUS = 'calculus.ti'
        devices = camsys.scan()
        dev = devices[0]
        self.camera = camsys.connect(dev)
#         if self.camera.isRunning():
#             self.camera.stop()
        self.camera.id()
        self.camera.isInitialized()
        self.camera.clearAllCallbacks()
        self.fileName = fileName
        self.numFrames = numFrames
        self.frameCount = 0

        if not self.camera.saveFrameStream(fileName):
            print "Can't save Data"
        else:        
            self.camera.registerCallback(Voxel.DepthCamera.FRAME_RAW_FRAME_UNPROCESSED, self.callBackFunction)
            self.camera.start()
            self.camera.isRunning()
            self.camera.wait() 
#             print self.frameCount

    def callBackFunction(self, depthCamera, frame, type):
        self.frameCount +=1
#         print self.frameCount
        print 'capturing frame %d'%(self.frameCount)
        if self.frameCount >= self.numFrames:
            print 'data captured'
            self.camera.stop()

if __name__ == '__main__':
    data = DataCapture()
    capture = data.captureData(1, 'tintin10.vxl')