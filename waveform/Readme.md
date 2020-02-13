# Author
Yu Pan (yupan@mednet.ucla.edu)

# License
[MIT](https://choosealicense.com/licenses/mit/)

# Repo Modules

\_\_main\_\_.py is the entrance code, where a job can be created.  
Currently, there are 2 job_types:
- toCsv: this converts adibin/vitalbin/xml to csvs
- deidXml: this simply deidentifies xml

## * The folder "shellscript" contains helper shell scripts.  
- check_if_xml_truncated.sh checks if the xmls from Vivek are truncated.    
- parallel_runner.sh runs the code in parallel, refer to "parallel computing in linux vm " in this doc.  
- create_waveform_catalog.sh creates a catalog for adibin.csv files.  

## * The folder "config" contain configuration file, which can configure things, like logging level.  

## * The folder "tests" contains unit tests.

## * The folder "deidentify" contains 
- the extract_data.sql extracts data from Ankur's table 
- the deidentify.csv contains the extracted data.
- the deidentifier.py defines:
    -- how to create a dictionary from deidentify.csv.
    -- the functions to generate event sequence. 
- the deidentify_xml.py deidentifies xml by removing UTC and replace date with event sequence.

## * The folder "to_csv" contains
### 0. single_file_processor.py 
This defines SingleFilePorcessor, which contains methods to create dataframes and write dataframes to csv.

The following three scripts each defines a child class of SingleFilePorcessor 
and implements the abstract method "create_dataframe".

### 1. processor_adibin.py: Convert waveforms records from adibin to csv
The code uses https://github.com/hulab-ucsf/binfilepy to read adibin.

### 2. processor_vitalbin.py: Convert vitals records from vitalbin to csv
The code uses https://github.com/hulab-ucsf/vitalfilepy to read vitalbin.

### 3. processor_xml.py: Convert alarms records from xml to csv
The code can convert waveforms/vitals/alarms to csv,  
but we only convert alarms since waveforms and vitals are converted from binary files.  



# How to setup Linux VM and run the code there   
## 1. ssh-gen rsa keys, setup .ssh/authorized_keys, this enable ssh wo password and scp.  

## 2. scp codes to vm. The codes are not very mature yet and probably need changes.   
That is why I don't want to update every change through PyPI.  

## 3. ask Vivek to install anaconda, pip, screen.  
 
## 4. create a conda env, libraries are only allowed to be installed in conda env in the T1 VMs  
conda create -n edwards -y Python=3.7  
conda init bash  
conda activate edwards  
Make sure you get the latest version (0.1.7 or above), which fixed a bug in the reader.
You can just install the dependencies by 
```bash
pip install -r requirements.txt # This has to be done in a new conda env, because I don't have permission to change existing installed libraries.  
```

## 5. call the code as below  
To test on my mac
python \_\_main\_\_.py \  
-input "/Users/yp/Google Drive/think for mac/ucla_health/test_data/input/WaveFormProcessedFiles" -output "/Users/yp/Google Drive/think for mac/ucla_health/test_data/output" -type "toCsv" -bp "/Users/yp/Google Drive/think for mac/ucla_health/binfilepy_git"

python \_\_main\_\_.py \  
-input "/Users/yp/Downloads/wftools/5xmls/single_in" -output "/Users/yp/Downloads/wftools/5xmls/single_out"  -type "deidXml"

To test on lapgnomap15  
python __main__.py -input "/home2/yup1/WaveFormProcessedFiles/CLIN_ENG_WMOR8/CLIN_ENG_WMOR8-1563486442/ADIBIN" -output "/opt/genomics/WaveFormProcessedFiles/CsvOutputs" -type "toCsv" -bp "/home2/yup1/binfilepy_git"  
python __main__.py -input "/home2/yup1/WaveFormProcessedFiles/CLIN_ENG_WMOR8/CLIN_ENG_WMOR8-1563486442/XML" -output "/opt/genomics/WaveFormProcessedFiles/CsvOutputs" -type "deidXml"   

## 6. parallel computing in linux vm  
ssh yup1@lapgnomap15  
conda activate edwards  
cd waveform  
./shellscript/parallel_runner.sh  

## 7. generate data catalog for the output adibin.csv files.  
./shellscript/create_waveform_catalog.sh /home2/yup1/CsvOutputs $(pwd)/waveform_catalog.txt


