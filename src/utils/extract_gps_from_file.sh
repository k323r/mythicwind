#!/bin/bash


function usage_extract_gps_from_file () {
    cat <<EOL

extract_gps_from_file INPUT_FILE OUTPUT_DIRECTORY OUTPUT_FILE_PREFIX

Bash function that accepts a single tom data file as input,
generates an output file name, extracts the gps track and 
writes the gps track out to the output file. 

INPUT_FILE:         Single tom data files
OUTPUT_DIRECTORY:   Directory to write the gps tracks to
OUTPUT_FILE_SUFFIX: string to be appended to the output gps track file

EOL

exit
}

if ! [ -z $1 ] && [ -f $1 ]
then
    tom_file=$1
else
    echo 'please provide a input file'
    usage_extract_gps_from_file
fi

if ! [ -z $2 ] && [ -d $2 ]
then
    output_dir=$2
else
    echo 'please provide an output file path'
    usage_extract_gps_from_file

fi

if ! [ -z $3 ]
then
    output_suffix=$3
else
    echo "please provide a valid output suffix"
    usage_extract_gps_from_file
fi

tom_file_name=$(
    echo $tom_file |    # print file path
    rev |               # reverse order, such that the file is now the first substring
    cut -d '/' -f1 |    # remove the path
    rev |               # reverse again 
    cut -d '.' -f1      # remove the file ending
)

output_file_name=$(echo $tom_file_name | sed -e "s/clean/${output_suffix}/")

output_file_path="${output_dir}/${output_file_name}.csv"

echo "epoch,latitude,longitude,altitude" > $output_file_path

cat $tom_file | # find returns full paths... 
tail -n +2 |             # skip the first two lines
cut -d ',' -f 1,3-5 |    # select epoch [2] and gps data [5-7]
awk -F, '$2 != -54.000 && $3 != -6.500' | # drop lines where no gps data is available [0]
sed -e 's/,/ /g' | # change the delimiter to space
uniq -f 1 |         # return only uniq fields, ignoring the first column
sed -e 's/ /,/g' >> $output_file_path  # change the delimiter back to a comma
