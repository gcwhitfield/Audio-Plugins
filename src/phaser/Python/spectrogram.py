import numpy as np
from scipy.io import wavfile
import scipy.signal
from matplotlib import pyplot as plt
import math

def plot_spectrogram(audio, samp_rate, title = "Untitled Spectrogram"):
    plt.title(title)
    f, t, sxx = scipy.signal.spectrogram(audio, fs = samp_rate, scaling = "spectrum", mode = 'magnitude')
    plt.pcolormesh(t, f, sxx)
    plt.show()

def main():
    # FILE = "noise-exp-12stage-0.26hz-0fb.wav"
    FILE = "WET-noise.wav"
    samp_rate, audio = wavfile.read(FILE)
    if len(audio.shape) > 1:
        audio = np.average(audio, axis=1)
    plot_spectrogram(audio, samp_rate, FILE)


if __name__ == "__main__":
    main()