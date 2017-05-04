'''
CommonPhaseOffset.py - takes vxl file as input along with modulation frequency and distance to give phaseCorr values. 
Requires two vxl files - one for each frequency to calculate phase corr 1 and phase corr 2
'''

'''Example Script:
python CommonPhaseOffset.py -f "file.vxl" -d 0.7 -m 20 (-n 10 -g "file2.vxl")
or 
python CommonPhaseOffset.py --file1 "file.vxl" --distance 0.7 --modFreq1 20 (--modFreq2 10 --file2 "file2.vxl")
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
import sys
import Voxel
import argparse

MAX_PHASE_VALUE = 4096
def wrapPhaseToSignedInteger(phase):
   if phase >= MAX_PHASE_VALUE/2:
     return -1*(MAX_PHASE_VALUE - phase)
   elif phase < -MAX_PHASE_VALUE/2:
     return (MAX_PHASE_VALUE + phase)
   else:
     return phase
 
def computeAveragePhases(camsys, filename, cx = 0, cy = 0, window = 4):
    r = Voxel.FrameStreamReader(filename, camsys)
    bool1, cols = r.getStreamParamu("frameWidth")
    bool2, rows = r.getStreamParamu("frameHeight")
    if not cx:
        bool3, cx = r.getStreamParamf("cx")
        if not bool3:
            cx = 0
    if not cy:
        bool4, cy = r.getStreamParamf("cy")
        if not bool4:
            cy = 0
   
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
        averagePhase = np.zeros((window, window), dtype = 'float')
    else:
        averagePhase = np.zeros((rows, cols), dtype = 'float')
    
    for i in np.arange(numFrames):
        if not r.readNext():
            print("Failed to read frame %d" %i)
            break
        tofFrame = Voxel.ToF1608Frame.typeCast(r.frames[Voxel.DepthCamera.FRAME_RAW_FRAME_PROCESSED])
        phase = np.array(tofFrame._phase, copy=True).reshape((rows, cols))\
        [centerShape[0]:centerShape[1], centerShape[2]:centerShape[3]]
        averagePhase += phase
    averagePhase /= numFrames
    if window:
        averagePhase = np.sum(averagePhase)/(window*window)
    
    r.close()
    return averagePhase, rows, cols 

def commonPhaseOffset(file1, distance, modFreq1, cx, cy, file2 = None, modFreq2 = None, window = 4, chipset = 'ti.tinitn'):
    c = 299792458 # m/s
    camsys = Voxel.CameraSystem()
    averagePhase1, rows, cols = computeAveragePhases(camsys, file1, cx, cy, window) #default window size = 4
    ds1 = c/(2*modFreq1*1E6)
    phaseActual1 = distance/ds1*4096
    phaseAverage1 = averagePhase1
    phaseCorr = wrapPhaseToSignedInteger(int(phaseAverage1 - phaseActual1))
    if file2 and modFreq2:
        averagePhase2, rows, cols =  computeAveragePhases(camsys, file2, cx, cy, window)
        ds2 = c/(2*modFreq2*1E6)
        phaseActual2 = distance/ds2*4096
        phaseAverage2 = averagePhase2
        phaseCorr2 = wrapPhaseToSignedInteger(int(phaseAverage2-phaseActual2))
    else:
        phaseCorr2 = 0    
    if chipset == 'ti.calculus': #additive phase
        phaseCorr = -phaseCorr
        phaseCorr2 = -phaseCorr2
    return True, phaseCorr, phaseCorr2, rows, cols
def parseArgs (args = None):
    
    parser = argparse.ArgumentParser(description='Calculate Common Phase Offsets')
    parser.add_argument('-f', '--file1', help = 'Filename1', required = 'True', default= None)
    parser.add_argument('-d', '--distance', type = float, help = 'Distance in meters', required = 'True', default= 0.5)
    parser.add_argument('-m', '--modFreq1', help = 'Modulation Frequency 1', type = float,  required = 'True', default = 40)     
    parser.add_argument('-g', '--file2', help = 'Filename2', default= None)
    parser.add_argument('-n', '--modFreq2', help = 'Modulation Frequency 2', type = float, default = 0)
    parser.add_argument('-x', '--cx', help = 'cx', type = float, default = 0)
    parser.add_argument('-y', '--cy', help = 'cy', type = float, default = 0)
    parser.add_argument('-w', '--window', help = 'Window Size', type = int, default = 4)
    parser.add_argument('-c', '--chipset', help = 'Chipset', default = 'tintin.ti', required = 'True')
    return parser.parse_args(args)

if __name__ == '__main__':
    val = parseArgs(sys.argv[1:])
    
    ret = commonPhaseOffset(val.file1,val.distance, val.modFreq1, val.cx, val.cy, val.file2, val.modFreq2, val.window, val.chipset)
    if not ret:
        print "Cannot compute phase offsets"
        sys.exit()
    boo, phaseCorr1, phaseCorr2, rows, cols = ret
                                               
                                        
    print 'phase_corr_1 = %d\n'%(phaseCorr1)
    print 'phase_corr_2 = %d\n'%(phaseCorr2) 
##    
