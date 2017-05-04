'''
HDRcommonPhaseOffset.py - takes vxl file as input along with modulation frequency and distance to give phaseCorr values. 
Requires two vxl files - one for each frequency to calculate phase corr 1 and phase corr 2
Make sure that hdr_scale is greater than zero before recording the vxl (only works for tintin at this point of time)
'''

'''Example Script:
python HDRcommonphaseoffset.py -f "file.vxl" -d 0.7 -m 20 (-n 10 -g "file2.vxl")
or 
python HDRcommonphaseoffset.py --file1 "file.vxl" --distance 0.7 --modFreq1 20 (--modFreq2 10 --file2 "file2.vxl")
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
from numpy import dtype
import argparse

def computeHDRAveragePhases(camsys, filename, cx = 0, cy = 0, window = 4, chipset = 'tintin.ti'):
    """ Computes average phases for the HDR frame"""
    r = Voxel.FrameStreamReader(filename, camsys)
    _, cols = r.getStreamParamu("frameWidth")
    _, rows = r.getStreamParamu("frameHeight")
    if not cx:
        _, cx = r.getStreamParamf('cx')
    if not cy:
        _, cy = r.getStreamParamf('cy')
    cx = int(cx)
    cy = int(cy)
    if cx == 0:
        cx = rows/2
    if cy == 0:
        cy = cols/2
    if window:
        centerShape = [cx-window/2, cx+window/2, cy-window/2, cy+window/2]
        averagePhase = np.zeros((window, window), dtype = 'complex')
    else: 
        centerShape = [0, rows, 0, cols]        
        averagePhase = np.zeros((rows, cols), dtype = 'complex')
    if not r.isStreamGood():
        print("Stream is not good: " + filename)
        
    numFrames = r.size()
    if chipset == 'tintin.ti':
        for i in np.arange(numFrames):
            if not r.readNext():
                print("Failed to read frame %d" %i)
                break
            tofFrame = Voxel.ToF1608Frame.typeCast(r.frames[Voxel.DepthCamera.FRAME_RAW_FRAME_PROCESSED])
            flag = np.array(tofFrame._flags, copy=True)[0]
            if flag == 0x04:
                phase = np.array(tofFrame._phase, copy=True).reshape((rows, cols))\
                [centerShape[0]:centerShape[1], centerShape[2]:centerShape[3]]*2*np.pi/4096
                averagePhase += np.array(tofFrame._amplitude, copy = True).reshape((rows,cols))\
                [centerShape[0]:centerShape[1], centerShape[2]:centerShape[3]]*(np.cos(phase)+ 1j*np.sin(phase))
        if np.sum(np.absolute(averagePhase))==0:
            print ("no HDR frames received")
            return False, 0,0,0
        averagePhase /= numFrames
        if window:
            averagePhase = np.sum(averagePhase)/(window*window)
        averagePhase = np.angle(averagePhase)* 4096/(2*np.pi)
        r.close()
    if chipset == 'calculus.ti':
        tofFrame = Voxel.ToF1608Frame.typeCast(r.frames[Voxel.DepthCamera.FRAME_RAW_FRAME_PROCESSED])
        flagFirst = np.array(tofFrame._flags, copy = True)[0]
        amplitudeFirst = np.array(tofFrame._amplitude, copy = True)
        if  not r.readNext():
            print("Failed to read frame 2")
        flagSecond = np.array(tofFrame._flags, copy = True)[0]
        amplitudeSecond = np.array(tofFrame._amplitude, copy = True)
        if np.mean(amplitudeFirst) > np.mean(amplitudeSecond):
            flagVal = flagSecond
        else:
            flagVal = flagFirst
        if flagVal == 0x02 or flagVal == 0x03:
            flagVal = flagVal -2
        for i in np.arange(numFrames):
            if not r.readNext():
                print("Failed to read frame %d" %i)
                break
            tofFrame = Voxel.ToF1608Frame.typeCast(r.frames[Voxel.DepthCamera.FRAME_RAW_FRAME_PROCESSED])
            flag = np.array(tofFrame._flags, copy=True)[0]
            if flag == flagVal or flag == flagVal+2:
                phase = np.array(tofFrame._phase, copy=True).reshape((rows, cols))\
                [centerShape[0]:centerShape[1], centerShape[2]:centerShape[3]]*2*np.pi/4096
                averagePhase += np.array(tofFrame._amplitude, copy = True).reshape((rows,cols))\
                [centerShape[0]:centerShape[1], centerShape[2]:centerShape[3]]*(np.cos(phase)+ 1j*np.sin(phase))
        if np.sum(np.absolute(averagePhase))==0:
            print ("no HDR frames received")
            return False, 0,0,0
        averagePhase /= numFrames
        if window:
            averagePhase = np.sum(averagePhase)/(window*window)
        averagePhase = np.angle(averagePhase)* 4096/(2*np.pi)
        r.close()
        return True, averagePhase, rows, cols
    
MAX_PHASE_VALUE = 4096
def wrapPhaseToSignedInteger(phase):
    """Phase offset should be between more than -2048 and less than 2048"""
    if phase >= MAX_PHASE_VALUE/2:
        return -1*(MAX_PHASE_VALUE - phase)
    elif phase < -MAX_PHASE_VALUE/2:
        return (MAX_PHASE_VALUE + phase)
    else:
        return phase
 
def hdrCommonPhaseOffset(fileName1 , distance, modFreq1, cx = 0, cy = 0,  fileName2 = None, modFreq2 = None, window = 4, chipset = 'tintin.ti'):
    """ Calculates HDR phase offsets for ti chipsets. 
    
    .. note: Make sure that the hdr flag is on for the file before capturing the file"""
    c = 299792458. # m/s
    camsys = Voxel.CameraSystem()
    ret1, averagePhase1, rows, cols = computeHDRAveragePhases(camsys, fileName1, cx, cy, window, chipset)
    if not ret1:
        return False
    ds1 = c/(2*modFreq1*1E6)
    phaseActual1 = distance/ds1*4096
    hdrphaseCorr = wrapPhaseToSignedInteger(int(averagePhase1- phaseActual1))
    if chipset == 'tintin.ti':
        if fileName2 and modFreq2:
            ret2, averagePhase2, _, _ =  computeHDRAveragePhases(camsys, fileName2, cx, cy, window)
            if not ret2:
                return True, hdrphaseCorr, 0
            ds2 = c/(2*modFreq2*1E6)
            phaseActual2 = distance/ds2*4096
            hdrphaseCorr2 = wrapPhaseToSignedInteger(int(averagePhase2- phaseActual2))
        else:
            hdrphaseCorr2 = 0 
    elif chipset == 'calculus.ti':
        hdrphaseCorr = -hdrphaseCorr 
        hdrphaseCorr2 = 0   
    return True, hdrphaseCorr, hdrphaseCorr2

def parseArgs(args = None):
    
    parser = argparse.ArgumentParser(description='Calculate Common Phase Offsets')
    parser.add_argument('-f', '--file1', help = 'Filename1', required = 'True', default= None)
    parser.add_argument('-d', '--distance', type = float, help = 'Distance in meters', required = 'True', default= 0.5)
    parser.add_argument('-m', '--modFreq1', help = 'Modulation Frequency 1', type = float,  required = 'True', default = 40)     
    parser.add_argument('-g', '--file2', help = 'Filename2', default= None)
    parser.add_argument('-n', '--modFreq2', help = 'Modulation Frequency 2', type = float, default = 0)
    parser.add_argument('-x', '--cx', help = 'cx', type = float, default = 0)
    parser.add_argument('-y', '--cy', help = 'cy', type = float, default = 0)
    parser.add_argument('-w', '--window', help = 'Widow Size', type = int, default = 4)
    parser.add_argument('-c', '--chipset', help = 'Chipset', default = 'tintin.ti', required = 'True')
    return parser.parse_args(args)

if __name__ == "__main__":
    
    val = parseArgs(sys.argv[1:])
    ret = hdrCommonPhaseOffset(val.file1, val.distance, val.modFreq1, val.cx, val.cy,\
                                               val.file2, val.modFreq2, val.window, val.chipset)
    if not ret:
        print "Can't find HDR phase offsets"
    else:
        boo, hdrPhaseCorr1, hdrPhaseCorr2 = ret
    if val.chipset == 'tintin.ti':
        print 'hdr_phase_corr_1 = %d\n'%(hdrPhaseCorr1)
        print 'hdr_phase_corr_2 = %f\n'%(hdrPhaseCorr2)
    else:
        print "mod_freq_2 = %d\n"%hdrPhaseCorr1  
    
