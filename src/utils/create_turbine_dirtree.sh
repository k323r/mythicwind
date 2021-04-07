#!/bin/bash

PWD=$(pwd)

# create a dir tree for storing turbine data

if [ -z $1] ; then
    echo "please provide a turbine id"
    exit
else
    TURBINE=$1
fi

echo "creating directory tree for ${TURBINE}"

for MEASUREMENT in helihoist-1 helihoist-2 sbitroot sbittip towertop towertransfer tp damper
do
    mkdir -p "${TURBINE}/${MEASUREMENT}/tom/clean"
    mkdir -p "${TURBINE}/${MEASUREMENT}/msr/clean"
    mkdir -p "${TURBINE}/${MEASUREMENT}/tom/processed"
    mkdir -p "${TURBINE}/${MEASUREMENT}/msr/processed"
done
