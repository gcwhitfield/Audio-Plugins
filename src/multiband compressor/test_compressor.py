import numpy as np
from scipy.io import wavfile 
import scipy.signal
from matplotlib import pyplot as plt
import math
import random

from compressor import *

def main():
    samp_rate, audio = wavfile.read("dance party.wav")
    audio = audio.astype("float32")
    audio /= max(audio)
    audio = np.average(audio, axis=1)
    original_audio = np.copy(audio)
    audio = process_compressor(samp_rate, audio)

    plt.title("Plot of compressor algorithm")
    plt.ylabel("Amplitude")
    plt.xlabel("Sample [n]")

    # plot the audio after compression algorithm
    plt.plot(np.arange(audio.shape[0]), audio)
    plt.plot(np.arange(audio.shape[0]), np.ones(audio.shape[0]) * THRESHOLD_HIGH, 'r')
    plt.plot(np.arange(audio.shape[0]), np.ones(audio.shape[0]) * -THRESHOLD_HIGH, 'r')
    plt.plot(np.arange(audio.shape[0]), np.ones(audio.shape[0]) * THRESHOLD_LOW, 'g')
    plt.plot(np.arange(audio.shape[0]), np.ones(audio.shape[0]) * -THRESHOLD_LOW, 'g')
    plt.plot(np.arange(audio.shape[0]), original_audio)
    plt.show()
    
if __name__ == "__main__":
    main()