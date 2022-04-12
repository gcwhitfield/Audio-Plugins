import numpy as np
from scipy.io import wavfile 
import scipy.signal
from matplotlib import pyplot as plt
import math
import random
from helpers import *

# import filters designed by MATLAB's filterDesigner tool
from filters.lowpass import *
from filters.bandpass import *
from filters.highpass import *

# evaluates a cubic spline at a time t
# precondition: 0 <= t <= 1
def cubic_unit_spline(t):
    if t < 0:
        return 0
    elif t > 1:
        return 1
    else:
        # evaluate the hermite basis functions
        h_00 = 2*pow(t, 3) - 3*pow(t, 2) + 1
        h_10 = pow(t, 3) - 2*pow(t, 2) + t
        h_01 = -2*pow(t, 3) + 3*pow(t, 2)
        h_11 = pow(t, 3) - pow(t, 2)
        p_0 = np.array([0, 0]) # position 0
        p_1 = np.array([1, 1]) # position 1
        m_0 = np.array([1, 0]) # tangent 0
        m_1 = np.array([-1, 0]) # tangent 1
        return (h_00*p_0 + h_10*m_0 + h_01*p_1 + h_11*m_1)[1]

RATIO_HIGH = 1/2
RATIO_LOW = 2
ATTACK = 400 # milliseconds
RELEASE = 1000 # milliseconds
THRESHOLD_HIGH = 0.5
THRESHOLD_LOW = 0.05

def process_compressor(samp_rate, audio):
    # read the audio file
    # samp_rate, audio = wavfile.read("drums.wav")
    # audio = np.average(audio, 1)

    # test with sin function
    # samp_rate = 100
    # audio = np.sin(np.arange(0, 1, 0.01) * 10)
    # audio += 0.2 * np.sin(np.arange(0, 1, 0.01) * 5)
    original_audio = np.copy(audio)

    
    # ---------- downwards compression ----------
    # audio = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    _attack = int((ATTACK * samp_rate) / 1000) # samples
    _release = int((RELEASE * samp_rate) / 1000) # samples

    # test cubic interpolation function
    # x = np.arange(0, 1, 0.01)
    # interpolation_vectorize = np.vectorize(cubic_unit_spline)
    # y = interpolation_vectorize(x)
    # plt.stem(x, y)
    # plt.title("Cubic unit spline")
    # plt.show()

    # save vector of data points to create scatterplot
    drys = np.zeros(audio.shape[0])
    wets = np.zeros(audio.shape[0])

    m = 0 # the "stength" of the compressor plugin. The attack and release parameters control m
    # apply compressor algorithm
    for i in np.arange(audio.shape[0]):
        dry = audio[i]
        wet = audio[i]
        sign = 1
        if dry < 0:
            sign = -1
        if (abs(dry) > THRESHOLD_HIGH):
            if _attack > 0:
                m += (1/_attack)
                if m > 1: 
                    m = 1
            else:
                m = 1
            wet = RATIO_HIGH * (dry - THRESHOLD_HIGH*sign) + THRESHOLD_HIGH*sign
        else:
            if _release > 0:
                m -= (1/_release)
                if m < 0:
                    m = 0
            else:
                m = 0
        
        interp = cubic_unit_spline(m) # smoothly interpolate the release and attack effect
        audio[i] = interp*wet + (1 - interp)*dry
        drys[i] = dry
        wets[i] = wet

    plt.scatter(drys, wets)
    plt.title("Scatterlpot of downwards compressor")
    plt.show()
    

    # ---------- upwards compression ----------
    m = 0 #
    # apply compressor algorithm
    for i in np.arange(audio.shape[0]):
        dry = audio[i]
        wet = audio[i]
        sign = 1
        if dry < 0:
            sign = -1
        if (abs(dry) < THRESHOLD_LOW):
            if _attack > 0:
                m += (1/_attack)
                if m > 1: 
                    m = 1
            else:
                m = 1
            # wet = (RATIO_LOW) * (dry - THRESHOLD_LOW*sign) + THRESHOLD_LOW*sign
            wet = (abs(dry - THRESHOLD_LOW*sign)*(1.0 - (1/RATIO_LOW))*sign + dry)
        else:
            if _release > 0:
                m -= (1/_release)
                if m < 0:
                    m = 0
            else:
                m = 0
        
        
        interp = cubic_unit_spline(m) # smoothly interpolate the release and attack effect
        audio[i] = interp*wet + (1 - interp)*dry
        drys[i] = dry
        wets[i] = wet

    plt.scatter(drys, wets)
    plt.title("Scatterlpot of upwards compressor")
    plt.show()
    return audio