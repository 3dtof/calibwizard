
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


import sys
import numpy as np
import csv
import os
import argparse

def TemperatureCalibration(csvFile):
    """Calculates temperature calibration offsets (coeff_illum, coeff_sensor), taking csv file as input. 
    
    Takes a CSV file containing phase values at temperatures for illumination and sensor. Gives coeff_illum and coeff_sensor as output
    Uses a least squares fit to compute temperature calibration
    """
    if not os.path.exists(csvFile):
        print ("Invalid Filename")
        sys.exit()
    tSensor = []
    tIllum = []
    phaseCorr1 = []
    
    with open(csvFile, 'rb') as f:
        reader = csv.reader(f)  
        for row in reader:
            tIllum.append(float(row[0]))
            tSensor.append(float(row[1]))
            phaseCorr1.append(float(row[2]))
    tSensor = np.array(tSensor)
    tIllum = np.array(tIllum)
    phaseCorr1 = np.array(phaseCorr1)
    tSensorCalib = tSensor[0]
    tIllumCalib = tIllum[0]
    phaseCorr1Calib = phaseCorr1[0]             
    tSensor -= tSensorCalib
    tIllum -= tIllumCalib
    phaseCorr1 -= phaseCorr1Calib
    A = np.c_[tSensor,tIllum]
    coeff_sensor,coeff_illum = np.linalg.lstsq(A, phaseCorr1)[0]
    calibPrec = 1
    coeff_illum *= 16
    coeff_sensor *= 16
    if coeff_illum > 2047 or coeff_illum < -2048 or coeff_sensor > 2047 or coeff_sensor < -2048:
        calibPrec = 0
        coeff_sensor /= 16
        coeff_illum /= 16
            
    return True, round(coeff_illum), round(coeff_sensor), calibPrec 

def parseArgs (args = None):
    
    parser = argparse.ArgumentParser(description='Calculate Temperature Calibration Offsets')
    parser.add_argument('-f', '--file', help = 'FilePath', required = 'True', default= None)
    return parser.parse_args(args)
    

if __name__ == '__main__':
    val = parseArgs(sys.argv[1:])
    try:
        ret = TemperatureCalibration(val.file)
        boo, coeff_illum, coeff_sensor, calibPrec = ret
        print ("coeff_illum = %d\ncoeff_senosr = %d\ncalib_prec = %d\n"%(coeff_illum, coeff_sensor, calibPrec))
    except Exception, e:
        print e
        sys.exit()
 
