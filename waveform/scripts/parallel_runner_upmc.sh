#! /bin/bash
# https://stackoverflow.com/questions/6593531/running-a-limited-number-of-child-processes-in-parallel-in-bash
# for p in `ps aux | grep wc | grep -v grep | awk '{print $2}'`; do kill -9 $p; done

#job_type="toCsv"
job_type="deidXml"

#input_path="/opt/genomics/WaveFormProcessedFiles"
#input_path="/home2/yup1/WaveFormProcessedFiles_2_stps"
#input_path="/opt/genomics/WaveFormProcessedFiles/codes/WaveFormProcessedFiles_2_stps"
input_path="/opt/genomics/WaveFormProcessedFiles"

#output_path="/opt/genomics/WaveFormProcessedFiles/CsvOutputs"
#output_path="/home2/yup1/CsvOutputs"
#output_path="/opt/genomics/WaveFormProcessedFiles/codes/CsvOutputs"
output_path="/opt/genomics/WaveFormProcessedFiles/codes/upmc3"

index=0
max_jobs=7 # the total number of jobs should NOT be less than max_jobs-1, if you have a single job, max_jobs=2, otherwise, the run will hang forever.
# lapgnomap15 and lapgnomap16 each has 8 vcores.

#code_path="/home2/yup1/waveform"
code_path="/opt/genomics/WaveFormProcessedFiles/codes/waveform"

#bp_path="/home2/yup1/binfilepy_git"
bp_path="/opt/genomics/WaveFormProcessedFiles/codes/binfilepy_git"

start=`date +%s`

function add_next_job {
   # if still jobs to do then add one
   if [[ $index -lt ${#todo_array[*]} ]]
   # apparently stackoverflow doesn't like bash syntax
   # the hash in the if is not a comment - rather it's bash awkward way of getting its length
   then
       echo adding job ${todo_array[$index]}
       do_job ${todo_array[$index]} &
       # replace the line above with the command you want
       index=$(($index+1))
   fi
}

set -o monitor
# means: run background processes in a separate processes...
trap add_next_job CHLD
# execute add_next_job when we receive a child complete signal

#todo_array=($(find $input_path -name "*ENG_*-*" -type d))
todo_array=($(find $input_path -type d -name "8ICU_W*-*" -o -type d -name "7ICU_W*-*" -o -type d -name "7N_W*-*"))
#todo_array=($(find $input_path -type d -name "7CCU_W*-*" -o -type d -name "7W_W*-*"))

function do_job {
    echo "starting job $1"

    cd $code_path

    if [ $job_type = "toCsv" ]
    then
        python __main__.py -input "${todo_array[$index]}" -output "$output_path" -type "toCsv" -bp "${bp_path}"
    else
        python __main__.py -input "${todo_array[$index]}" -output "$output_path" -type "deidXml"
    fi

    sleep 2
}

# add initial set of jobs
while [[ $index -lt $max_jobs ]]
do
   add_next_job
done

# wait for all jobs to complete
wait

end=`date +%s`
runtime=$((end-start))
echo "total_done with runtime: ${runtime} seconds"
