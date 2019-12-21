import time
import pandas as pd
import os
#import sys
#from pathlib import Path
from vitalfilepy import VitalFile
#from vitalfilepy import VITALBINARY

start_time = time.time()
#path = 'C:\\Users\\YuPan\\Downloads\\Cannenson\\stps\\testout'
in_path = '/Users/yp/Downloads/wftools/data_extraction/test_output'
out_path = '/Users/yp/Downloads/waveform/test_data/vitals'
files = []
for r,d,f in os.walk(in_path):
    for file in f:
        if '.vital' in file:
            filename = os.path.join(r, file)
            print(filename)
            data = []
            with VitalFile(filename, "r") as f:
                f.readHeader()
                line = f.readVitalData()
                try:
                    while True:
                        data.append(f.readVitalData())
                except:
                    pass
            print(len(data))
            df = pd.DataFrame(data, columns =['value','offset','low','high'])
            #df.waveform(os.path.join(r, file.split(".")[0])+".csv", header=True)
            df.to_csv(os.path.join(out_path, file.split(".")[0]) + ".csv", header=True)

elapsed_time = time.time() - start_time
print("elapsed_time: ", elapsed_time)

