"""Checkerboard Lens Calibration - uses the open cv algorithm to compute calibration 
    parameters for a lens. Takes PNGs or VXLs as input. Also converts the vxls into pngs.
    Rows and columns of the checkerboard need to be provided.
    Usage:
    python CheckerBoardLensCalibration.py --file filePath --rows rows --cols cols
    
    
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


import cv2
import numpy as np
import glob
import sys
from VxlToPng import vxltoPng
import argparse
def CheckerBoardLensCalibration(filePath, rows, cols):
    
    """Returns Lens Parameters and distortion coefficients using images or vxl files of a checkerboard taken in different orientations.
    
    Checkerboard Lens Calibration - uses the open cv algorithm to compute calibration 
    parameters for a lens. Takes PNGs or VXLs as input. Also converts the vxls into pngs.
    Rows and columns of the checkerboard need to be provided.

 - **Parameters** required::

          :param filePath: Takes the path of the file with checkerboard images / vxl files
          :param rows: Rows present in the checkerboard
          :param cols: Columns present in the checkerboard
          
   .. note:: Use at least ten images of the checkerboard in different orientations to get the correct result  
"""
          
    objp = np.zeros((rows*cols,3), np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp[:,:2] = np.mgrid[0:rows,0:cols].T.reshape(-1,2)
    objpoints = []
    imgpoints = []
    images = glob.glob(filePath+ '/*.png')
    if not images:
        vxls = glob.glob(filePath + '/*.vxl')
        for vxl in vxls:
            vxltoPng(vxl)
    images = glob.glob(filePath+ '/*.png')        
    for image in images: 
        img = cv2.imread(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)# images are converted to grayscale
        ret, corners = cv2.findChessboardCorners(gray, (rows, cols),None)
        if ret:
            objpoints.append(objp)
            cv2.cornerSubPix(gray,corners,(4,4),(-1,-1),criteria)
            imgpoints.append(corners)
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
    if ret:
        return ret, mtx, dist, rvecs, tvecs
    else:
        print "Cannot calibrate the camera."
        return False
    
def parseArgs (args = None):
    """ Parsing the arguments in the command line - this is used to get the parameters using this script"""
    parser = argparse.ArgumentParser(description='Calculate Common Phase Offsets')
    parser.add_argument('-f', '--file', help = 'FilePath', required = 'True', default= None)
    parser.add_argument('-r', '--rows', type = int, help = 'Number of Rows', required = 'True', default= 10)
    parser.add_argument('-c', '--cols', help = 'Number of Columns', type = int,  required = 'True', default = 15)     
    return parser.parse_args(args)
    
if __name__ == "__main__":    
    
    val = parseArgs(sys.argv[1:])
    ret = CheckerBoardLensCalibration(val.file, val.rows, val.cols)
    if not ret:
        print "Cannot perform lens calibration"
        sys.exit()
    
    boo, mtx, dist, rvecs, tvecs = ret
    dist = dist[0]
    cx = mtx[0,2]
    cy = mtx[1,2]
    fx = mtx[0,0]
    fy = mtx[1,1]
    k1 = dist[0]
    k2 = dist[1]
    p1 = dist[2]
    p2 = dist[3]
    k3 = dist[4]
    
    print "cx = %f\ncy = %f\nfx = %f\nfy = %f\nk1 = %f\nk2 = %f\nk3=%f\np1=%f\np2=%f\n"%(cx, cy, fx, fy, k1, k2, k3, p1, p2)
