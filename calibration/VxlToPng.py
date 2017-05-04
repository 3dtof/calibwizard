
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


import Voxel
import numpy as np 
import sys
import os
import cv2

def vxltoPng(filename):
    """Converts VXL file to a PNG using amplitude data. Uses open cv libraries"""
    camsys = Voxel.CameraSystem()
    r = Voxel.FrameStreamReader(filename, camsys)
    bool1, cols = r.getStreamParamu("frameWidth")
    bool2, rows = r.getStreamParamu("frameHeight")
    if not bool1 or not bool2:
        print ("Cannot read the stream")
    if not r.isStreamGood():
        print("Stream is not good: " + filename)
    numFrames = r.size()
    meanAmplitudes = np.zeros(( rows, cols), dtype='float')
    for i in (range(numFrames)):
        if not r.readNext():
            print("Failed to read frame %d" %i)
            break
        tofFrame = Voxel.ToF1608Frame.typeCast(r.frames[Voxel.DepthCamera.FRAME_RAW_FRAME_PROCESSED])
        meanAmplitudes += np.array(tofFrame._amplitude, copy=True).reshape((rows, cols))
    r.close()
    meanAmplitudes = meanAmplitudes/np.max(meanAmplitudes)*255

    outFileName = os.path.splitext(filename)[0] + '.png' 
    cv2.imwrite(outFileName, meanAmplitudes.astype(np.uint8))
    
if __name__ == "__main__":
    vxltoPng("test.vxl")
    
