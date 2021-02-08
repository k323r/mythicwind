#!/bin/bash

PWD=$(pwd)
TURBINE=$1

echo "creating directory tree for ${TURBINE}"

for MEASUREMENT in helihoist-1 helihoist-2 sbitroot sbittip towertop towertransfer tp damper
do
    mkdir -p "${TURBINE}/${MEASUREMENT}/tom/clean"
    mkdir -p "${TURBINE}/${MEASUREMENT}/msr/clean"
    mkdir -p "${TURBINE}/${MEASUREMENT}/tom/processed"
    mkdir -p "${TURBINE}/${MEASUREMENT}/msr/processed"
done
