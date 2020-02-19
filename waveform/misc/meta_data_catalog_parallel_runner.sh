#! /bin/bash
# https://stackoverflow.com/questions/6593531/running-a-limited-number-of-child-processes-in-parallel-in-bash
# for p in `ps aux | grep wc | grep -v grep | awk '{print $2}'`; do kill -9 $p; done

#input_path="/opt/genomics/WaveFormProcessedFiles"
input_path="/opt/genomics/WaveFormProcessedFiles/codes/edwards_one_month_test"

output_path="/opt/genomics/WaveFormProcessedFiles/codes/edwards_one_month_output"

code_path="/opt/genomics/WaveFormProcessedFiles/codes/waveform"

index=0
max_jobs=2 # the total number of jobs should NOT be less than max_jobs-1, if you have a single job, max_jobs=2, otherwise, the run will hang forever.
# lapgnomap15 and lapgnomap16 each has 8 vcores.

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

todo_array=($(find $input_path -name "CLIN_ENG_WMOR*-*" -type d))
#todo_array=($(find $input_path -name "CLIN_ENG_WCATHL*-*" -type d))

function do_job {
    echo "starting job $1"

    cd $code_path

    op1=`basename ${todo_array[$index]}`
    op2="$output_path/${op1}.txt"
    echo $op2
    python ./misc/meta_data_catalog.py -input_dir "${todo_array[$index]}" -output_file $op2

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
