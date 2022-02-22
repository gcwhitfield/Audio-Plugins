import numpy as np
from scipy.io import wavfile
import scipy.signal
from matplotlib import pyplot as plt
import math

def plot_spectrogram(audio, samp_rate, title = "Untitled Spectrogram"):
    plt.title(title)
    f, t, sxx = scipy.signal.spectrogram(audio, fs = samp_rate, scaling = "spectrum", mode = 'phase')
    plt.pcolormesh(t, f, sxx)
    plt.show()

def main():
    R = 2
    FREQ = 1000 # hertz
    SAMP_RATE = 4410
    NOISE_LEN = 100000
    noise = np.random.randn(NOISE_LEN)
    a1 = -2 * R * math.cos(FREQ/SAMP_RATE)
    a2 = R * R

    dry = np.copy(noise)
    wet = np.copy(noise)
    for i in np.arange(0, NOISE_LEN):
        x_n = dry[i]                
        x_n_minus_2 = dry[(i - 2) % NOISE_LEN]
        y_n_minus_2 = wet[(i - 2) % NOISE_LEN]
        x_n_minus_1 = dry[(i - 1) % NOISE_LEN]
        y_n_minus_1 = wet[(i - 1) % NOISE_LEN]
        if i - 2 < 0:
            x_n_minus_2 = 0
            y_n_minus_2 = 0
        if i - 1 < 0:
            x_n_minus_1 = 0
            y_n_minus_1 = 0
        y_n = x_n_minus_2 + ((x_n + a1*(x_n_minus_1 - y_n_minus_1) - y_n_minus_2) / a2)
        wet[i] = y_n

    plt.plot(np.arange(0, NOISE_LEN), noise)
    plt.title("Plot of noise")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.show()
    plt.plot(np.arange(0, NOISE_LEN), wet)
    plt.title("Plot of noise")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.show()
    plot_spectrogram(noise, SAMP_RATE, "Spectrogram of input noise")
    plot_spectrogram(wet, SAMP_RATE, "Spectrogram of noise after going through allpass filter")
    




if __name__ == "__main__":
    main()