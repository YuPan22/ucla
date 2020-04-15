import time
import datetime
from datetime import timedelta
import pandas as pd
from pandas import HDFStore
import numpy as np
import logging
import xml.etree.ElementTree as ET
import os
import copy

from deidentify.deidentifier import Deidentifier

class UPMC:
    def xml_to_csv_waveforms(self, input_path, input_file, output_file_path, dob, mask):
        tree = ET.parse(input_path)
        root = tree.getroot()
        print(f'xml_to_csv_waveforms processing {input_file}')

        sample_rates = {}
        SamplePeriodInMsec_per_sample_rates = {}

        start_pass1 = time.time()

        for segment in root.findall("Segment"):
            for waveform_per_sec in segment.findall("Waveforms"):
                for waveform_per_channel in waveform_per_sec.findall("WaveformData"):
                    sample_rate = int(waveform_per_channel.attrib['SampleRate'])
                    SamplePeriodInMsec = int(waveform_per_channel.attrib['SamplePeriodInMsec'])
                    if sample_rate not in sample_rates:
                        sample_rates[sample_rate] = {}
                    channel = waveform_per_channel.attrib["Label"]
                    sample_rates[sample_rate][channel] = [""]*sample_rate

        print(f'sample_rates.keys: {sample_rates.keys()}')

        for key in sample_rates.keys():
            output_file = output_file_path + "/" + input_file.replace(" ", "_").replace(".xml","") + "_Waveforms_" + str(key) + ".csv"
            try:
                os.remove(output_file)
            except OSError:
                pass

        end_pass1 = time.time()
        print(f"pass1 runtime: {end_pass1 - start_pass1}")

        ct = 0
        for segment in root.findall("Segment"):
            for waveform_per_sec in segment.findall("Waveforms"):
                ct += 1
                new_sample_rates = copy.deepcopy(sample_rates)

                cdate, ctime = self.get_cdate_and_ctime(waveform_per_sec.attrib['CollectionTime'])
                sequence = Deidentifier.get_sequence(cdate, dob, mask)
                dt = datetime.datetime.strptime(waveform_per_sec.attrib['CollectionTime'], '%m/%d/%Y %I:%M:%S %p')

                for waveform_per_channel in waveform_per_sec.findall("WaveformData"):
                    sample_rate = int(waveform_per_channel.attrib['SampleRate'])
                    channel = waveform_per_channel.attrib["Label"]
                    new_sample_rates[sample_rate][channel] = waveform_per_channel.text.split(',')


                for key, val in new_sample_rates.items():
                    output_file = output_file_path + "/"+input_file.replace(" ", "_").replace(".xml","") + "_Waveforms_" + str(key)+".csv"
                    file_exist = os.path.exists(output_file)
                    with open(output_file, "a") as fow:
                        if not file_exist:
                            fow.write("Sequence,CollectionTime,"+",".join([str(x) for x in val.keys()])+"\n")
                        for row in zip(*val.values()):
                            dt += datetime.timedelta(microseconds=1024) #milliseconds
                            fow.write(sequence+","+dt.strftime('%H:%M:%S.%f')+","+ ",".join([str(x) for x in row]) + "\n")

    def get_xml_prefix(self, input_file, dob, mask):
        #return input_file.replace(" ", "_").replace(".xml","")
        utc = input_file.split("-")[1].split("_")[0]
        d = datetime.datetime.utcfromtimestamp(int(utc))
        sequence = Deidentifier.get_sequence(str(d.date()), dob, mask)
        t = str(d.time())
        ret = input_file.replace(utc, f'{sequence}:{t}').replace(" ", "_").replace(".xml","")
        return ret

    def get_modified_output_path(self, xml_prefix, output_file_path):
        new_output_file_path = os.path.join(output_file_path, xml_prefix)
        if not os.path.exists(new_output_file_path):
            os.makedirs(new_output_file_path)  #this equals to mkdir -p
        return new_output_file_path

    def xml_to_csv_waveforms_pandas(self, input_path, input_file, output_file_path, dob, mask):
        tree = ET.parse(input_path)
        root = tree.getroot()
        print(f'xml_to_csv_waveforms_pandas processing {input_file}')

        dfs = {}
        ct = 0
        start_append = time.time()
        for segment in root.findall("Segment"):
            for waveform_per_sec in segment.findall("Waveforms"):
                ct += 1
                dfs_per_sec = {}
                #print(f'!!!!!!!!!!!!!!!!!!!!!!!ct: {ct}')
                #if ct >= 4:
                #    break

                for waveform_per_channel in waveform_per_sec.findall("WaveformData"):

                    sample_rate = int(waveform_per_channel.attrib['SampleRate'])
                    #print(f'sample_rate: {sample_rate}, ct: {ct}')

                    col = f'{waveform_per_channel.attrib["Label"]}(UOM={waveform_per_channel.attrib["UOM"]} Cal={waveform_per_channel.attrib["Cal"].replace(",",";")})'
                    #col = f'{waveform_per_channel.attrib["Label"]}'
                    sp = waveform_per_channel.text.split(',')

                    if sample_rate not in dfs_per_sec:
                        dfs_per_sec[sample_rate] = pd.DataFrame(sp, columns=[col])
                    else:
                        dfs_per_sec[sample_rate][col] = sp
                        #print("=================", waveform_per_channel.attrib['Label'], waveform_per_channel.text.split(','), len(waveform_per_channel.text.split(',')))

                        # xtra = {waveform_per_channel.attrib['Label']: waveform_per_channel.text.split(',')}
                        # df_per_sec = df_per_sec.append(xtra, ignore_index=True)

                    df_per_sec_begin_time = pd.to_datetime(waveform_per_sec.attrib['CollectionTime'])
                    dfs_per_sec[sample_rate]['timestamp'] = df_per_sec_begin_time + pd.to_timedelta(dfs_per_sec[sample_rate].index * 1 / (sample_rate), unit='s')
                    #time_delta = int(waveform_per_channel.attrib['SamplePeriodInMsec'])
                    #print(f'time_delta: {time_delta}')
                    #dfs_per_sec[sample_rate]['timestamp'] = df_per_sec_begin_time + pd.Timedelta(np.timedelta64(time_delta, 'ms'))

                    if sample_rate not in dfs:
                        dfs[sample_rate] = []

                for sample_rate in dfs_per_sec.keys():
                    dfs[sample_rate].append(dfs_per_sec[sample_rate])

        end_append = time.time()
        print(f"append runtime: {end_append - start_append}")

        print(f'ct: {ct}')
        print(dfs.keys())

        if len(dfs.keys())>0:
            for sample_rate, df_array in dfs.items():
                if len(df_array) > 0:
                    start_concat = time.time()

                    df = pd.concat(df_array, sort=False)

                    #pd.set_option('display.max_columns', None)
                    #pd.set_option('display.max_rows', None)
                    #print(df.head())
                    print(df.shape)

                    end_concat = time.time()
                    print(f"concat runtime - sample_rate {sample_rate}: {end_concat - start_concat}")

                    start_trans = time.time()
                    df['Sequence'] = [Deidentifier.get_sequence(str(d.date()), dob, mask) for d in df['timestamp']]
                    df['CollectionTime'] = [str(d.time()) for d in df['timestamp']]
                    # df = df.set_index('timestamp')
                    del df['timestamp']
                    cols = df.columns.tolist()
                    cols = cols[-2:] + cols[:-2]
                    df_cleaned = df[cols]

                    end_trans = time.time()
                    print(f"trans runtime - sample_rate {sample_rate}: {end_trans - start_trans}")

                    # print(df_cleaned)
                    # print(len(df_cleaned))

                    ext = "csv"
                    #ext = "h5"
                    xml_prefix = self.get_xml_prefix(input_file, dob, mask)
                    #output_file = output_file_path + "/"+input_file.replace(" ", "_").replace(".xml","") + "_Waveforms_" + str(sample_rate)+".csv2"
                    output_file = os.path.join(self.get_modified_output_path(xml_prefix, output_file_path), xml_prefix + "_Waveforms_" + str(sample_rate)+"."+ext)
                    print(f'writing to {output_file}')

                    start_to_csv = time.time()

                    df_cleaned.to_csv(output_file, index=False)

                    #store = HDFStore(output_file)
                    #store.put('dataset', df_cleaned, format='table', data_columns=True)

                    end_to_csv = time.time()
                    print(f"to_csv runtime - sample_rate {sample_rate}: {end_to_csv - start_to_csv}")

    def f(self, x):
        if x is None:
            return ""
        return str(x)

    def get_cdate_and_ctime(self, str, just_return_ctime=False):
        if ' ' not in str:
            if not just_return_ctime:
                raise Exception('No whitespace to split into cdate and ctime')
            else:
                return str
        cdate = str.split(' ')[0]
        ctime = ' '.join(str.split(' ')[1:])
        if not just_return_ctime:
            return [cdate, ctime]
        return ctime

    def xml_to_csv_vitals(self, input_path, input_file, output_file_path, dob, mask):
        tree = ET.parse(input_path)
        root = tree.getroot()
        print(f'xml_to_csv_vitals processing {input_file}')

        vss = {}
        ct = 0

        for segment in root.findall("Segment"):
            for vitals_per_sec in segment.findall("VitalSigns"):
                ct += 1
                for vitalsign in vitals_per_sec.findall("VitalSign"):
                    channel = vitalsign[0].text
                    cdate, ctime = self.get_cdate_and_ctime(vitals_per_sec.attrib['CollectionTime'])
                    sequence = Deidentifier.get_sequence(cdate, dob, mask)
                    if channel not in vss:
                        vss[channel] = []
                    vss[channel].append(",".join([sequence, ctime, self.f(vitalsign[4].text), self.f(vitalsign[5].text), self.f(vitalsign[6].text), self.f(vitalsign[4].attrib['UOM'])]))

        xml_prefix = self.get_xml_prefix(input_file, dob, mask)
        for channel, arr in vss.items():
            #output_file = output_file_path + "/" + input_file.replace(" ", "_").replace(".xml", "") + "_VitalSigns_" + channel + ".csv"
            output_file = os.path.join(self.get_modified_output_path(xml_prefix, output_file_path), xml_prefix + "_VitalSigns_" + channel + ".csv")
            with open(output_file, "w") as fov:
                fov.write("Sequence,CollectionTime,Value,AlarmLimitLow,AlarmLimitHigh,UOM\n")
                for row in arr:
                    fov.write(row + "\n")

    def xml_to_csv_alarms(self, input_path, input_file, output_file_path, dob, mask):
        tree = ET.parse(input_path)
        root = tree.getroot()
        print(f'xml_to_csv_alarms processing {input_file}')

        msgs = []
        ct = 0

        for segment in root.findall("Segment"):
            for alarms_per_sec in segment.findall("Alarms"):
                ct += 1
                for alarm in alarms_per_sec.findall("Alarm"):
                    cdate, ctime = self.get_cdate_and_ctime(alarms_per_sec.attrib['CollectionTime'])
                    sequence = Deidentifier.get_sequence(cdate, dob, mask)
                    msgs.append(",".join([sequence, ctime,  self.f(alarm[0].text), self.f(alarm[1].text), self.f(alarm[2].text), \
                                          self.get_cdate_and_ctime(self.f(alarm[3].text),True), self.get_cdate_and_ctime(self.f(alarm[5].text),True), self.get_cdate_and_ctime(self.f(alarm[7].text),True), \
                                          self.f(alarm[9].attrib['Level']), self.f(alarm[9].text), self.f(alarm[10].attrib['Level']), self.f(alarm[10].text)]))

        xml_prefix = self.get_xml_prefix(input_file, dob, mask)
        #output_file = output_file_path + "/" + input_file.replace(" ", "_").replace(".xml", "") + "_Alarms.csv"
        output_file = os.path.join(self.get_modified_output_path(xml_prefix, output_file_path), xml_prefix + "_Alarms.csv")
        with open(output_file, "w") as foa:
            foa.write("Sequence,CollectionTime,Message,ID,Level,StartTime,SilenceTime,EndTime,KindLevel,KindText,SeverityLevel,SeverityText\n")
            for row in msgs:
                foa.write(row + "\n")

if __name__ == '__main__':
    start = time.time()

    input_file_path = "/opt/genomics/WaveFormProcessedFiles/CLIN_ENG_WCATHL4/CLIN_ENG_WCATHL4-1567611924/XML/CLIN ENG_WCATHL4-1567611924_20200115175143_0_wf.xml"
    output_file_path = "/opt/genomics/WaveFormProcessedFiles/codes"
    upmc = UPMC()
    upmc.xml_to_csv(input_file_path, os.path.basename(input_file_path), output_file_path, "1950-03-07", "2107039137")

    end = time.time()
    print(f"__main__ runtime: {end - start}")

# python __main__.py -input "/opt/genomics/WaveFormProcessedFiles/CLIN_ENG_WCATHL4/CLIN_ENG_WCATHL4-1567611924/XML" -output "/opt/genomics/WaveFormProcessedFiles/codes/upmc" -type "deidXml"
