import os
import re
import time
import pandas as pd
from pandas import HDFStore
import logging

from deidentify.deidentifier import Deidentifier

class SingleFileProcessor():
    def __init__(self, dob, mask, debug_yn=True):
        self.debug_yn = debug_yn
        self.dob = dob
        self.mask = mask

    def create_dataframe(self, input_file):
        pass

    def check_dataframe(self, df):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        print(df.head())
        print(df.shape)

    def deidentified_filename(self, filename):
        return re.sub('_\d{8}', '_', filename)

    def deidentified_filename_with_sequence(self, filename):
        pattern = re.compile('_\d{8}')
        def replace(match):
            return "_"+Deidentifier.get_sequence(match.group()[1:], self.dob, self.mask)+"~"
        tmp = pattern.sub(replace, filename)
        #return re.sub('-\d{10}_', '-', tmp) #10 digits is UTC timestamp, which should be removed
        return tmp


    def get_output_file_name(self, input_file, output_path, filename, ext):
        stp_filename = os.path.basename(input_file)

        study_id = Deidentifier.query_dictionary(stp_filename, field="studyid")
        encounter_id = Deidentifier.query_dictionary(stp_filename, field="encounterid")

        new_output_path = os.path.join(output_path, study_id, encounter_id)
        if not os.path.exists(new_output_path):
            os.makedirs(new_output_path)  #this equals to mkdir -p

        if ".xml" in filename:
            filename = filename.replace(".xml", ".alarm")

        #filename = filename.split("-")[1]

        final_output_filename = os.path.join(new_output_path, study_id + "_" + encounter_id + "_" + self.deidentified_filename_with_sequence(filename) + "." + ext)

        return final_output_filename


    def dataframe_to_csv(self, df, input_file, output_path, filename, header_yn=True):

        start_time = time.time()

        final_output_filename = self.get_output_file_name(input_file, output_path, filename, "csv")
        logging.debug(f"Writing into {final_output_filename}")

        df.to_csv(final_output_filename, index=False)
        #df.waveform(os.path.join(output_path, filename.split(".")[0]) + ".csv.gz", chunksize=100000, compression='gzip', encoding='utf-8')

        elapsed_time = time.time() - start_time
        logging.debug(f"SingleFilePorcessor.dataframe_to_csv elapsed_time: {elapsed_time}")

    def dataframe_to_hdf5(self, df, input_file, output_path, filename, header_yn=True):

        start_time = time.time()

        final_output_filename = self.get_output_file_name(input_file, output_path, filename, "h5")
        logging.debug(f"Writing into {final_output_filename}")

        store = HDFStore(final_output_filename)
        store.put('dataset', df, format='table', data_columns=True)

        elapsed_time = time.time() - start_time
        logging.debug(f"SingleFilePorcessor.dataframe_to_csv elapsed_time: {elapsed_time}")


    def rows_to_csv(self, rows, input_file, output_path, filename):
        start_time = time.time()

        final_output_filename = self.get_output_file_name(input_file, output_path, filename, "csv")
        logging.debug(f"Writing into {final_output_filename}")

        with open(final_output_filename, 'w', encoding='utf-8') as f:
            for row in rows:
                f.write(f"{','.join(row)}\n")

        elapsed_time = time.time() - start_time
        logging.debug(f"SingleFilePorcessor.dataframe_to_csv elapsed_time: {elapsed_time}")
