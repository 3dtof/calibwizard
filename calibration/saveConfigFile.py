
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

from ConfigParser import ConfigParser
import Voxel
import os

class WriteConfigFile (object):
    def __init__(self, chipset, profile):
        self.config = None
        self.chipset = chipset
        super (WriteConfigFile, self). __init__()
        self.chipsetName = chipset + 'CDKCamera'
        self.profile = profile + '.conf'
        c = Voxel.Configuration()
        ret, path = c.getLocalConfPath()
        self.confFile = path  + os.sep + self.chipsetName + self.profile
        if not os.path.isfile(self.confFile):
            self.configBase()
        else:
            self.config = ConfigParser()
            self.config.read(self.confFile)    
    def configBase(self):   
        self.config = ConfigParser()
        self.config.add_section('global')
        self.config.set ('global', 'id', 149)
        self.config.set ('global', 'name', self.profile)
        self.config.add_section('defining_params')
        
        if self.chipset == 'Calculus':
            self.config.add_section('params')
            self.config.set('params', 'disable_illum_p', True)
            self.config.set('params', 'disable_illum_n', True)
            self.config.set('params', 'pvdd_en', True)
            self.config.set('params', 'pvdd_voltage', 5)
            self.config.set('defining_params', 'unambiguous_range', 4)
            self.config.set('defining_params', 'mix_volt', 1200)
            self.config.set('defining_params', 'mod_freq1', 36.0)
            self.config.set('defining_params', 'mod_cdriv_en', True)
            self.config.set('defining_params', 'mod_cdriv_curr', 30)
            self.config.set('defining_params', 'sub_frame_cnt_max1', 2)
            self.config.set('defining_params', 'frame_rate', 60.0)
            self.config.set('defining_params', 'intg_time', 88)
            self.config.set('defining_params', 'shutter_en', True)
            self.config.set('defining_params', 'high_ambient_en', False)
        
        if self.chipset == 'Tintin':
           
            self.config.set('defining_params', 'op_clk_freq', 0)
            self.config.set('defining_params', 'sub_frame_cnt_max', 2)
            self.config.set('defining_params', 'unambiguous_range', 8)
            self.config.set('defining_params', 'quad_cnt_max', 6)
            self.config.set('defining_params', 'frame_rate', 50.0)
            self.config.set('defining_params', 'intg_duty_cycle', 5)            
            self.config.set('defining_params', 'illum_power_percentage', 55)
            self.config.set('defining_params', 'delay_fb_corr_mode', 1)
            self.config.set('defining_params', 'delay_fb_dc_corr_mode', 1)
            self.config.set('defining_params', 'sscg_en', True)
            self.config.set('defining_params', 'sscg_period', 6)
            self.config.set('defining_params', 'sscg_modulation', 0)
            self.config.set('defining_params', 'init_2', 310)
            self.config.set('defining_params', 'init_3', 330)
            self.config.set('defining_params', 'init_4', True)
            self.config.set('defining_params', 'init_5', 3)
            self.config.set('defining_params', 'mix_volt', 1500)
            self.config.set('defining_params', 'intg_time', 28)

        self.config.add_section('calib')
            
    def configSet(self, param, value):
        if not self.config.has_section('calib'):
            self.config.add_section('calib')
            
        self.config.set('calib', param, value)
                
                
    def configWrite(self):
        with open (self.confFile, 'w') as conf:
            self.config.write(conf)
            conf.close()
