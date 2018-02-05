'''
This file calculates the phase offsets and saves it as an npy file.
It also returns the bin file of the offsets. 
Usage:
python PerPixelOffset.py -f "file.vxl" -n "profileName" -m 0
or 
python PerPixelOffset.py --file "file.vxl" --name "profileName" --mask 0

'''

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
import struct
import Voxel
import cv2
import argparse
import sys
import os

def computeAveragePhases(camsys, filename, window = 0):
    """Returns the average phases for all pixels for a given file"""
    r = Voxel.FrameStreamReader(filename, camsys)
    bool1, cols = r.getStreamParamu("frameWidth")
    bool2, rows = r.getStreamParamu("frameHeight")
    _, cx = r.getStreamParamf('cx')
    _, cy = r.getStreamParamf('cy')
    _,fx = r.getStreamParamf('fx')
    _, fy = r.getStreamParamf('fy')
    _, k1 = r.getStreamParamf('k1')
    _, k2 = r.getStreamParamf('k2')
    _, k3 = r.getStreamParamf('k3')
    _, p1 = r.getStreamParamf('p1')
    _, p2 = r.getStreamParamf('p2')
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
    dist = np.array([k1, k2, p1, p2, k3])
    mtx  = np.array([[fy, 0 , cy], [0, fx, cx], [0, 0 ,1]])
    return averagePhase, rows, cols, mtx, dist

MAX_PHASE_VALUE = 4096
PHASE_FILENAME = 'per-pixel-offset.npy'
PHASE_OFFSET_FILE = 'phaseOffset.bin'

def wrapPhaseToSignedInteger(phase):
    if phase >= MAX_PHASE_VALUE/2:
        return -1*(MAX_PHASE_VALUE - phase)
    elif phase < -MAX_PHASE_VALUE/2:
        return (MAX_PHASE_VALUE + phase)
    else:
        return phase

def perPixelOffset(fileName, dealiasedPhaseMask = 0, pathToSave= None, profileName = None):
    """Computes pixelwise phase offset for all pixels. Returns a numpy file containing the pixelwise offsets as well as the bin file
    
    .. note: Copy the bin file to the /path/to/.voxel/conf folder path before using it in the conf file
    """
    camsys = Voxel.CameraSystem()
    if not profileName:
        profileName = os.path.basename(fileName).split('.')[0]
    ret = computeAveragePhases(camsys, fileName, 0)
    if not ret:
        print "Can't calculate the phase offsets. Check file"
        sys.exit()
    else:
        phases, rows, cols, mtx, dist = ret
    if pathToSave is None:
        newFile = os.path.splitext(fileName)[0] + PHASE_FILENAME
    else:
        newFile = pathToSave + profileName + PHASE_FILENAME
    np.save(newFile, phases.T)
    phases2 = phases.T
    cGrid = np.mgrid[0:rows,0:cols].astype(np.float32)
    cGrid1D = np.reshape(np.transpose(cGrid, (1, 2, 0)), (rows*cols, 1, 2)).astype(np.float32)
    cGridCorrected1D = cv2.undistortPoints(cGrid1D, mtx, dist)
    cGridCorrected = np.transpose(np.reshape(cGridCorrected1D, (rows, cols, 2)), (2, 0, 1))
    ry = cGridCorrected[0]
    rx = cGridCorrected[1]
    # Uncomment to get undistortion mapping
    #with open('temp2.txt', 'w') as f:
      #for r in range(0, self.rows):
        #for c in range(0, self.columns):
          #f.write('(%d, %d) -> (%.2f, %.2f)\n'%(self.cGrid[1, r, c], self.cGrid[0, r, c], rx[r, c], ry[r, c]))
        
    rad2DSquare = ((rx**2) + (ry**2))

    cosA = 1/((rad2DSquare + 1)**0.5)
    
    deltaPhase = phases - phases[int(mtx[0,2]), int(mtx[1,2])]/cosA
    if pathToSave is None:
        phaseOffsetFileName = os.path.splitext(fileName)[0] + PHASE_OFFSET_FILE
    else:
        phaseOffsetFileName = pathToSave + os.sep + profileName +PHASE_OFFSET_FILE
    with open (phaseOffsetFileName, 'wb') as f:
        f.write(struct.pack('H', rows))
        f.write(struct.pack('H', cols))
        f.write(struct.pack('H', np.uint16(dealiasedPhaseMask) & 0x000f))
        np.reshape(deltaPhase, rows*cols).astype(np.short).tofile(f)    
    return True, phaseOffsetFileName, rows, cols

def parseArgs (args = None):
    parser = argparse.ArgumentParser(description='Calculate Per Pixel Offsets')
    parser.add_argument('-f', '--file', help = 'Filename', required = 'True', default= None)
    parser.add_argument('-n', '--name', help = 'Profile Name', default = None, required = False)
    parser.add_argument('-m', '--mask', help = 'Dealiased Phase Mask', required = True, type = int)
    return parser.parse_args(args)    

if __name__ == '__main__':
    val = parseArgs(sys.argv[1:])
    ret = perPixelOffset(val.file, dealiasedPhaseMask = val.mask,  profileName=val.name)
    if not ret:
        print "Can't compute the phase offsets"
        sys.exit()
    boo, text, rows, cols = ret
    print ("Successfully saved the offsets to " + text)
