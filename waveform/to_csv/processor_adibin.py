import time
import datetime
import logging
import numpy as np
import pandas as pd

# use the local binfilepy
from os import path
import sys
#sys.path.append(path.abspath('/Users/yp/Google Drive/think for mac/ucla_health/binfilepy_git'))
#sys.path.append(path.abspath('/home2/yup1/binfilepy_git'))
#from binfilepy import binfile

from deidentify.deidentifier import Deidentifier
from to_csv.single_file_processor import SingleFileProcessor

class ProcessorAdibin(SingleFileProcessor):

    def __init__(self, dob, mask, binfilepy_path, debug_yn=True):
        super().__init__(dob, mask, debug_yn)
        self.binfilepy_path = binfilepy_path

    def read_binfile(self, input_file):
        sys.path.append(path.abspath(self.binfilepy_path))
        from binfilepy import binfile

        with binfile.BinFile(input_file, "r") as f:
            # You must read header first before you can read channel deidentify
            f.readHeader()
            # I want to read the entire file
            data = f.readChannelData(offset=0, length=0, useSecForOffset=False, useSecForLength=False)

        logging.debug(f"Dataformat: {f.header.DataFormat}")
        logging.debug(f"Seconds per tick: {f.header.secsPerTick}")  # sampling rate 300 Hz
        logging.debug(f"{f.header.__dict__}")
        '''
        {'secsPerTick': 0.004166666666666667, 'Year': 2018, 'Month': 10, 'Day': 16, 'Hour': 19, 'Minute': 3, 'Second': 58.0, 'trigger': 0.0, 'NChannels': 8, 'SamplesPerChannel': 262080, 'TimeChannel': 0, 'DataFormat': 3, 'Version': 1}
        '''

        return f, data

    def create_dataframe(self, input_file):
        start_time = time.time()

        f, data = self.read_binfile(input_file)

        begin_time = pd.to_datetime(str(f.header.Month) + '/' + str(f.header.Day) + '/' + str(f.header.Year) + ' ' + str(f.header.Hour) + ':' + str(f.header.Minute) + ':' + str(f.header.Second))
        sf = 300  # this is the max sampling rate for UCI that all the files are upsampled to
        logging.debug(f"begin_time: {begin_time}")

        for fii in np.arange(len(f.channels)):
            logging.debug(f"Title: {f.channels[fii].Title}, Units: {f.channels[fii].Units}, Scale: {f.channels[fii].scale}, Offset: {f.channels[fii].offset}")
            if fii == 0:
                wave = pd.DataFrame(data[fii], columns=[f.channels[fii].Title])
            else:
                wave[f.channels[fii].Title] = data[fii]
            '''
            if f.channels[fii].Title in ['GE_ART', 'INVP1']:
                wave.loc[wave[f.channels[fii].Title] < 0, f.channels[fii].Title] = 0.
            if f.channels[fii].Title in ['GE_ECG', 'ECG', 'PLETH']:
                wave.loc[wave[f.channels[fii].Title] == -1.700000e+308, f.channels[fii].Title] = 0.
            '''

        wave['timestamp'] = begin_time + pd.to_timedelta(wave.index * f.header.secsPerTick, unit='s') #- pd.Timedelta('8H')
        logging.debug(f"=========original wave dataframe ============: {wave.head()}")

        wave['Sequence'] = [Deidentifier.get_sequence(str(d.date()), self.dob, self.mask) for d in wave['timestamp']]
        wave['CollectionTime'] = [str(d.time()) for d in wave['timestamp']]
        #wave = wave.set_index('timestamp')
        del wave['timestamp']
        cols = wave.columns.tolist()
        cols = cols[-2:] + cols[:-2]
        wave = wave[cols]
        logging.debug(f"!!!!!!!!!!deidentified wave dataframe !!!!!!!!!!! : {wave.head()}")

        elapsed_time = time.time() - start_time
        logging.debug(f"ProcessorAdibin.create_dataframe elapsed_time: {elapsed_time}")

        return wave

    def create_rows(self, input_file):
        start_time = time.time()

        f, data = self.read_binfile(input_file)

        begin_time_str = str(f.header.Month) + '/' + str(f.header.Day) + '/' + str(f.header.Year) + ' ' + str(f.header.Hour) + ':' + str(f.header.Minute) + ':' + str(int(f.header.Second))
        logging.info(f"begin_time: {begin_time_str}")
        begin_time = datetime.datetime.strptime(begin_time_str, '%m/%d/%Y %H:%M:%S')
        logging.debug(f"begin_time: {begin_time}")

        rows = []
        header = ['Sequence','CollectionTime']
        for fii in np.arange(len(f.channels)):
            header.append(f.channels[fii].Title)
        rows.append(header)

        dt = begin_time
        for i in range(len(data[0])):
            dt = dt + datetime.timedelta(seconds=f.header.secsPerTick)
            sequence = Deidentifier.get_sequence(str(dt.date()), self.dob, self.mask)
            ctime = str(dt.time())
            row = [sequence, ctime]
            for fii in np.arange(len(f.channels)):
                logging.debug(f"Title: {f.channels[fii].Title}, Units: {f.channels[fii].Units}, Scale: {f.channels[fii].scale}, Offset: {f.channels[fii].offset}")
                row.append(str(data[fii][i]))
            rows.append(row)

        elapsed_time = time.time() - start_time
        logging.debug(f"ProcessorAdibin.create_dataframe elapsed_time: {elapsed_time}")

        return rows
