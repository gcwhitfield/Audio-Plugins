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

# ensures that the audio is normalized before writing to file, to prevent the 
# listener's ears from being damaged when listening to the audio
def write_audio_safe(file_name, fs, audio):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html
    wavfile.write(file_name, fs, audio / max(audio))