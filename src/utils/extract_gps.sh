#!/bin/bash

SOURCE_DIR=$1
TARGET_DIR=$2
OUTFILE_PREFIX="gps"

for file in $(ls ${SOURCE_DIR}/*.csv ) ; do
    echo $file
    # isolate date and index from the input file
    infile_name=$(echo $file | rev | cut -d '/' -f1 | rev | cut -d '.' -f1 | cut -d '_' -f2-)

    echo $infile_name

    outfile_path="${TARGET_DIR}/${OUTFILE_PREFIX}_${infile_name}.csv"
    echo $outfile_path

    cat $file |              # print each file to stdout
    tail -n +2 |             # skip the first two lines
    cut -d ' ' -f 1,3-5 |    # select epoch [2] and gps data [5-7]
    uniq -u > $outfile_path  # reduce to only unique time stamps and write out

done


