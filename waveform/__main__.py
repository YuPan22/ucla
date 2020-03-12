"""
This example module shows various types of documentation available for use
with pydoc.  To generate HTML documentation for this module issue the
command:

    pydoc -w foo

"""
import os
import glob
import time
import traceback
import argparse
import configparser
import logging

from to_csv.processor_adibin import ProcessorAdibin
from to_csv.processor_vitalbin import ProcessorVitalbin
from to_csv.processor_xml import ProcessorXml
from deidentify.deidentifier import Deidentifier
from deidentify import deidentify_xml

from upmc.xml_to_csv import UPMC


class Job():
    def __init__(self, input_folder_path, output_folder_path, binfilepy_path, config_section='Test Env', type="toCsv", debug_yn=True):
        self.debug_yn = debug_yn

        self.job_type = type
        self.input_folder_path = input_folder_path
        self.output_folder_path = output_folder_path
        self.binfilepy_path = binfilepy_path

        self.config_section = config_section
        self.get_config()
        logging.basicConfig(level=getattr(logging, self.config_dict.get('log_level')))
        #logging.basicConfig(level=logging.INFO)


    def get_config(self):
        config = configparser.RawConfigParser()
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config', 'configuration.cfg'))
        self.config_dict = dict(config.items(self.config_section))

    def process_folder(self):
        """
        Iterate all file inside a folder.
        If job_type is toCsv, then convert adibin to waveform csv, convert vitalbin to vital csv, convert xml to alarms csv.
        If job_type is deidXml, then deidentify xml file with replacing data with sequence.
        """
        #for r, d, f in os.walk(input_folder_path):
        #    for file in f:
        #        input_file_path = os.path.join(r, file)
        for input_file_path in glob.iglob(self.input_folder_path+'/**', recursive=True):
            if os.path.isfile(input_file_path):
                logging.info(f"job_type: {self.job_type}, processing: {input_file_path}")
                start_time = time.time()
                file = os.path.basename(input_file_path)

                try:
                    adob = Deidentifier.query_dictionary(stp_filename=file, field="DateofBirth")
                    amask = Deidentifier.query_dictionary(stp_filename=file, field="BaseDateNumber")
                    logging.debug(f"dob: {adob}, mask: {amask}")

                    if self.job_type == "toCsv":
                        #processor = SingleFilePorcessor(dob=adob, mask=amask, debug_yn=self.debug_yn)
                        if '.adibin' in file:
                            processor = ProcessorAdibin(dob=adob, mask=amask, binfilepy_path=self.binfilepy_path, debug_yn=self.debug_yn)
                        elif '.vital' in file:
                            processor = ProcessorVitalbin(dob=adob, mask=amask, debug_yn=self.debug_yn)
                        elif '.xml' in file:
                            processor = ProcessorXml(dob=adob, mask=amask, debug_yn=self.debug_yn)
                        else:
                            continue

                        df = processor.create_dataframe(input_file_path)
                        if self.debug_yn:
                            processor.check_dataframe(df)

                        processor.dataframe_to_csv(df, file, self.output_folder_path, file, header_yn=True)

                        '''
                        rows = processor.create_rows(input_file_path)
                        processor.rows_to_csv(rows, file, self.output_folder_path, file)
                        '''
                    else:
                        if '.xml' in file:
                            #deidentify_xml.deidentify_xml(input_file_path, file, self.output_folder_path, adob, amask)
                            #up = UPMC(256)
                            up = UPMC()
                            up.xml_to_csv_waveforms(input_file_path, file, self.output_folder_path, adob, amask)
                            #up.xml_to_csv_vitals(input_file_path, file, self.output_folder_path, adob, amask)
                            #up.xml_to_csv_alarms(input_file_path, file, self.output_folder_path, adob, amask)

                    elapsed_time = time.time() - start_time
                    logging.info(f"Done processing: {input_file_path}, elapsed_time: {elapsed_time}, seconds \n")
                except Exception:
                    logging.error("Exception occurred", exc_info=True)
                    #traceback.print_exc()
                    #print(Exception)

    def run(self):
        """
        First create the deidentification dictionary,
        then process all files inside a folder
        """
        #logging.info(self.config_dict.get('azure_storage_account'))

        de_id_ins = Deidentifier()
        logging.debug(de_id_ins.dict)

        self.process_folder()


if __name__ == '__main__':
    start = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument('-debug', action="store_true")
    parser.add_argument('-type', choices=['toCsv', 'deidXml'], action="store", dest="type")
    parser.add_argument('-input', action="store", dest="input_folder_path")
    parser.add_argument('-output', action="store", dest="output_folder_path")
    parser.add_argument('-bp', action="store", dest="binfilepy_path")
    args = parser.parse_args()
    logging.info(args)

    Job(input_folder_path=args.input_folder_path, output_folder_path=args.output_folder_path, binfilepy_path=args.binfilepy_path, type=args.type, debug_yn=args.debug).run()

    end = time.time()
    logging.info(f"__main__ runtime: {end - start}")
    
