#! /bin/bash

# Usage: ./create_waveform_catalog.sh /home2/yup1/CsvOutputs $(pwd)/waveform_catalog.txt

csvs_dir="$1"

catalog="$2"

if [ -e $catalog ]; then rm $catalog; fi

for csv in `ls -1 $csvs_dir/*/*.adibin.csv`
do

#dir=$(dirname $csv)
#file=$(basename $csv)

IN="$csv"
split=(${IN//\// })
echo "${split[-3]}/${split[-2]}/${split[-1]},$(head -1 $csv)" >> $catalog

done

cat << EOF > create_wc_step2.py
with open("$catalog", "r") as wc1, open("${catalog}.final", "w") as wc2:
    wc2.write("Channel,Filename\n")
    line = wc1.readline()
    while line:
        sp = line.rstrip().split(",")
        print(sp)
        for i in range(3, len(sp)):
            wc2.write(f"{sp[i]},{sp[0]}\n")
        line = wc1.readline()
EOF

python create_wc_step2.py

echo total_done
