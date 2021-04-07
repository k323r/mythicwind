#!/bin/bash

if [ -f "$1" ] ; then
        in_file="$1"
else
        echo 'please provide a input file'
        exit
fi

target_file=$(echo "$in_file" | cut -d ' ' -f 1).csv

mv "$in_file" "$target_file"



