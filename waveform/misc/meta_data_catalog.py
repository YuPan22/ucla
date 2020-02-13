import os
import glob
import logging
import subprocess
import time
import argparse
import logging
import sys
sys.path.append(".")
from deidentify.deidentifier import Deidentifier

logging.basicConfig(level=logging.INFO)

def generate_catalog(input_dir, output_file_path):
    de_id_ins = Deidentifier()
    logging.debug(de_id_ins.dict)

    with open(output_file_path, "w") as outf:
        for xml_file_path in glob.iglob(input_dir + '/**', recursive=True):
            if os.path.isfile(xml_file_path) and ".xml" in xml_file_path:
                base_file_name = os.path.basename(xml_file_path)
                study_id = Deidentifier.query_dictionary(base_file_name, field="studyid")
                encounter_id = Deidentifier.query_dictionary(base_file_name, field="encounterid")

                channels = set()
                # cmd = f'''grep "Label=" "${xml_file_path}" | awk '{{print $3}}' | awk -F'"' \'{{print $2}}' | sort | uniq >> output.txt'''
                with open(xml_file_path, "r") as inf:
                    xml_line = inf.readline()
                    logging.info(xml_line)
                    while xml_line:
                        if f'Label="' in xml_line:
                            logging.info(f"xml_line: {xml_line}")
                            sp = xml_line.split('Label="')
                            channel = sp[1].split('"')[0]
                            if channel not in channels:
                                channels.add(channel)
                        xml_line = inf.readline()

                for c in channels:
                    outf.write(f'{c}, {study_id}, {encounter_id}, {base_file_name}\n')

if __name__ == '__main__':
    start = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument('-input_dir', action="store", dest="input_dir")
    parser.add_argument('-output_file', action="store", dest="output_file_path")
    args = parser.parse_args()
    logging.info(args)

    generate_catalog(args.input_dir, args.output_file_path)

# python misc/meta_data_catalog.py -input_dir "/Users/yp/Downloads/xmls" -output_file "/Users/yp/Google Drive/think for mac/ucla_health/ucla/waveform/dc.txt"
# python misc/meta_data_catalog.py -input_dir /opt/genomics/WaveFormProcessedFiles/CLIN_ENG_WCATHL2 -output_file /opt/genomics/WaveFormProcessedFiles/codes/waveform/dc.txt
