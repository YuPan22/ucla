#! /bin/bash

<<COMMENT
1, get "filename {adibin.csv header}"
2, get xml in terms of filename, then
3, remove bed unit from csv names
COMMENT


# Usage: ./create_waveform_catalog.sh "/opt/genomics/WaveFormProcessedFiles/codes/CsvOutputs_test" $(pwd)/waveform_catalog_test.txt "/opt/genomics/WaveFormProcessedFiles/codes/WaveFormProcessedFiles_2_stps"

csvs_dir="$1"

catalog="$2"

input_base="$3"

if [ -e $catalog ]; then rm $catalog; fi

for csv in `ls -1 $csvs_dir/*/*/*.adibin.csv`
do

#dir=$(dirname $csv)
#file=$(basename $csv)

IN="$csv"
split=(${IN//\// })
echo "${split[-3]}/${split[-2]}/${split[-1]},$(head -1 $csv)" >> $catalog

done

cat << EOF > create_wc_step2.py
import os
import glob
import logging

logging.basicConfig(level=logging.INFO)

input_base="$input_base"

with open("$catalog", "r") as wc1, open("${catalog}.final", "w") as wc2:
    wc2.write("Channel,Filename,Calibration\n")
    line = wc1.readline()
    while line:
        sp = line.rstrip().split(",")
        logging.info(sp)
        sp2 = os.path.basename(sp[0]).split("-")  #1832304229_1053498419_CLIN_ENG_WCATHL4-1567611924_1832333416~084529_1832333416~091629.adibin.csv
        dir1 = "_".join(sp2[0].split("_")[2:])
        dir2 = f"{dir1}-{sp2[1].split('_')[0]}"
        xml_dir_path = os.path.join(input_base, dir1, dir2, "XML")
        logging.info(f"xml_dir_path: {xml_dir_path}")
        for i in range(3, len(sp)): # "filename, Sequence, CollectionTime, col1, col2, col3, ..."
            for xml_file_path in glob.iglob(xml_dir_path+'/**', recursive=True):
                if os.path.isfile(xml_file_path) and "_0_wf.xml" in xml_file_path:
                    logging.info(f"processing: {xml_file_path}")
                    with open(xml_file_path, "r") as inf:
                        xml_line = inf.readline()
                        logging.info(xml_line)
                        while xml_line:
                            if f'Label="{sp[i]}"' in xml_line:
                                logging.info(f"xml_line: {xml_line}")
                                sp3 = xml_line.split('Cal="')
                                cal = sp3[1].split('"')[0]

                                csv_filename = os.path.basename(sp[0])
                                sp4 = csv_filename.split("-")
                                head = "_".join(sp4[0].split("_")[:2])
                                tail = "_".join(sp4[1].split("_")[1:])
                                new_csv_filename = f"{head}-{tail}"
                                new_csv_path = os.path.join(os.path.dirname(sp[0]), new_csv_filename)

                                wc2.write(f'{sp[i]},{new_csv_path},"{cal}"\n')
                                break
                            else:
                                xml_line = inf.readline()
        line = wc1.readline()


for csv_file_path in glob.iglob("$csvs_dir"+'/**', recursive=True):
    if os.path.isfile(csv_file_path) and ".csv" in csv_file_path:
        csv_filename = os.path.basename(csv_file_path)
        sp = csv_filename.split("-")
        head = "_".join(sp[0].split("_")[:2])
        tail = "_".join(sp[1].split("_")[1:])
        new_csv_filename = f"{head}-{tail}"
        new_csv_path = os.path.join(os.path.dirname(csv_file_path), new_csv_filename)
        os.rename(csv_file_path, new_csv_path)
EOF

python create_wc_step2.py

echo total_done
