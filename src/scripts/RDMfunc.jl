module RDMfunc
using DataFrames, DSP, Peaks, Statistics, AbstractFFTs
#
#SOME FUNCTIONS
function th_finder(acceleration,threshold_init,amount,positive_trigger_only) #function to find threshold, so that amount values are above that threshold
    #!!! Implement adaptive step size in reference to maximum accel. 
    #println("finding out threshold")
    threshold = threshold_init
    found = false
    if positive_trigger_only
        high_initial_guess = !(amount<length(tr_finder(acceleration,threshold_init))) # low init guess=too many triggers
        res_min = amount + 2;
        off = 0;
        while !found    
            trigger_count = length(tr_finder(acceleration,threshold))
            res = abs(amount-trigger_count)
            #display("res:")    #for debugging
            #display(res)  
            #display(res_min)
            if res >res_min
                off += 1    
            end
            if off> 20
                throw(DomainError(amount, "amount of triggers can not be obtained from the given dataset"))
            end
            if threshold< 0
                throw(DomainError(amount, "amount of triggers can not be obtained from the given dataset - probably fewer periods that amount of intended Triggerpoints")) 
            end

            if res < res_min 
                res_min = res 
            end
            if (trigger_count < amount)&&(high_initial_guess) #if too few triggers=too high threshold && initial guess is too high: decreasingthresh
                threshold += -0.005
                #display("decreasing")
            elseif (trigger_count > amount) && (!high_initial_guess) #if too many triggers && low initial guess: incereasing threshold
                threshold += 0.005
                #display("increasing")
            elseif (trigger_count > amount)&&(high_initial_guess) # if starting from too high threshold but crossing the amount i.e now too many triggers
                found=true 
                #display("end: from high threshold")
                #display(amount)
                #display(trigger_count)
            elseif (trigger_count < amount) && (!high_initial_guess) #starting from too low threshold, now too crossing amount i.e too few triggers
                threshold+= -0.005 
                found = true
                #display("end : from low threshold")
            elseif trigger_count==amount
                found = true
                #display("amount = trigger number")
            end 
            #display(threshold)
            #display(trigger_count)
        end

    elseif !positive_trigger_only
        high_initial_guess = !(amount<length(tr_finder(acceleration,threshold_init))+length(neg_tr_finder(acceleration,threshold_init))) # low init guess=too many triggers
        while !found    
            trigger_count = length(tr_finder(acceleration,threshold))+length(neg_tr_finder(acceleration,threshold))
            #display("trigger count - (1):pos (2): neg")
            #display(length(tr_finder(acceleration,threshold,starttime,period)))
            #display(length(neg_tr_finder(acceleration,threshold,starttime,period)))


            if threshold< 0         #if amount of triggers can not be obtained, throw error instead of endless loop
                throw(DomainError(amount, "amount of triggers can not be obtained from the given dataset - probably fewer periods that amount of intended Triggerpoints")) 
            end
            if (trigger_count < amount)&&(high_initial_guess) #if too few triggers=too high threshold && initial guess is too high: decreasingthresh
                threshold = threshold -0.005
                #display("decreasing")
            elseif (trigger_count > amount) && (!high_initial_guess) #if too many triggers && low initial guess: incereasing threshold
                threshold = threshold +0.005
                #display("increasing")
            elseif (trigger_count > amount)&&(high_initial_guess) # if starting from too high threshold but crossing the amount i.e now too many triggers
                found=true 
                #display("end: from high threshold")
                #display(amount)
                #display(trigger_count)
            elseif (trigger_count < amount) && (!high_initial_guess) #starting from too low threshold, now too crossing amount i.e too few triggers
                threshold= threshold-0.005 
                found = true
                #display("end : from low threshold")
            elseif trigger_count==amount
                found = true
                #display("amount = trigger number")
            end 
            #display(threshold)
            #display(trigger_count)
        end

    end
    return threshold
end 

