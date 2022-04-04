from curses import delay_output
import numpy as np
from scipy.io import wavfile 
import scipy.signal
from matplotlib import pyplot as plt
import math
import random

def plot_spectrogram(audio, samp_rate, title = "Untitled Spectrogram"):
    plt.title(title)
    f, t, sxx = scipy.signal.spectrogram(audio, fs = samp_rate, scaling = "spectrum", mode = 'magnitude')
    plt.pcolormesh(t, f, sxx)
    plt.show()

# ensures that the audio is normalized before writing to file, to prevent the 
# listener's ears from being damaged when listening to the audio
def write_audio_safe(file_name, fs, audio):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html
    wavfile.write(file_name, fs, audio / max(audio))

# takes audio file as input, applies feedback filter to it as output
def process_feedback_filter(audio, delay_amount):
    g = 0.84
    delay_amount = int(delay_amount)
    result = np.zeros(audio.shape[0] * 2)
    x_n = np.zeros(audio.shape[0] * 2)
    for i in np.arange(result.shape[0]):
        if i < audio.shape[0]:
            x_n[i] += audio[i]
        if i >= delay_amount:
            result[i] = result[i-delay_amount]*g + x_n[i-delay_amount]
    return result
    
# takes audio file as input, applies allpass filter for echo density smoothing to it
def process_allpass_filter(audio, delay_amount):
    h = 0.5
    delay_amount = int(delay_amount)
    result = np.zeros(audio.shape[0])
    x_n = audio
    feedback_x_n = np.zeros(audio.shape[0])
    for i in np.arange(0, result.shape[0]):
        result[i] += x_n[i] * -1 * h
        if i >= delay_amount:
            feedback_x_n[i] += x_n[i-delay_amount] + h*feedback_x_n[i-delay_amount]
            result[i] += feedback_x_n[i] * (1-pow(h, 2))
    return result