#!/bin/bash


function usage_extrac_gps () {
    cat <<EOL

extract_gps.sh INPUT_DIRECTORY OUTPUT_DIRECTORY OUTPUT_FILE_SUFFIX

Shell script to extact gps data from tower oscillation measurements.
Only unique gps locations are written out. Due to the measurement technique, 
large gaps between consecutive gps locks may appear

INPUT_DIRECTORY:    Directory containing the raw tom data
OUTPUT_DIRECTORY:   The output directory were the gps tracks will be written to
OUTPUT_FILE_SUFFIX: string that will be appended to the input file name

EOL
    exit
}

### Main logic 

if ! [ -z $1 ] && [ -d $1 ]
then
    tom_dir=$1
else
    echo "please provide a valid input directory"
    usage_extrac_gps
fi

if ! [ -z $2 ] && [ -d $2 ]
then
    output_dir=$2
else
    echo "please provide a valid output directory"
    usage_extrac_gps
fi

if ! [ -z $3 ]
then
    output_suffix=$3
else
    echo "Warning: no output prefix provided, falling back to 'gps_'"
    output_suffix='gps'
fi

# extract description string from tom data file
description_string=$(
ls $tom_dir |       # list all tom data files
head -n 1 |         # take the first one
rev |               # reverse it
cut -d '/' -f1 |    # remove everything exept the file name
rev |               # reverse back
cut -d '.' -f1 |    # remove the file ending
cut -d '_' -f1-3    # keep the first three fields: turbine, measurement position)
)

# print all availale files and extract gps tracks

find $tom_dir -type f -iname "*.csv" | # use find to generate a list of files
parallel extract_gps_from_file.sh {} $output_dir $output_suffix

# concatenate all newly generated gps tracks into one record
cat ${output_dir}/*${output_suffix}.csv |
sort -k 1 -n > ${output_dir}/${description_string}_${output_suffix}.csv

#### Footnotes
# [1]:    to obfuscate the postions of individuals turbines, a constant offset was substracted
#         from all measurements.

