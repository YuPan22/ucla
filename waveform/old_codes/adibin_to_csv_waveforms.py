from binfilepy import binfile
import sys
#import imp
#import importlib
import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
#imp.reload(binfile)
import os

#path = 'C:\\Users\\YuPan\\Downloads\\Cannenson\\stps\\testout'
in_path = '/Users/yp/Downloads/wftools/data_extraction/test_output'
out_path = '/Users/yp/Downloads/waveform/test_data/waveforms'

files = []

for r,d,f in os.walk(in_path):
    for file in f:
        if '.adibin' in file:
            filename = os.path.join(r, file)
            print(filename)

            #filename = 'C:\\Users\\YuPan\\Downloads\\Cannenson\\stps\\testout\\_20190926142533_20190926142729.adibin' 
            #filename = '/Users/yp/Downloads/wftools/data_extraction/test_output/_20181016190358_20181016192210.adibin'
            #filename = '/Users/yp/Downloads/wftools/data_extraction/test_output/_20181016192210_20181017111840.adibin'
            with binfile.BinFile(filename, "r") as f:
                # You must read header first before you can read channel deidentify
                f.readHeader()
                # I want to read the entire file
                data = f.readChannelData(offset=0, length=0, useSecForOffset=False, useSecForLength=False)

            print('Dataformat: ', f.header.DataFormat)
            print('Year: ', f.header.Year)
            print('Month: ', f.header.Month)
            print('Day: ', f.header.Day)
            print('Hour: ', f.header.Hour)
            print('Minute: ', f.header.Minute)
            print('Second: ', f.header.Second)
            print('Seconds per tick: ', f.header.secsPerTick) #sampling rate 300 Hz

            starttime = pd.to_datetime(str(f.header.Month)+'/'+str(f.header.Day)+'/' +str(f.header.Year)+' '+str(f.header.Hour)+':'+str(f.header.Minute)+':'+ str(f.header.Second))
            sf = 300 #this is the max sampling rate for UCI that all the files are upsampled to
            print(starttime)

            for fii in np.arange(len(f.channels)):
                print('Title: ', f.channels[fii].Title, ', Units: ', f.channels[fii].Units, ', Scale: ', f.channels[fii].scale, ', Offset: ', f.channels[fii].offset)
                if fii == 0:
                    wave = pd.DataFrame(data[fii], columns=[f.channels[fii].Title])
                else:
                    wave[f.channels[fii].Title] = data[fii]
                if f.channels[fii].Title in ['GE_ART', 'INVP1']: 
                    wave.loc[wave[f.channels[fii].Title] < 0, f.channels[fii].Title] = 0.
                if f.channels[fii].Title in ['GE_ECG', 'ECG', 'PLETH']:
                    wave.loc[wave[f.channels[fii].Title] == -1.700000e+308, f.channels[fii].Title] = 0.

            wave['timestamp'] = starttime + pd.to_timedelta(wave.index*f.header.secsPerTick, unit='s') - pd.Timedelta('8H')
            wave = wave.set_index('timestamp')
            pd.set_option('display.max_columns', None)
            pd.set_option('display.max_rows', None)
            wave.head()
            wave.shape
            #(125520, 8)
            #(262080, 8)
            #(13773600, 8)
            #total 14161200

            # https://datatofish.com/export-dataframe-to-csv/
            #wave.waveform('/Users/yp/Downloads/binfilepy/export_dataframe.csv', index = None, header=True)
            #wave.waveform('C:\\Users\\YuPan\\Downloads\\Cannenson\\stps\\testout\\export_dataframe.csv', header=True)
            wave.to_csv(os.path.join(out_path, file.split(".")[0])+".csv", header=True)

