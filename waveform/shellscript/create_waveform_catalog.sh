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
echo "${split[-3]}/${split[-2]}/${split[-1]}, $(head -1 $csv)" >> $catalog

done

echo total_done
