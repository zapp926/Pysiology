import peakutils #peak detection for IBI / BPM
import numpy as np #to handle datas
import math #to handle mathematical stuff (example power of 2)
from scipy.signal import butter, lfilter  #for signal filtering

def getIBI(peaks,samplerate):
    """ This function returns the IBI of a discrete heart signal
        Input: peaks of the ECG signal
        Output: IBI in ms
    """ 
    delta = []
    for peakIndex in range(1,len(peaks)):
        delta.append(((peaks[peakIndex] - peaks[peakIndex - 1]) / samplerate) * 1000)
    IBI = np.mean(delta) 
    return(IBI)
    
def getBPM(npeaks,nsample, samplerate):
    """ This function returns the IBI of a discrete heart signal
        
        Input: number of peaks of the ECG signal,number of samples, samplerate of the signal
        Output: PBM
    """ 
    samplelen = nsample / samplerate #lenght in seconds
    BPM = (npeaks * 60) / samplelen
    return(BPM)
    
def getSDNN(peaks,samplerate):
    """ This functions evaluate the standard deviation of intervals between heartbeats
        SDNN = sqrt((1/N-1) * sum(i=1 --> N)(rri - rrmean)^2
        
        Input: peaks of the ECG signal,samplerate of the signal
        Output: standard deviations of Intervals between heartbeats
    """
    delta = []
    for peakIndex in range(1,len(peaks)):
        delta.append(((peaks[peakIndex] - peaks[peakIndex - 1]) / samplerate) * 1000)
    SDNN = np.std(delta)
    return(SDNN)
    
def getSDSD(peaks,samplerate):
    """ This functions evaluate the the standard deviation of successive differences between adjacent R-R intervals
        SDSD: sqrt((1 / (N - 1)) * sum(i=1 --> N)(RR i - mean(RR))**2)
        
        Input: peaks of the ECG signal,samplerate of the signal
        Output: the standard deviation of successive differences between adjacent R-R intervals:
    """
    delta = []
    for peakIndex in range(1,len(peaks)):
        delta.append(((peaks[peakIndex] - peaks[peakIndex - 1]) / samplerate) * 1000)
    
    differences = [] 
    for i in range(1,len(delta)):
        differences.append(delta[i] - delta[i-1])
        
    SDSD = np.std(differences)
    return(SDSD)
    
def getRMSSD(peaks,samplerate):
    """ This functions evaluate the root mean square of successive differences between adjacent R-R intervals
        RMSSD = sqrt((1 / (N - 1)) * sum(i=1 --> N)(RRdiff i - mean(RRdiff))**2)
        
        Input: peaks of the ECG signal,samplerate of the signal
        Output: the root mean square of successive differences between adjacent R-R intervals
    """
    delta = []
    for peakIndex in range(1,len(peaks)):
        delta.append(((peaks[peakIndex] - peaks[peakIndex - 1]) / samplerate) * 1000)
    
    differences = [] 
    for i in range(1,len(delta)):
        differences.append(math.pow(delta[i] - delta[i-1],2))
        
    RMSSD = np.std(differences)
    return(RMSSD)
    
def getPNN50(peaks,samplerate):
    """ This functions evaluate pNN20, the proportion of differences greater than 50ms.
        
        Input: peaks of the ECG signal,samplerate of the signal
        Output: the root mean square of successive differences between adjacent R-R intervals
    """
    delta = []
    for peakIndex in range(1,len(peaks)):
        delta.append(((peaks[peakIndex] - peaks[peakIndex - 1]) / samplerate) * 1000)
    
    differences = [] 
    for i in range(1,len(delta)):
        differences.append(delta[i] - delta[i-1])
        
    NN50 = [x for x in differences if x > 50]
    pNN50 = float(len(NN50)) / float(len(differences))
    return(pNN50)
    
def getPNN20(peaks,samplerate):
    """ This functions evaluate pNN20, the proportion of differences greater than 50ms.
        
        Input: peaks of the ECG signal,samplerate of the signal
        Output: the root mean square of successive differences between adjacent R-R intervals
    """
    delta = []
    for peakIndex in range(1,len(peaks)):
        delta.append(((peaks[peakIndex] - peaks[peakIndex - 1]) / samplerate) * 1000)
    
    differences = [] 
    for i in range(1,len(delta)):
        differences.append(delta[i] - delta[i-1])
        
    NN20 = [x for x in differences if x > 20]
    pNN20 = float(len(NN20)) / float(len(differences))
    return(pNN20)
 
#Define the filters
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs #Nyquist frequeny is half the sampling frequency
    normal_cutoff = cutoff / nyq 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return(b, a)
    
def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs #Nyquist frequeny is half the sampling frequency
    normal_cutoff = cutoff / nyq 
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return(b, a)
    
def butter_lowpass_filter(data, cutoff, fs, order):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return(y)
    
def butter_highpass_filter(data, cutoff, fs, order):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return(y)
    
#http://www.paulvangent.com/2016/03/15/analyzing-a-discrete-heart-rate-signal-using-python-part-1/
def analyzeECG(rawECGSignal,samplerate,highpass = 0.5, lowpass=2.5 ibi=True,bpm=True,sdnn = True,sdsd = True, rmssd = True,pnn50 = True, pnn20 = True):
    """ This function analyze a discreate heart rate signal
        Input: 
            rawECGSignal = ecg signal as list
            samplerate = sample rate of the signal
            
        Output: BPM
    """ 
    #First we get the peaks
    filteredECGSignal = butter_lowpass_filter(rawECGSignal, lowpass, samplerate, 5)#filter the signal with a cutoff at 2.5Hz and a 5th order Butterworth filter
    filteredECGSignal = butter_highpass_filter(filteredECGSignal, highpass, samplerate, 5)#filter the signal with a cutoff at 2.5Hz and a 5th order Butterworth filter
    min_dist = int(samplerate / 2) #Minimum distance between peaks is set to be 500ms
    peaks = peakutils.indexes(filteredECGSignal,min_dist=min_dist)
    resultsdict = {}
    if(ibi):
        resultsdict["ibi"] =  getIBI(peaks,samplerate)
    if(bpm):
        resultsdict["bpm"] =  getBPM(len(peaks),len(rawECGSignal),samplerate)
    if(sdnn):
        resultsdict["sdnn"] =  getSDNN(peaks,samplerate)
    if(sdsd):
        resultsdict["sdsd"] =  getSDSD(peaks,samplerate)
    if(rmssd):
        resultsdict["rmssd"] =  getRMSSD(peaks,samplerate)
    if(pnn50):
        resultsdict["pnn50"] =  getPNN50(peaks,samplerate)
    if(pnn20):
        resultsdict["pnn20"] =  getPNN20(peaks,samplerate)
    if(pnn50 and pnn20):
        resultsdict["pnn50pnn20"] = resultsdict["pnn50"] / resultsdict["pnn20"]
    return resultsdict

###############################################################################
#                                                                             #
#                                  DEBUG                                      #
#                                                                             #
###############################################################################
""" For debug purposes"""

if(__name__=='__main__'):
    pass