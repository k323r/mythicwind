#!/bin/bash

function usage_integrate_turbine () {
    echo <<EOL

integrate_turbine.sh TURBINE_DIRECTORY

integrate_turbine.sh iterates over available positions in a given turbine directory,
selects non-empty folders and calls postprocess_tomdata.py

EOL
    exit
}

if ! [ -z $1 ] && [ -d $1 ]
then
    turbine_dir=$1
else
    echo "please provide a valid input directory"
    usage_integrate_turbine
fi

for position_dir in ${turbine_dir}/*/tom/clean
do
    position_name=$(echo $position_dir | rev | cut -d '/' -f3 | rev)
    echo -n "parsing ${position_name} "

    if ! [[ -z $(ls $position_dir) ]]
    then
        echo "-> found $(ls $position_dir | wc -l) files. "

        target_dir="${turbine_dir}/${position_name}/tom/acc-vel-pos"

        # check if the output directory exists
        if ! [[ -d $target_dir ]]
        then
            echo "    could not find a valid output directory.. skipping"
            continue
        fi

        # remove any old files in the taget directory
        if ! [[ -z $(ls ${target_dir}) ]]
        then
            rm ${target_dir}/*
        fi

        echo "    exporting data to ${target_dir}"

        postprocess_tomdata.py --input ${position_dir} --output ${target_dir} --substract-mean

        echo ""

    else
        echo ""
    fi
done