import re

from deidentify.deidentifier import Deidentifier

#src_filepath = '/Users/yp/Downloads/wftools/5xmls/CLIN_ENG_WCATHL3-1569512080.xml'
#des_filepath = '/Users/yp/Downloads/wftools/5xmls/CLIN_ENG_WCATHL3-1569512080_de.xml'

#src_filepath = "C:\\Users\\YuPan\\Downloads\\Cannenson\\CLIN ENG_WMOR23-1564670746.xml"
#des_filepath = "C:\\Users\\YuPan\\Downloads\\Cannenson\\CLIN ENG_WMOR23-deidentified.xml"

def deidentify_xml(src_filepath, file, des_filepath, dob, mask):
    sp = file.split(".xml")
    output_file = des_filepath+"/"+sp[0]+"_deidentified.xml"
    with open(src_filepath) as src:
        with open(output_file, 'w') as des:
            line = src.readline()
            while line:
                matched_id = re.search("PatientName ID=\"[0-9]+\"", line)
                if matched_id != None:
                    #print("matched_id: ", matched_id.group())
                    line = re.sub(matched_id.group(), "PatientName ID=\"\"", line)

                if "PatientName" in line:
                    matched_name = re.search("\>.+\<\/PatientName", line)
                    if matched_name != None:
                        line = re.sub(matched_name.group(), "></PatientName", line)

                matched_date = re.search("\d{1,2}/\d{1,2}/\d{4} ", line)
                if matched_date != None:
                    line = line.replace(matched_date.group(), Deidentifier.get_sequence(matched_date.group(), dob, mask))

                if "Filename" in line:
                    matched_utc = re.search("\-\d{10}\.", line)
                    if matched_utc != None:
                        line = re.sub(matched_utc.group()[0:-1], "", line)

                if "UTC" in line:
                    matched_utc = re.search("[\"|\>]\d{10}[\"|\<]", line)
                    if matched_utc != None:
                        line = re.sub(matched_utc.group()[1:-1], "", line)

                des.write(line)
                line = src.readline()
