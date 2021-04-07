#!/bin/bash

if [ -d $1 ] ; then
    input_dir=$1
else
    echo "please provide a valid input directory"
    exit
fi

if ! [ -z $2 ] ; then
    output_file=$2
else
    echo "please provide an output file!"
    exit
fi

echo "start,stop,filepath" > $output_file

for f in $(find $input_dir -iname "*acc-vel-pos*.csv" | sort) ; do
    start=$(echo $f | cut -d '_' -f 5)
    end=$(echo $f | cut -d '_' -f 6 | cut -d '.' -f 1)
    echo "$start,$end,$f" >> $output_file
done

