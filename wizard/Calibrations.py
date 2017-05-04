
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


from collections import OrderedDict
LENSCALIBS = ['CheckerBoard']
COMMONPHASECALIBS = ['FlatWall']
PERPIXELCALIBS = ['FlatWall']
NONLINEARITYCALIBS = ['PieceWise']
TEMPCALIBS = ['Temperature']
HDRCALIBS = ['FlatWall HDR']

CALIB_DICT = OrderedDict()
CALIB_DICT['lens'] = LENSCALIBS
CALIB_DICT['nonLinearity'] = NONLINEARITYCALIBS
CALIB_DICT['temperature'] = TEMPCALIBS
CALIB_DICT['commonPhase'] = COMMONPHASECALIBS
CALIB_DICT['hdrCommonPhase'] = HDRCALIBS
CALIB_DICT['perPixel']= PERPIXELCALIBS

CALIB_SHOW = OrderedDict()
CALIB_SHOW['lens'] = False
CALIB_SHOW['commonPhase'] = False
CALIB_SHOW['perPixel']= False
CALIB_SHOW['nonLinearity'] = False
CALIB_SHOW['temperature'] = False
CALIB_SHOW['crossTalk'] = False
CALIB_SHOW['hdrCommonPhase'] = False

CHIPSETS = OrderedDict()
CHIPSETS["tintin.ti"] = "TintinCDKCamera"
CHIPSETS["calculus.ti"] = "CalculusCDKCamera"

CALIB_NAME = OrderedDict()
CALIB_NAME['lens'] = 'Lens'
CALIB_NAME['commonPhase'] = 'Common Phase'
CALIB_NAME['perPixel']= 'Per Pixel'
CALIB_NAME['nonLinearity'] = 'Non Linearity'
CALIB_NAME['temperature'] = 'Temperature'
CALIB_NAME['hdrCommonPhase'] = 'HDR Common Phase'    