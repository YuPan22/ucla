import xml.etree.ElementTree as ET
import os
#import sys
#import codecs
from datetime import datetime

def f(x):
    if x is None:
        return ""
    return str(x)

#input_file = "/Users/yp/Downloads/wftools/5xmls/CLIN_ENG_WCATHL4-1567611924.xml"
#input_file = "/Users/yp/Downloads/wftools/5xmls/CLIN_ENG_WMOR8-1563486442.xml"
#input_file = "/Users/yp/Downloads/wftools/5xmls/CLIN_ENG_WMOR23-1564670746.xml"
#input_file = "/Users/yp/Downloads/wftools/5xmls/CLIN_ENG_WCATHL3-1569512080.xml"
input_file = "/Users/yp/Downloads/wftools/5xmls/CLIN_ENG_WMOR10-1560977286.xml"

file = os.path.basename(input_file)

tree = ET.parse(input_file)

root = tree.getroot()
print(root.tag)

output_waveforms = "/Users/yp/Downloads/wftools/5xmls/cals_"+file+".csv"

with open(output_waveforms, 'w', encoding='utf-8') as fow:
    for segment in root.findall("Segment"):
        for waveforms in segment.findall("Waveforms"):
            for waveform in waveforms.findall("WaveformData"):
                row = f(waveform.attrib['Label']) + "," + "\"" + f(waveform.attrib['Cal']) + "\"\n"
                fow.write(row)


#grep "Waveforms CollectionTime" /Users/yp/Downloads/wftools/5xmls/CLIN_ENG_WMOR23-deidentified.xml | wc -l
#awk -F "," '{print $12}' 3csvout3/CLIN_ENG_WCATHL3-deidentified_waveforms.csv | head -1

