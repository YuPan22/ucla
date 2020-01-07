'''
Author: Yu Pan (yupan@mednet.ucla.edu)

Function of this code:
Because RESP channel contains multiple cals, e.g.,
grep -E "Resp.*Waveform" CLIN_ENG_WMOR8-1563486442.xml | head -1
• CLIN_ENG_WMOR8-1563486442.xml
    Resp,"0,1,1230,2867"
• CLIN_ENG_WMOR23-1564670746.xml
    Resp,"0,1,1018,3078"
• CLIN_ENG_WCATHL3-1569512080.xml
    Resp,"0,1,2,4095"

We need to generate configuration file with corresponding scaling factor and offset before we convert xml to adibin.

The logic is as below:
If an xml doesn't contain RESP, then use the base configuration.
Otherwise, get the RESP cal from the xml to calculate scaling factor and offset, and append them into the base configuration to create a new configuration file.

Then this code will call wfconvert -c {appropriate configuration} to convert xml to adibin/vitalbin.

Usage example:
C:\Users\YuPan\Source\Workspaces\OHIA\Enterprise Information Architecture\Data Architecture\Development\Edwards\yupan\waveform\misc>python wfconvert_runner_with_dynamic_config.py \
-wfconvert_path C:\Users\YuPan\Downloads\wftools_v0.65\wftools_v0.65\wfconvert.exe \
-base_cfg_path C:\Users\YuPan\Downloads\wftools_v0.65\wftools_v0.65\wfconvert_config.yaml \
-xml_input_path C:\Users\YuPan\Downloads\Cannenson\xmls \
-bin_output_path C:\Users\YuPan\Downloads\Cannenson\testout

'''

import argparse
import glob
import logging
import os
import time
from shutil import copyfile
from pathlib import Path

class Wrapper:
    def __init__(self, wfconvert_path, base_cfg_path, xml_input_path, bin_output_path):
        self.wfconvert_path = wfconvert_path
        self.base_cfg_path = base_cfg_path
        self.xml_input_path = xml_input_path
        self.bin_output_path = bin_output_path

    def dynamic_config_gen(self):
        use_dynamic_cfg = False

        '''
        Read xml file to check if it contains RESP
        '''
        scale = 0
        offset = 0
        with open(self.xml_input_path, 'r') as xf:
            line = xf.readline()
            while line:
                if "Resp" in line and "Cal=" in line:
                    use_dynamic_cfg = True
                    break
                line = xf.readline()

            '''
            If xml contains RESP and corresponding config doesn't exist, then create it
            '''
            if not use_dynamic_cfg:
                return self.base_cfg_path

            logging.debug(f"line: {line}")
            values = line.split('Cal="')[1].split('"')[0]
            logging.debug(f"Cal values: {values}")
            base_cfg_name = os.path.basename(self.base_cfg_path)
            dynamic_cfg_name = base_cfg_name.replace(".yaml", f"{values}.yaml")
            dynamic_cfg_path = os.path.join(os.path.dirname(self.base_cfg_path), dynamic_cfg_name)
            logging.debug(f'dynamic_cfg_path: {dynamic_cfg_path}')

            '''
            If dynamic config already exists, then no need to recreate it.
            '''
            if os.path.exists(dynamic_cfg_path):
                return dynamic_cfg_path

            '''
            Do not directly modify the base config file, instead, get its copy and modify the copy
            '''
            copyfile(self.base_cfg_path, dynamic_cfg_path)

            cal_low, cal_high, grid_low, grid_high = values.split(",")
            logging.debug(f"cal_low, cal_high, grid_low, grid_high : {cal_low}, {cal_high}, {grid_low}, {grid_high}")
            offset = float(grid_low)
            if "nan" in cal_low.lower():
                scale = -0.025
            else:
                scale = round((float(cal_high) - float(cal_low)) / (float(grid_high) - float(grid_low)), 5)
            logging.debug(f"scale: {scale}, offset: {offset}")

            # what if grid_low == grid_high

            with open(dynamic_cfg_path, 'a') as cf:
                cf.write('- label: "RESP"\n')
                cf.write('    uom: "Uncalib"\n')
                cf.write('    rangeLow: 0.0\n')
                cf.write('    rangeHigh: 100.0\n')
                cf.write(f'    offset: {offset}\n')
                cf.write(f'    scale: {scale}\n')

            return dynamic_cfg_path

    def call_wfconvert(self):
            chosen_config = self.dynamic_config_gen()
            cmd = f'{self.wfconvert_path} -c {chosen_config} -f {self.xml_input_path} -o {self.bin_output_path}'
            logging.info(f'cmd: {cmd}')
            os.system(cmd)

def run(wfconvert_path, base_cfg_path, xml_input_path, bin_output_path):
    output_path = os.path.basename(bin_output_path)
    #logging.debug(f"output_path: {output_path}, os.path.basename(xml_input_path)[:-4]: {os.path.basename(xml_input_path)[:-4]}")
    if output_path != os.path.basename(xml_input_path)[-4]:
        output_path = os.path.join(bin_output_path, os.path.basename(xml_input_path)[:-4])
    else:
        output_path = bin_output_path

    logging.debug(f"output_path: {output_path}")
    Path(output_path).mkdir(parents=True, exist_ok=True)

    wrapper = Wrapper(wfconvert_path, base_cfg_path, xml_input_path, output_path)
    wrapper.call_wfconvert()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    start = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument('-wfconvert_path', action="store", dest="wfconvert_path")
    parser.add_argument('-base_cfg_path', action="store", dest="base_cfg_path")
    parser.add_argument('-xml_input_path', action="store", dest="xml_input_path")
    parser.add_argument('-bin_output_path', action="store", dest="bin_output_path")
    args = parser.parse_args()
    logging.info(f"args: {args}")

    '''
    args.xml_input_path can be a file or a folder.
    If it is a folder, iterate all the .xml files under it one by one
    '''
    if os.path.isdir(args.xml_input_path):
        for input_file_path in glob.iglob(args.xml_input_path+'/**', recursive=True):
            if os.path.isfile(input_file_path) and '.xml' in os.path.basename(input_file_path):
                logging.info(f"processing: {input_file_path}")
                run(args.wfconvert_path, args.base_cfg_path, input_file_path , args.bin_output_path)
    else:
        if os.path.isfile(args.xml_input_path) and '.xml' in os.path.basename(args.xml_input_path):
            logging.info(f"processing: {args.xml_input_path}")
            run(args.wfconvert_path, args.base_cfg_path, args.xml_input_path, args.bin_output_path)

    end = time.time()
    logging.info(f"__main__ runtime: {end - start} seconds")
