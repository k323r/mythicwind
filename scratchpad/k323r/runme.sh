jobnumber=0     # job number incrementor to keep track of the number of jobs run
maxjobs=4       # number of max. parallel jobs
njobs=1         # number of currently running jobs


# dummy job
function runme () {
    global $jobnumber
    global $njobs

    jobnumber=$(echo $jobnumber + 1 | bc)
    echo "inside runme: running job ${jobnumber}"
    
    # the 'job'
    sleep 3
    
    # when the job is done, substract one from the current number of running jobs
    # and return
    njobs=$(echo $njobs - 1 | bc)
    return 0
}

while [[ $jobnumer -le 10 ]]
do
    echo "$i"
    if [[ $njobs -lt $maxjobs ]]
    then
        njobs=$(echo $njobs + 1 | bc)
        runme &
    else
        echo "currently at jobnumber ${jobnumber}"
        sleep 1
    fi
done


