"""FlatWallLensCalibration: Uses two-distance algorithm for computing lens parameters. 

Takes VXL of a flat wall at two distances as input. Gives lens parameters as the output
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
from ComputeAveragePhase import computeAveragePhases
import Voxel
import scipy.ndimage as snd 
import scipy.optimize as sopt


def flatWallLensCalibration(fileName1, distance1, fileName2, distance2, cx= 0 , cy = 0):
    camsys = Voxel.CameraSystem()
    nearPhase, _, _ = computeAveragePhases(camsys, fileName1, cx, cy,  window= 0)
    farPhase, _, _ = computeAveragePhases(camsys, fileName2, cx, cy, window = 0)
    deltaPhase = farPhase - nearPhase
    deltaPhaseSmooth = snd.uniform_filter (deltaPhase, 5, mode = 'nearest')
 # 1. Compute normal pixel
    ny, nx = np.unravel_index(np.argmin(deltaPhaseSmooth), deltaPhase.shape)
    rows, columns = deltaPhase.shape
    # 2. Construct a set of all possible distances from the Normal Pixel
     # a is the set of all squared distances from the normal pixel
    y = np.outer(np.linspace(0, rows - 1, rows), np.ones((columns,)))
    x = np.outer(np.ones((rows,)), np.linspace(0, columns - 1, columns))
    a = np.square(y - ny) + np.square(x - nx)
    
    # a1 is the set of all unique distances from the normal pixel
    (a1, inverse) = np.unique(a.reshape(-1), return_inverse=True)
    # a_root is the matrix of all pixel distances from the normal pixel
    a1Root = np.sqrt(a1)
    # inverse1 is the matrix with the index in a1 of a pixel's distance from the normal pixel
    inverse1 = inverse.reshape(rows, -1)
    
    # 3. For every distance, take the set of pixels at the same distance from the normal pixel
    # and take the mean of the corresponding cosThetas at each distance
    cosThetas = []
    cosThetaMatrix = np.zeros(inverse1.shape)
    for index, value in enumerate(a1):
      i = inverse1 == index
      co = deltaPhaseSmooth[ny, nx]/np.mean(deltaPhaseSmooth[i])
      cosThetas.append(co)
      cosThetaMatrix[i] = co
    
    cosThetas = np.array(cosThetas)
    # This array is now the set of pixel distances vs cosThetas
    # We can use this directly to compute per pixel offsets if we like
    
    # Note: there might be some cosThetas > 1. Clamping it for now
    cosThetas = np.clip(cosThetas, 0, 1)
    cosThetaMatrix = np.clip(cosThetaMatrix, 0, 1)
    
    # 4. Note: before computing tanThetas, we need to translate these to Cx, Cy - see step 4 in the PPT
    cosThetas = cosThetas*deltaPhaseSmooth[ny, nx]/deltaPhaseSmooth[cy, cx]
    cosThetaMatrix = cosThetaMatrix*deltaPhaseSmooth[ny, nx]/deltaPhaseSmooth[cy, cx]
    
    tanThetas = np.tan(np.arccos(cosThetas))
    
    # 5. Use either scipy.optimize.curve_fit or np.linalg.lstsq to fit the tanTheta function
    # x is pixel distance (a1_root)
    # and tanThetas is the measured tanTheta
    # Note: should we skip a few distances at the beginning?
    popt, pcov = sopt.curve_fit(lambda x, f, k1, k2, k3:  f*x*(1 + x*x*(k1 + x*x*(k2 + x*x*k3))), tanThetas, a1Root)
    #popt[] should now be f, k1, k2, k3
    # And can be used for distortion matrix
    # p1, p2 are assumed to be 0 (no tangential distortion) and fx, fy are assumed to be equal to f
    if popt and pcov:
        mtx = np.array([[popt[0], 0, cx], [0, popt[1], cy], [0 ,0 , 1]])
        dist = np.array([popt[2], popt[3], 0., 0, popt[3]])
        
        return True, mtx, dist
    else:
        return False
