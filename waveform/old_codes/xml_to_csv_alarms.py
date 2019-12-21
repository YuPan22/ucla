import xml.etree.ElementTree as ET
import os
#import sys
#import codecs
from datetime import datetime

import configparser 


'''
CLIN_ENG_WCATHL4-1567611924.xml 4473298 1832304559
CLIN_ENG_WMOR8-1563486442.xml 4487595 386971832
CLIN_ENG_WMOR23-1564670746.xml 5883791 1323571570
CLIN_ENG_WCATHL3-1569512080.xml 4635037 386370657
CLIN_ENG_WMOR10-1560977286.xml  2227725 1072956326
'''

mrn2mask = {'4473298':(1832304559, '9/1/1940', '1053498419', '1832304229', 'CLIN NG_WCATHL4-1567611924.Stp'), 
            '4487595':(386971832, '3/7/1950', '1374033569', '386971641', 'CLIN ENG WMOR8-1563486442.Stp'), 
            '5883791':(1323571570, '6/20/2019', '774373930', '1323571277', 'CLIN ENG_WMOR23-1564670746.Stp'), 
            '4635037':(386370657, '3/14/1947', '248502009', '386370318', 'CLIN ENG_WCATHL3-1569512080.Stp'), 
            '2227725':(1072956326, '5/16/1932', '94472141', '1072956169', 'CLIN ENG_WMOR10-1560977286.Stp')}

def f(x):
    if x is None:
        return ""
    return str(x)

# map_label_values
def mlv(waveform, label):
    if label == waveform.attrib['Label']:
        return "\"" + waveform.text + "\""
    return ""

def mlv_wrapper(waveform, labels):
    str = ""
    for label in labels:
        str = str + mlv(waveform, label) + ","
    return str[:-1]

#input_file = "/Users/yp/Downloads/wftools/data_extraction/test_data/6N_W6645-1539741315.xml"
input_file = "/Users/yp/Downloads/wftools/5xmls/CLIN_ENG_WCATHL4-1567611924.xml"
#input_file = "C:\\Users\\YuPan\\Downloads\\Cannenson\\CLIN ENG_WMOR23-deidentified.xml"

#base = os.path.basename(os.path.normpath(input_file)).split(".")[0]
base = os.path.basename(os.path.normpath(input_file)).split("-")[0]
print("base: ", base)

tree = ET.parse(input_file)

root = tree.getroot()
print(root.tag)

s_wf = set()
for waveforms in root.findall("Segment")[0].findall("Waveforms"):
    for waveformdata in waveforms.findall("WaveformData"):
        s_wf.add(waveformdata.attrib['Label'])
labels_wf = sorted(list(s_wf))

s_vs = set()
for vitalsigns in root.findall("Segment")[0].findall("VitalSigns"):
    for vitalsign in vitalsigns.findall("VitalSign"):
        s_vs.add(vitalsign[0].text)
labels_vs = sorted(list(s_vs))
print("labels_vs: ", labels_vs)

patient_mrn = root.findall("Segment")[0].findall("PatientName")[0].attrib['ID']
print("patient_mrn: ", patient_mrn)
mask, dob, encounter_id, study_id, stpfilename = mrn2mask[patient_mrn]
print("mask: ", mask, "dob: ", dob)

#'''
output_file_prefix = "/Users/yp/Downloads/wftools/3csvout5/" + study_id
print("output_file_prefix: ", output_file_prefix)
print(os.path.exists(output_file_prefix))
if not os.path.exists(output_file_prefix):
    os.makedirs(output_file_prefix)

#output_waveforms = output_file_prefix + "/" + base + "_waveforms.csv"
#output_vitalsigns = output_file_prefix + "/" + base + "_vitalsigns.csv"
#output_alarms = output_file_prefix + "/" + base + "_alrms.csv"
output_waveforms = output_file_prefix + "/" + study_id+ "_" + encounter_id + "_waveforms.csv"
output_vitalsigns = output_file_prefix + "/" + study_id+ "_" + encounter_id +  "_vitalsigns.csv"
output_alarms = output_file_prefix + "/" + study_id+ "_" + encounter_id +  "_alrms.csv"
#'''

'''
output_file_prefix = "C:\\Users\\YuPan\\Downloads\\Cannenson\\csv"
output_waveforms = output_file_prefix + "\\" + base + "_waveforms.csv"
output_vitalsigns = output_file_prefix + "\\" + base + "_vitalsigns.csv"
output_alarms = output_file_prefix + "\\" + base + "_alrms.csv"
'''

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%m/%d/%Y")
    d2 = datetime.strptime(d2, "%m/%d/%Y")
    return abs((d2 - d1).days)

#print(days_between("9/1/1940", "9/4/2019"))

def get_sequence(date_to_mask, dob, mask):
    return str(days_between(dob, date_to_mask) + mask)

def get_cdate_and_ctime(str, just_return_ctime=False):
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

