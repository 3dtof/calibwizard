import numpy as np
import sys
import Voxel


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


def computeAveragePhases(camsys, filename, cx = 0, cy = 0, window = 4):
    r = Voxel.FrameStreamReader(filename, camsys)
    bool1, cols = r.getStreamParamu("frameWidth")
    bool2, rows = r.getStreamParamu("frameHeight")
    cx = int(cx)
    cy = int(cy)
    if cx == 0:
        cx = rows/2
    if cy == 0:
        cy = cols/2
    if window:
        centerShape = [cx-window/2, cx+window/2, cy-window/2, cy+window/2]
    else: 
        centerShape = [0, rows, 0, cols]        
    if not r.isStreamGood() or not bool1 or not bool2:
        print("Stream is not good: " + filename)
    numFrames = r.size()
    if window:
        averagePhase = np.zeros((window, window), dtype = 'complex')
    else:
        averagePhase = np.zeros((rows, cols), dtype = 'complex')
    
    for i in np.arange(numFrames):
        if not r.readNext():
            print("Failed to read frame %d" %i)
            break
        tofFrame = Voxel.ToF1608Frame.typeCast(r.frames[Voxel.DepthCamera.FRAME_RAW_FRAME_PROCESSED])
        phase = np.array(tofFrame._phase, copy=True).reshape((rows, cols))\
        [centerShape[0]:centerShape[1], centerShape[2]:centerShape[3]]*2*np.pi/4096
        amplitude = np.array(tofFrame._amplitude, copy = True).reshape((rows,cols))\
        [centerShape[0]:centerShape[1], centerShape[2]:centerShape[3]]
        averagePhase += amplitude*(np.cos(phase)+ 1j*np.sin(phase))
    averagePhase /= numFrames
    if window:
        averagePhase = np.sum(averagePhase)/(window*window)
        if averagePhase <0:
            averagePhase += 4096
    averagePhase = np.angle(averagePhase)* 4096/(2*np.pi)
    
    r.close()
    return averagePhase, rows, cols

if __name__ == "__main__":
    camsys = Voxel.CameraSystem()
    if len(sys.argv) != 5:
        print("Usage: computeAveragePhases.py inFile.vxl cx cy, window")
        sys.exit()
    
    inFileName = sys.argv[1]
    cx = float(sys.argv[2])
    cy = int(sys.argv[3])
    window = int(sys.argv[4])
    
    averagePhase, _, _ = computeAveragePhases(camsys, inFileName, cx, cy, window)
    print (averagePhase)
