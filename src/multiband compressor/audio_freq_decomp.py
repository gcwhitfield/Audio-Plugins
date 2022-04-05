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
from filters.lowpass2 import *
from filters.highpass2 import *
from filters.highpass3 import *
from filters.highpass4 import *

def main():
    # read the audio file
    # samp_rate, audio = wavfile.read("drums.wav")
    # audio = np.average(audio, 1)

    # test with sin function
    # samp_rate = 100
    # audio = np.sin(np.arange(0, 1, 0.01) * 10)
    # audio += 0.2 * np.sin(np.arange(0, 1, 0.01) * 5)
    # original_audio = np.copy(audio)

    # test with noise function
    samp_rate = 44100
    audio = np.random.randn(samp_rate * 10)

    # create lowpass filter
    # desired = np.array([1, 1, 0, 0])
    # freqs = np.array([0, 150/samp_rate, 250/samp_rate, 1])
    # numtaps = 3001
    # low = scipy.signal.firls(numtaps, freqs, desired)
    # w, h = scipy.signal.freqz(low)
    # plt.plot(w, h)
    # plt.title("Freqz of lowpass filter")
    # plt.show()

    # create bandpass filter
    # desired = np.array([0, 0, 1, 1, 0, 0])
    # freqs = np.array([0, 150/samp_rate, 250/samp_rate, 5800/samp_rate, 6200/samp_rate, 1])
    # numtaps = 6001
    # band = scipy.signal.firls(numtaps, freqs, desired)
    # w, h = scipy.signal.freqz(band)
    # plt.plot(w, h)
    # plt.title("Freqz of bandpass filter")
    # plt.show()
    
    # create highpass filter
    # desired = np.array([0, 0, 1, 1])
    # freqs = np.array([0, 5800/samp_rate, 6200/samp_rate, 1])
    # numtaps = 5001
    # high = scipy.signal.firls(numtaps, freqs, desired)
    # w, h = scipy.signal.freqz(high)
    # plt.plot(w, h)
    # plt.title("Freqz of highpass filter")
    # plt.show()
    
    plot_spectrogram(audio, samp_rate, "Original audio")
    l = scipy.signal.convolve(audio, lowpass2(), 'same')
    b = scipy.signal.convolve(audio, bandpass(), 'same')
    h = scipy.signal.convolve(audio, highpass4(), 'same')
    plot_spectrogram(l, samp_rate, "Audio convolved with lowpass")
    plot_spectrogram(b, samp_rate, "Audio convolved with bandpass")
    plot_spectrogram(h, samp_rate, "Audio convolved with highpass")
    plot_spectrogram(l + b + h, samp_rate, "Audio reconstructed")

    write_audio_safe("Original noise.wav", samp_rate,  audio)
    write_audio_safe("Lowpass noise.wav", samp_rate,  l)
    write_audio_safe("Bandpass noise.wav", samp_rate,  b)
    write_audio_safe("Highpass noise.wav", samp_rate,  h)


if __name__ == "__main__":
    main()