with open(output_alarms, 'w', encoding='utf-8') as foa, open(output_vitalsigns, 'w', encoding='utf-8') as fov, open(output_waveforms, 'w', encoding='utf-8') as fow:
    #foa.write("CollectionTime,Message,ID,Level,StartTime,StartTimeUTC,SilenceTime,SilenceTimeUTC,EndTime,EndTimeUTC,KindLevel,KindText,SeverityLevel,SeverityText\n")
    foa.write("Sequence,CollectionTime,Message,ID,Level,StartTime,SilenceTime,EndTime,KindLevel,KindText,SeverityLevel,SeverityText\n")
    #fov.write("CollectionTime,DeviceName,Parameter,BpChannel,Time,TimeUTC,UOM,Q,Text,AlarmLimitLow,AlarmLimitHigh\n")
    #fov.write("Sequence,CollectionTime,DeviceName,Parameter,BpChannel,Time,UOM,Q,Text,AlarmLimitLow,AlarmLimitHigh\n")
    fov.write("Sequence,CollectionTime," + ','.join([label+"-BpChannel,"+label+"-Time,"+label+"-UOM,"+label+"-Q,"+label+"-Text,"+label+"-AlarmLimitLow,"+label+"-AlarmLimitHigh" for label in labels_vs]) + "\n")
    #fow.write("SegmentNo,SegmentOffset,CollectionTime,TTX,DisplayOrder,ID,UOM,Cal,SampleRate,SamplePeriodInMsec,Samples,CO₂,I,II,III,Label,Pleth,Resp,V,V1,aVF,aVL,aVR\n")
    #fow.write("SegmentNo,SegmentOffset,CollectionTime,TTX,DisplayOrder,ID,UOM,Cal,SampleRate,SamplePeriodInMsec,Samples,"+','.join(labels)+"\n")
    fow.write("Sequence,CollectionTime," + ','.join([label+","+label+"-SampleRate"+","+label+"-UOM" for label in labels_wf]) + "\n")
    for segment in root.findall("Segment"):
        for alarms in segment.findall("Alarms"):
            for alarm in alarms.findall("Alarm"):
                cdate, ctime = get_cdate_and_ctime(alarms.attrib['CollectionTime'])
                row = get_sequence(cdate, dob, mask) + "," + ctime + "," + f(alarm[0].text) + "," + f(alarm[1].text) + "," + f(alarm[2].text) + "," + get_cdate_and_ctime(f(alarm[3].text),True) + "," + get_cdate_and_ctime(f(alarm[5].text),True) + "," + get_cdate_and_ctime(f(alarm[7].text),True) + "," + f(alarm[9].attrib['Level']) + "," + f(alarm[9].text) + "," + f(alarm[10].attrib['Level']) + "," + f(alarm[10].text) +"\n"
                foa.write(row)
        for vitalsigns in segment.findall("VitalSigns"):
            vs = {}
            for vitalsign in vitalsigns.findall("VitalSign"):
                #cdate, ctime = get_cdate_and_ctime(vitalsigns.attrib['CollectionTime'])
                #row = get_sequence(cdate, dob, mask) + "," + ctime + "," + vitalsign.attrib['DeviceName'] + "," + f(vitalsign[0].text) + "," + f(vitalsign[1].text) + "," + get_cdate_and_ctime(f(vitalsign[2].text),True) + "," + f(vitalsign[4].attrib['UOM']) + "," + f(vitalsign[4].attrib['Q']) + "," + f(vitalsign[4].text) + "," + f(vitalsign[5].text) + "," + f(vitalsign[6].text) +"\n"
                #fov.write(row)
                vs[vitalsign[0].text] = f(vitalsign[1].text) + "," + get_cdate_and_ctime(f(vitalsign[2].text),True) + "," + f(vitalsign[4].attrib['UOM']) + "," + f(vitalsign[4].attrib['Q']) + "," + f(vitalsign[4].text) + "," + f(vitalsign[5].text) + "," + f(vitalsign[6].text)
            #print(vitalsigns.attrib['CollectionTime'])
            try:
                cdate, ctime = get_cdate_and_ctime(vitalsigns.attrib['CollectionTime'])
                row = get_sequence(cdate, dob, mask) + "," + ctime + ","
                for label in labels_vs:
                    row += vs.get(label, ","*6) + ","
                fov.write(row[:-1] + "\n")
            except:
                pass
        for waveforms in segment.findall("Waveforms"):
            wf = {}
            for waveform in waveforms.findall("WaveformData"):
                #row = segment.attrib['N'] + "," + segment.attrib['Offset'] + "," + waveforms.attrib['CollectionTime'] + "," + f(waveforms.attrib['TTX']) + "," + f(waveforms.attrib['DisplayOrder']) + "," + f(waveform.attrib['ID']) + "," + f(waveform.attrib['Label']) + "," + f(waveform.attrib['UOM']) + "," + "\"" + f(waveform.attrib['Cal']) + "\"" + "," + f(waveform.attrib['SampleRate']) + "," + f(waveform.attrib['SamplePeriodInMsec']) + "," + f(waveform.attrib['Samples']) + "," + "\"" + waveform.text + "\"" +"\n"
                #row = segment.attrib['N'] + "," + segment.attrib['Offset'] + "," + waveforms.attrib['CollectionTime'] + "," + f(waveforms.attrib['TTX']) + "," + f(waveforms.attrib['DisplayOrder']) + "," + f(waveform.attrib['ID']) + "," + f(waveform.attrib['UOM']) + "," + "\"" + f(waveform.attrib['Cal']) + "\"" + "," + f(waveform.attrib['SampleRate']) + "," + f(waveform.attrib['SamplePeriodInMsec']) + "," + f(waveform.attrib['Samples']) + "," + mlv_wrapper(waveform, labels) +"\n"
                #fow.write(row)
                wf[waveform.attrib['Label']] = "\"" + waveform.text + "\"" + "," + f(waveform.attrib['SampleRate']) + "," + f(waveform.attrib['UOM'])
            try:
                cdate, ctime = get_cdate_and_ctime(waveforms.attrib['CollectionTime'])
                row = get_sequence(cdate, dob, mask) + "," + ctime + ","
                for label in labels_wf:
                    row += wf.get(label, ","*2) + ","
                fow.write(row[:-1] + "\n")
            except:
                pass

#grep "Waveforms CollectionTime" /Users/yp/Downloads/wftools/5xmls/CLIN_ENG_WMOR23-deidentified.xml | wc -l
#awk -F "," '{print $12}' 3csvout3/CLIN_ENG_WCATHL3-deidentified_waveforms.csv | head -1

