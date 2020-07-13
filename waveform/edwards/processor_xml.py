import time
import pandas as pd
import logging
import xml.etree.ElementTree as ET

from deidentify.deidentifier import Deidentifier
from edwards.single_file_processor import SingleFileProcessor

class ProcessorXml(SingleFileProcessor):
    def f(self, x):
        if x is None:
            return ""
        return str(x)

    def get_cdate_and_ctime(self, str, just_return_ctime=False):
        if ' ' not in str:
            if not just_return_ctime:
                raise Exception('No space to split into cdate and ctime')
            else:
                return str
        cdate = str.split(' ')[0]
        ctime = ' '.join(str.split(' ')[1:])
        if not just_return_ctime:
            return [cdate, ctime]
        return ctime

    def create_dataframe(self, input_file):
        start_time = time.time()

        tree = ET.parse(input_file)

        root = tree.getroot()
        #print(root.tag)

        df = pd.DataFrame(columns=["Sequence", "CollectionTime", "Message", "ID", "Level", "StartTime", "SilenceTime", "EndTime", "KindLevel", "KindText", "SeverityLevel", "SeverityText"])
        #df = pd.DataFrame()
        for segment in root.findall("Segment"):
            for alarms in segment.findall("Alarms"):
                for alarm in alarms.findall("Alarm"):
                    cdate, ctime = self.get_cdate_and_ctime(alarms.attrib['CollectionTime'])

                    '''
                    if self.debug_yn:
                        print("Sequence", Deidentifier.get_sequence(cdate, dob, mask),
                               "CollectionTime", ctime,
                               "Message", self.f(alarm[0].text),
                               "ID", self.f(alarm[1].text),
                               "Level", self.f(alarm[2].text),
                               "StartTime", self.get_cdate_and_ctime(self.f(alarm[3].text), True),
                               "SilenceTime", self.get_cdate_and_ctime(self.f(alarm[5].text), True),
                               "EndTime", self.get_cdate_and_ctime(self.f(alarm[7].text), True),
                               "KindLevel", self.f(alarm[9].attrib['Level']),
                               "KindText", self.f(alarm[9].text),
                               "SeverityLevel", self.f(alarm[10].attrib['Level']),
                               "SeverityText", self.f(alarm[10].text))
                    '''
                    # the append doesn't happen in-place
                    df = df.append({"Sequence": Deidentifier.get_sequence(cdate, self.dob, self.mask),
                               "CollectionTime": ctime,
                               "Message": self.f(alarm[0].text),
                               "ID": self.f(alarm[1].text),
                               "Level": self.f(alarm[2].text),
                               "StartTime": self.get_cdate_and_ctime(self.f(alarm[3].text), True),
                               "SilenceTime": self.get_cdate_and_ctime(self.f(alarm[5].text), True),
                               "EndTime": self.get_cdate_and_ctime(self.f(alarm[7].text), True),
                               "KindLevel": self.f(alarm[9].attrib['Level']),
                               "KindText": self.f(alarm[9].text),
                               "SeverityLevel": self.f(alarm[10].attrib['Level']),
                               "SeverityText": self.f(alarm[10].text)}, ignore_index=True)

        elapsed_time = time.time() - start_time
        logging.debug(f"ProcessorXml.create_dataframe elapsed_time: {elapsed_time}")

        return df
