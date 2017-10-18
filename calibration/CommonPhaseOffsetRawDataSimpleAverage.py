"""
CommonPhaseOffset.py - takes vxl file as input along with modulation frequency and distance to give phaseCorr values. 
Requires two vxl files - one for each frequency to calculate phase corr 1 and phase corr 2
'''

'''Example Script:
python CommonPhaseOffset.py -f "file.vxl" -d 0.7 -m 20  -c tintin.ti (-n 10 -g "file2.vxl")
or 
python CommonPhaseOffset.py --file1 "file.vxl" --distance 0.7 --modFreq1 20 --chipset tintin.ti (--modFreq2 10 --file2 "file2.vxl")
"""

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
import argparse
import sys

MAX_PHASE_VALUE = 4096
def wrapPhaseToSignedInteger(phase):
   """Keeps the phase offset value between -2048 and 2048 """ 

   if phase >= MAX_PHASE_VALUE/2:
     return -1*(MAX_PHASE_VALUE - phase)
   elif phase < -MAX_PHASE_VALUE/2:
     return (MAX_PHASE_VALUE + phase)
   else:
     return phase

def parseframe(frame, rows=240, cols=320):
    """Parses the values given by the group by 16 mode of the code and gives individual frames. Required for using raw data"""
    confidenceData = np.ndarray(rows*cols, dtype="uint16")
    phaseData = np.ndarray(rows*cols, dtype="uint16")
    confidenceData.dtype = "uint64"
    phaseData.dtype = "uint64"
    frame.dtype="uint64"
    confidenceData[::2] = frame[::4]
    confidenceData[1::2] = frame[1::4]
    phaseData[::2] = frame[2::4]
    phaseData[1::2] = frame[3::4]
    confidenceData.dtype="uint16"
    phaseData.dtype="uint16"
    confidenceData = confidenceData.reshape(rows, cols)
    phaseData = phaseData.reshape(rows, cols)
    ambientData = (confidenceData & 0xF000) >> 12
    flagsData = (phaseData & 0xF000) >> 12
    confidenceData = confidenceData & 0x0FFF
    phaseData = phaseData & 0x0FFF
    frame.dtype="uint16"
    return (phaseData, confidenceData, ambientData, flagsData) 

def extractPhasesandAmplitudes(fileName, camsys):
    """Extracts just phase and amplitude values from the parsed frames"""
    rawFrames, rows, cols = extractRawdataFromVXL(fileName, camsys)
    frames = rawFrames.shape[0]
    processedPhases = np.zeros([frames, rows, cols])
    processedAmplitudes = np.zeros([frames, rows, cols])
    for frame in np.arange(frames):
        phaseData, confidenceData, _, _ = parseframe(rawFrames[frame], rows, cols)
        processedPhases[frame] = phaseData
        processedAmplitudes[frame] = confidenceData
    return processedPhases, processedAmplitudes,  frames, rows, cols
    
def computeAveragePhases(camsys, fileName, window =4, cx = 0, cy = 0):
    """ Computes the average phases for a given file. Uses simple average for getting phase value """
    r = Voxel.FrameStreamReader(fileName, camsys)
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
    
    phases, amplitudes, frames, rows, cols = extractPhasesandAmplitudes(fileName, camsys)
    if cx == 0:
        cx = rows/2
    if cy == 0:
        cy = cols/2    
    centerShape = [cx-window/2, cx+window/2, cy-window/2, cy+window/2]
    averagePhases = np.zeros([window, window], dtype = 'float')
    for val in np.arange(frames):
        phaseWindow= phases[val][centerShape[0]:centerShape[1], centerShape[2]:centerShape[3]]
        averagePhases+= phaseWindow
    averagePhases = averagePhases/frames
    averagePhases = np.mean(averagePhases)
    
    return averagePhases, rows, cols

def extractRawdataFromVXL(filename, camsys):
    """Takes raw data from vxl file"""
    r = Voxel.FrameStreamReader(filename, camsys)
    if not r.isStreamGood():
        print("Stream is not good: " + filename)
    bool1, cols = r.getStreamParamu("frameWidth")
    bool2, rows = r.getStreamParamu("frameHeight")
    numFrames = r.size()
    rawFrames = np.zeros((numFrames, rows*cols*4), dtype='uint8')
    for i in (range(numFrames)):
        if not r.readNext():
            print("Failed to read frame %d" %i)
            break
        rawFrame = Voxel.RawDataFrame.typeCast(r.frames[Voxel.DepthCamera.FRAME_RAW_FRAME_UNPROCESSED])
        rawFrames[i] = np.array(rawFrame.data, copy=True)
    r.close()
    return rawFrames, rows, cols

def commonPhaseOffset(file1, distance, modFreq1, cx, cy, file2 = None, modFreq2 = None, window = 4, chipset = 'TintinCDKCamera'):
    """ Computes the common phase offsets. 
    
    This function calculates the common phase offsets for a given file, taking VXL as input. 
    
    **Parameters**::
    
        - file1, file2: File(s) for computing common phase offsets. These should be vxl files of a flat wall. The camera should be almost parallel to the wall.
        - modFreq1, modFreq2 : Modulation Frequency (ies) when the data is captured. If dealiasing is enabled, two modulation frequencies are required
        - cx, cy: The coordinates of the center pixel, found during lens calibration. If cx and cy are not available, the central value (120,160) is taken.
        - window: The window size. By default, a window of 4x4 is required. 
        - chipset: The chipset being used. 
        
    **Returns**::
    
        - phase_Corr1: Phase offset value for the first modulation frequency
        - phase_Corr2: Phase offset value for the second modulation frequency
        """
    c = 299792458 # m/s
    camsys = Voxel.CameraSystem()
    averagePhase1, rows, cols = computeAveragePhases(camsys, file1, window, cx, cy) #default window size = 4
    ds1 = c/(2*modFreq1*1E6)
    phaseActual1 = distance/ds1*4096
    phaseAverage1 = averagePhase1
    phaseCorr = wrapPhaseToSignedInteger(int(phaseAverage1 - phaseActual1))
    if file2 and modFreq2:
        averagePhase2, rows, cols =  computeAveragePhases(camsys, file2, window, cx, cy)
        ds2 = c/(2*modFreq2*1E6)
        phaseActual2 = distance/ds2*4096
        phaseAverage2 = averagePhase2
        phaseCorr2 = wrapPhaseToSignedInteger(int(phaseAverage2-phaseActual2))
    else:
        phaseCorr2 = 0    
    if chipset == 'CalculusCDKCamera': #additive phase
        phaseCorr = -phaseCorr
        phaseCorr2 = -phaseCorr2
    return True, phaseCorr, phaseCorr2, rows, cols
def parseArgs (args = None):
    """ Parsing the arguments in the command line - this is used to get the parameters using this script"""
    parser = argparse.ArgumentParser(description='Calculate Common Phase Offsets')
    parser.add_argument('-f', '--file1', help = 'Filename1', required = 'True', default= None)
    parser.add_argument('-d', '--distance', type = float, help = 'Distance in meters', required = 'True', default= 0.5)
    parser.add_argument('-m', '--modFreq1', help = 'Modulation Frequency 1', type = float,  required = 'True', default = 40.0)     
    parser.add_argument('-g', '--file2', help = 'Filename2', default= None)
    parser.add_argument('-n', '--modFreq2', help = 'Modulation Frequency 2', type = float, default = 0.0)
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
