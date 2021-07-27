using DataFrames
using CSV
using Plots
using DSP
using Statistics
using Interpolations
using FFTW
using AbstractFFTs
include("RDMfunc.jl")
plotly()     

#PARAMETERS
#const file="/home/san/Projekte/mythicwind/src/scripts/50y20degot.csv"                                        #File containing Data

const file="/home/san/Projekte/mythicwind/src/scripts/test.csv"
#const file="/home/san/Projekte/mythicwind/src/scripts/test2.csv"

const samplefreq =          5;                                     #sample frequency in Hz that should be achieved/resampled   
#const threshold_initx =     0.2                                   #initial guess threshold, can be adapted by the th_finder function
#const threshold_inity =     0.23
threshold_steps =           collect(0.9:-0.1:0.1)                #Threshold steps that should be considered
period_steps =              samplefreq.*collect(20:10:100)          #Number of samples as a function of sample frequency N * samplefreq, N = [10:1:100] 
#const min_trigger_number =  200;                                  #minimum Trigger number when using the auto threshold
const positive_trigger_only =     true;                            #allows negative Triggerpoints, roughly doubling the amount of triggers
#freqx=                0.176   #function written to obtain these
#freqy=                0.12    #

println("Start new calculation:")
#READ DATA and assign readable names to the input data                                           
#df = CSV.File(file,delim=";")                       #read input data
df = CSV.File(file,delim=",")
time = df.epoch                                                                  
accx = df.pos_x                                     #type: array{float64}
accy = df.pos_z                                      


#Direction1 : X
#PREPROCESS
df_t = collect(0 : 1/samplefreq : last(time)-time[1])                                       #yields array containing time in s (converting unix timestamp to sec since start)
                                                                                            #time index from 0 to end of signal

polx =LinearInterpolation(time, accx).(first(time):1/samplefreq:last(time))                 #Resample to samplefrequency  
freqx = RDMfunc.freq_an(polx,samplefreq)                                                    #find first mode frequency for filtering
filt_accx = RDMfunc.filtering(polx,freqx,samplefreq)                                        #Filttering 
#RDM
thresholdx = maximum(filt_accx)
resultsx = RDMfunc.fullrdm(filt_accx,period_steps,threshold_steps,thresholdx,positive_trigger_only)

# aus der full rdm kommt eine datenstruktur mit den fertigen paramtern raus. 4 enthaelt die daempfungsparamter

x_damp = resultsx[:,4:length(period_steps)+3]'                                                          #yield Damping values from results matrix
x_damp_converted = convert(Array{Float64}, x_damp)                                                      #Change Type, so that it is readable for plotly
#s1 = plot(period_steps,x_damp_converted,title = "Damping Ratio - X",xlabel = "Tau",ylabel="Damping")    #Plot Results - X 
s1alt = plot(threshold_steps',x_damp_converted',title = "Damping Ratio - X",xlabel = "Threshold",ylabel="Damping")    #Plot Results - X 

#Direction2 : Y
#PREPROCESS
poly =LinearInterpolation(time, accy).(first(time):1/samplefreq:last(time))                 #Resample to samplefrequency 
freqy = RDMfunc.freq_an(poly,samplefreq)
filt_accy = RDMfunc.filtering(poly,freqy,samplefreq)                                        #Filtering   
#RDM
thresholdy = maximum(filt_accy)
resultsy = RDMfunc.fullrdm(filt_accy,period_steps,threshold_steps,thresholdy,positive_trigger_only)
y_damp = resultsy[:,4:length(period_steps)+3]' 
y_damp_converted = convert(Array{Float64}, y_damp)                                                      #Change Type, so that it is readable for plotly
#s2 = plot(period_steps,y_damp_converted,title = "Damping Ratio - X",xlabel = "Tau",ylabel="Damping")    #Plot Results - Y
#s2alt = plot(threshold_steps,y_damp_converted',title ="Damping Ratio- Y",xlabel="Threshold",ylabel="Damping" )
#PLOT
#display(plot(s1,s2,size =[900,400]))
#display(plot(s1alt,s2alt,size =[900,400]))
#display(x_damp_converted)
#display(s1alt)
#savefig(s1,"plot_x.png")
#display(x_damp_converted')
xconv2 =x_damp_converted'
yconv2 =y_damp_converted'
#display(threshold_steps)
mean_xdamps = mean(xconv2,dims=2)
mean_ydamps = mean(yconv2,dims=2)

p1 = (
    plot(threshold_steps, xconv2);
    scatter!(threshold_steps, mean_xdamps, ylims=[0,0.01]);
    plot!(threshold_steps, yconv2);
    scatter!(threshold_steps, mean_ydamps);
)

display(p1)

scatter(threshold_steps, mean_xdamps)
scatter!(threshold_steps, mean_ydamps)

println(mean(mean_ydamps))
println(mean(mean_xdamps))