function filtering(accelerations,frequency,samplefreq)  #function to initially filter the data, in this case using butterworth bandpass
    ("filtering accelerations ")
    responsetype = Bandpass(frequency*0.8,frequency*1.2; fs=samplefreq)      
    designmethod = Butterworth(4)
    acc_filt= filtfilt(digitalfilter(responsetype, designmethod), accelerations)
    return acc_filt                                     #maybe change type vector to df later
end

function tr_finder(acc,thresh::Float64)         #returns array of locations of trigger points in dataset - triggers are at the vals>threshold at level crossing
    list = zeros(0)                             #intialize the list containing Trigger data
    k = 0::Int64                                #intitialize switch k
    for i in 1:length(acc)   
        if ((acc[i]>thresh) && (k==0))          #appends line of df when (acc exceeds threshold and its the first value exceeding) or (acc_below threshold and its the first value subceeding)
            push!(list,i)
            k=1
        elseif ((acc[i]<thresh) && (k==1)) 
            push!(list,i-1)   #or i ?? 
            k=0
        end
    end
    return round.(Int,list)
end

function neg_tr_finder(acc,thresh::Float64)         #returns array of locations of negative trigger 
    list = zeros(0)                                 #intialize the list containing Trigger data
    k = 0::Int64                                    #intitialize switch k
    for i in 1:length(acc)   #works 
        if ((acc[i]<-thresh) && (k==0))             #appends line of df when (acc exceeds threshold and its the first value exceeding) or (acc_below threshold and its the first value subceeding)
            append!(list,i)
            k=1
            #println(i)
        elseif ((acc[i]>-thresh) && (k==1)) 
            append!(list,i-1)   #or i ?? 
            k=0
        end
    end
    return round.(Int,list)
end


function rdm_alternative(accel,trig,period)     #optimized version of rdm, roughly 10^4 times faster
    list = zeros(Float32, period, 1)
    for i in trig;
        if i+period< length(accel)
            for j in 1:period
                list[j] += accel[i+j]
            end
        end
    end
    list = list./length(trig)
    return list
end


function rdm2_alternative(accel,trig,trig_neg,period)   #faster alternative
    list = zeros(Float32, period, 1)
    for i in trig;
        if i+period< length(accel)
            for j in 1:period
                list[j] += accel[i+j]
            end
        end
    end
    for i in trig_neg;
        if i+period< length(accel)
            for j in 1:period
                list[j] -= accel[i+j]
            end
        end
    end
    list = list./(length(trig)+length(trig_neg))
    return list
end

function localmaxima(list)  #returns list of indexes, where local min and max are located, can be refined to include boundaries
    min_list=[]
    max_list=[]
    for i in 1:length(list)
        if i==1 
            if list[i]>list[i+1]
                append!(max_list,i)
            elseif list[i]<list[i+1]
                append!(min_list,i)
            end
        elseif i==length(list)
            #print("end of list")
        else
            if list[i]>list[i-1] && list[i]>list[i+1]
                append!(max_list,i)
            elseif list[i]<list[i-1] && list[i]<list[i+1]
                append!(min_list,i)
            end    
        end
    end
    return max_list     #CURRENTLY ONLY RETURNING MAX_LIST
end

