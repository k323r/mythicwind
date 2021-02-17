#!/bin/bash

if [ -f $1 ]
then
    input_file=$1
else
    echo "Please provide a valid input file" 
    exit
fi

temp_file=$(mktemp)

cat $input_file |
tr ' ' ',' |
sed -e "s/,,/,/g" |
sed -e "s/#,//g" |
sed -e "s/#//g" |
sed -e "s/'//g" > $temp_file 

mv $temp_file $input_file
