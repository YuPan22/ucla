#! /bin/bash

xmls_dir="$1"

for xml in `ls -1 $xmls_dir/*.xml`
do
# get last 5 lines of a xml file
end_of_file=`tail -5 $xml | tr -d "\n"`
# if end_of_file doesn't contain "/Bedmaster", notify truncation detected
if [[ $end_of_file != */Bedmaster* ]] 
then
echo "$xml Truncated"
fi
done

echo all_checked