function fullrdm(acc,period_steps,threshold_steps,threshold,positive_trigger_only)
    if positive_trigger_only
        results =zeros(0,length(period_steps)+3) # = function (params ) 
        for i in threshold_steps            #loop through steps in threshold to  find Damping
            #FIND TRIGGERPOINTS

            current_threshold= threshold*i                          #calculates threshold to be used in current iteration
            trigger =tr_finder(acc,current_threshold)               #store triggerpoints in list #builds matrix containing all datasets starting at trigger
            #display(length(trigger))
            resultrow = []                                          #creating arrays with valuable information where the dampening values will be added later
            push!(resultrow, i, current_threshold, length(trigger))   
            for j in period_steps
                M_mean = rdm_alternative(acc,trigger,j)    #builds matrix containing all datasets starting at trigger and average the sets to obtain RD-Signature - 
                max_list= localmaxima(M_mean[:,1])      #lists containing the positions in time of maximum values
                #display(i)
                #display(j)
                logarithmic_decrement=(1/(length(max_list)-1))*log(M_mean[max_list[1,1],1] / M_mean[last(max_list),1]) #calculating between first and last peak in period length
                damping_ratio = logarithmic_decrement/(2*pi)
                push!(resultrow,damping_ratio)
            end
            results = vcat(results,resultrow')   #concatenating resultrows to the result matrix
        end 
    elseif !positive_trigger_only
        results =zeros(0,length(period_steps)+3) # = function (params ) 
            for i in threshold_steps                                            #loop through steps in threshold to  find Damping
                #FIND TRIGGERPOINTS
                current_threshold= threshold*i                                  #calculates threshold to be used in current iteration
                trigger =       tr_finder(acc,current_threshold)                #store triggerpoints in list 
                neg_trigger =   neg_tr_finder(acc,current_threshold)
                resultrow = []                                                  #creating arrays with valuable information where the dampening values will be added later
                push!(resultrow, i, current_threshold, length(trigger)+length(neg_trigger))   
                for j in period_steps
                    M_mean = rdm2_alternative(acc,trigger,neg_trigger,j)        #builds matrix containing all datasets starting at trigger                                              #average the sets to obtain RD-Signature
                    #CALC LOG DEC
                    max_list= localmaxima(M_mean[:,1])                          #lists containing the positions in time of maximum values
    
                    logarithmic_decrement=(1/(length(max_list)-1))*log(M_mean[max_list[1,1],1] / M_mean[last(max_list),1]) #calculating between first and last peak in period length
                    damping_ratio = logarithmic_decrement/(2*pi)
                    push!(resultrow,damping_ratio)
                end
                results = vcat(results,resultrow')                              #concatenating resultrows to the result matrix
            end 
    end
    return results
end


# OUTDATED FUNCTIONS 

function rdm(accel,trig,period) #OUTDATED : slow version, using matrices
    #println("RDM: calc free decay response")
    Mat= reshape([],period,0) #creates list with length of the datapoints contained in period
    #display("looping through triggerpoints")
    for i in trig;                   #loops through the trigger points and appends column for every sample
        if i+period < length(accel) #statement takes end of sample data into account
            col= accel[i:i+period-1]    #-1 for 1-indexing
            Mat = cat(Mat, col, dims=2) #appends column
        end
    end
    #println("FDR calculated")
    #display(Mat)
    M_mean = mean(Mat,dims=2)
    return M_mean
end

function rdm2(accel,trig,trig_neg,period)   #OUTDATED    #building matrix containining time sequences of data using positive and negative triggers
    #println("RDM: calc free decay response")
    Mat= reshape([],period,0) #creates list with length of the datapoints contained in period
    #display("looping through triggerpoints")
    for i in trig;                   #loops through the trigger points and appends column for every sample
        if i+period < length(accel) #statement takes end of sample data into account
            col= accel[i:i+period-1]    #-1 for 1-indexing
            Mat = cat(Mat, col, dims=2) #appends column
        end
    end
    for i in trig_neg
        if i+period < length(accel) #statement takes end of sample data into account
            col= (-1).*accel[i:i+period-1]    #-1 for 1-indexing, negating values
            Mat = cat(Mat, col, dims=2) #appends column
        end
    end
    #println("FDR calculated")
    M_mean = mean(Mat,dims=2)
    return M_mean
end

function freq_an(acc,fs)
    fft_signal = abs.(fft(acc))
    freqs = DSP.fftfreq(length(acc),fs)
    max_pos= findmax(fft_signal)
    return(abs(freqs[max_pos[2]]))
end


export th_finder, tr_finder, neg_tr_finder, filtering1, rdm, logdec, rdm_alternative, freq_an
end 