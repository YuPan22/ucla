'''
Please see the below code to read .Vital file. This can be used to convert .vital file to csv.
https://github.com/hulab-ucsf/vitalfilepy/blob/master/tests/test_vitalfilepy.py
'''

'''
Offset is an index, which also reflects gag and overlap.
When a gap occurs, the index jumps, e.g,
Sequence	CollectionTime	value	offset	low	high
3.87E+08	20:04:34	21	4267	-999999	999999
3.87E+08	20:04:35	-999999	15707	-999999	999999
When an overlap occurs, the index duplicate.
3.87E+08	20:11:49	-999999	58998	-999999	999999
3.87E+08	20:11:50	-999999	58998	-999999	999999

I need to change sequence and collectiontime accordingly.
'''

import os
import glob
import re
import time
import logging
import pandas as pd
#from datetime import datetime
import datetime

from vitalfilepy import VitalFile
from deidentify.deidentifier import Deidentifier
from to_csv.single_file_processor import SingleFileProcessor



class ProcessorVitalbin(SingleFileProcessor):
    def get_original_begin_time_from_xml(self, input_file):
        xml_path = os.path.join(os.path.dirname(os.path.dirname(input_file)), "XML", "*_0_wf.xml")
        xmls = list(glob.iglob(xml_path, recursive=True))
        if len(xmls) != 1:
            raise Exception("the count of *_0_wf.xml !=1, fails to get vital begin time to fix vital shifting issue")
        begin_time_str = ''
        with open(xmls[0]) as xml:
            line = xml.readline()
            while line:
                if "<Time>" in line:
                    begin_time_str = line.split("<Time>")[1].split("</Time>")[0]
                    break
                line = xml.readline()
        begin_time = datetime.datetime.strptime(begin_time_str, '%m/%d/%Y %I:%M:%S %p')
        return begin_time

    def get_original_begin_time(self, input_file):
        def get_timestamp(filename):
            matched = re.search('-\d{10}_', filename)
            if matched != None:
                return matched.group()[1:-1]

        logging.debug(f'==============os.path.basename(input_file): {os.path.basename(input_file)}')
        unix_epoch_time_str = get_timestamp(os.path.basename(input_file))
        logging.debug(f'unix_epoch_time_str: {unix_epoch_time_str}')
        begin_time = datetime.datetime.fromtimestamp(int(unix_epoch_time_str))
        logging.debug(f"original begin_time in vital: {begin_time}")
        return begin_time

    def get_begin_time(self, input_file):
        #print("!!!!!!!!!!!!!!!!!!!", input_file, os.path.basename(input_file).split('.')[0].split('_')[1])
        #begin_time_str = os.path.basename(input_file).split('.')[0].split('_')[1]

        def get_timestamp(filename):
            matched = re.search('_\d{14}_', filename)
            if matched != None:
                return matched.group()[1:-1]

        begin_time_str = get_timestamp(os.path.basename(input_file))
        #begin_time = pd.to_datetime(begin_time_str[0:4] + '/' + begin_time_str[4:6] + '/' + begin_time_str[6:8] + ' ' + begin_time_str[8:10] + ':' + begin_time_str[10:12] + ':' + begin_time_str[12:14])
        begin_time = datetime.datetime.strptime(begin_time_str[4:6] + '/' + begin_time_str[6:8] + '/' + begin_time_str[0:4]+ ' ' + begin_time_str[8:10] + ':' + begin_time_str[10:12] + ':' + begin_time_str[12:14], '%m/%d/%Y %H:%M:%S')
        logging.debug(f"begin_time in vital: {begin_time}")
        return begin_time

    def create_dataframe(self, input_file):

        start_time = time.time()

        #begin_time = self.get_begin_time(input_file)
        #begin_time = self.get_original_begin_time(input_file)
        begin_time = self.get_original_begin_time_from_xml(input_file)

        data = []
        uom = ''
        with VitalFile(input_file, "r") as f:
            f.readHeader()
            # print(f.header.__dict__)
            # {'Label': 'ECT', 'Uom': '', 'Unit': '6N', 'Bed': 'W664', 'Year': 0, 'Month': 0, 'Day': 0, 'Hour': 0, 'Minute': 0, 'Second': 0.0}
            uom = f.header.__dict__.get('Uom','')
            logging.debug(f"uom: {uom}")
            #line = f.readVitalData()
            try:
                while True:
                    value,offset,low,high = f.readVitalData()
                    yp_datetime = begin_time + datetime.timedelta(seconds=offset)
                    new_tuple = (value, int(offset), low, high, uom, yp_datetime)
                    #logging.debug(f"new_tuple: {new_tuple}")
                    data.append(new_tuple)
            except:
                    pass

        logging.debug(f"vital len(deidentify): {len(data)}")

        vital = pd.DataFrame(data, columns =['value','offset','low','high','uom', 'timestamp'])

        secsPerTick = 1
        #vital['timestamp'] = begin_time + pd.to_timedelta(vital.index * secsPerTick, unit='s')

        vital['Sequence'] = [Deidentifier.get_sequence(str(d.date()), self.dob, self.mask) for d in vital['timestamp']]
        vital['CollectionTime'] = [d.time() for d in vital['timestamp']]

        del vital['timestamp']
        cols = vital.columns.tolist()
        cols = cols[-2:] + cols[:-2]
        vital = vital[cols]

        elapsed_time = time.time() - start_time
        logging.debug(f"ProcessorVitalbin.create_dataframe elapsed_time: {elapsed_time}")

        return vital

    def create_rows(self, input_file):
        start_time = time.time()

        dt = self.get_begin_time(input_file)

        rows = []
        header = ['Sequence','CollectionTime','Value','Offset','Low','High','Uom']
        rows.append(header)

        uom = ''
        with VitalFile(input_file, "r") as f:
            f.readHeader()
            uom = f.header.__dict__.get('Uom', '')
            logging.debug(f"uom: {uom}")
            try:
                while True:
                    value, offset, low, high = f.readVitalData()
                    dt = dt + datetime.timedelta(seconds=offset)
                    sequence = Deidentifier.get_sequence(str(dt.date()), self.dob, self.mask)
                    ctime = str(dt.time())
                    row = [sequence, ctime, str(value), str(int(offset)), str(low), str(high), uom]
                    rows.append(row)
            except:
                pass

        logging.info(f"vital rows {rows}")
        elapsed_time = time.time() - start_time
        logging.debug(f"ProcessorAdibin.create_dataframe elapsed_time: {elapsed_time}")

        return rows

