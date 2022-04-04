import numpy as np
from scipy.io import wavfile 
import scipy.signal
from matplotlib import pyplot as plt
import math
import random
from helpers import *

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


def main():
    # read the audio file
    # samp_rate, audio = wavfile.read("drums.wav")
    # audio = np.average(audio, 1)

    # test with sin function
    samp_rate = 100
    audio = np.sin(np.arange(0, 1, 0.01) * 10)
    audio += 0.2 * np.sin(np.arange(0, 1, 0.01) * 5)
    original_audio = np.copy(audio)

    # audio = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    RATIO = 1/25
    ATTACK = 100 # milliseconds
    RELEASE = 100 # milliseconds
    THRESHOLD = 0.5
    _attack = int((ATTACK * samp_rate) / 1000) # samples
    _release = int((RELEASE * samp_rate) / 1000) # samples

    # test cubic interpolation function
    x = np.arange(0, 1, 0.01)
    interpolation_vectorize = np.vectorize(cubic_unit_spline)
    y = interpolation_vectorize(x)
    plt.stem(x, y)
    plt.title("Cubic unit spline")
    plt.show()

    m = 0 # the "stength" of the compressor plugin. The attack and release parameters control m
    # step 1) apply compressor algorithm
    for i in np.arange(audio.shape[0]):
        dry = audio[i]
        wet = audio[i]
        if (dry > THRESHOLD):
            if _attack > 0:
                m += (1/_attack)
                if m > 1: 
                    m = 1
            else:
                m = 1
            wet = RATIO * (dry - THRESHOLD) + THRESHOLD
            # print("above threshold: " + str(i) + " : " + str(dry) + " : " + str(wet))

        else:
            if _release > 0:
                m -= (1/_release)
                if m < 0:
                    m = 0
            else:
                m = 0
        
        interp = cubic_unit_spline(m) # smoothly interpolate the release and attack effect
        print(interp)
        audio[i] = interp*wet + (1 - interp)*dry


    plt.plot(np.arange(audio.shape[0]), audio)
    plt.title("Plot of compressor algorithm")
    plt.ylabel("Amplitude")
    plt.xlabel("Sample [n]")
    # plot the threshold line
    plt.plot(np.arange(audio.shape[0]), np.ones(audio.shape[0]) * THRESHOLD)
    plt.plot(np.arange(audio.shape[0]), original_audio)
    plt.show()

if __name__ == "__main__":
    main()
