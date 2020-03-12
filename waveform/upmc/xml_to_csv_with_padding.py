import time
import pandas as pd
import logging
import xml.etree.ElementTree as ET
import numpy as np

from deidentify.deidentifier import Deidentifier

class UPMC():
    def __init__(self, max_sample_rate):
        self.MAX_SAMPLE_RATE = max_sample_rate

    def pad_list(self, arr):
        if len(arr) < self.MAX_SAMPLE_RATE:
            lists = [arr, [np.nan]*(self.MAX_SAMPLE_RATE-len(arr))]
            return [x for t in zip(*lists) for x in t]
        return arr

    def xml_to_csv(self, input_path, input_file, output_file, dob, mask):
        print(input_path, input_file, output_file, dob, mask)
        tree = ET.parse(input_path)

        root = tree.getroot()
        print(root.tag)

        frames = []
        ct = 0
        for segment in root.findall("Segment"):
            for waveform_per_sec in segment.findall("Waveforms"):
                ct += 1
                #sample_rate = float("inf")
                sample_rate = 256
                init = True
                for waveform_per_channel in waveform_per_sec.findall("WaveformData"):
                    print(waveform_per_channel.text, waveform_per_channel.attrib['Label'])
                    #if sample_rate == float("inf"):
                    if init:
                        sp = waveform_per_channel.text.split(',')
                        sp = self.pad_list(sp)
                        print("$$$$$$$$$$$$$$$$$$", len(sp))
                        df_per_sec = pd.DataFrame(sp, columns=[waveform_per_channel.attrib['Label']])
                        #sample_rate = int(waveform_per_channel.attrib['SampleRate'])
                        init = False
                    else:
                        sp = waveform_per_channel.text.split(',')
                        sp = self.pad_list(sp)
                        df_per_sec[waveform_per_channel.attrib['Label']] = sp
                        print("=================", waveform_per_channel.attrib['Label'], waveform_per_channel.text.split(','),len(waveform_per_channel.text.split(',')))

                        #xtra = {waveform_per_channel.attrib['Label']: waveform_per_channel.text.split(',')}
                        #df_per_sec = df_per_sec.append(xtra, ignore_index=True)

                    df_per_sec_begin_time = pd.to_datetime(waveform_per_sec.attrib['CollectionTime'])
                    df_per_sec['timestamp'] = df_per_sec_begin_time + pd.to_timedelta(df_per_sec.index * 1/(sample_rate), unit='s')

                frames.append(df_per_sec)
                #if ct == 10:
                    #break
            #break

        if len(frames) > 0:
            df = pd.concat(frames, sort=False)

            df['Sequence'] = [Deidentifier.get_sequence(str(d.date()), dob, mask) for d in df['timestamp']]
            df['CollectionTime'] = [str(d.time()) for d in df['timestamp']]
            #df = df.set_index('timestamp')
            del df['timestamp']
            cols = df.columns.tolist()
            cols = cols[-2:] + cols[:-2]
            ret = df[cols]

            #print(ret)
            #print(len(ret))
            ret.to_csv(output_file+"/converted_"+input_file.replace(" ",""), index=False)

if __name__ == '__main__':
    start = time.time()

    input_file = "/opt/genomics/WaveFormProcessedFiles/CLIN_ENG_WCATHL4/CLIN_ENG_WCATHL4-1567611924/XML/CLIN ENG_WCATHL4-1567611924_20200115175143_0_wf.xml"
    output_file = "/opt/genomics/WaveFormProcessedFiles/codes/upmc2.csv"
    upmc = UPMC(256)
    upmc.xml_to_csv(input_file, output_file)

    end = time.time()
    logging.info(f"__main__ runtime: {end - start}")

# python __main__.py -input "/opt/genomics/WaveFormProcessedFiles/CLIN_ENG_WCATHL4/CLIN_ENG_WCATHL4-1567611924/XML" -output "/opt/genomics/WaveFormProcessedFiles/codes/upmc" -type "deidXml"



