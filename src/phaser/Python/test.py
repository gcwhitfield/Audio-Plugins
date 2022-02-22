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

def main():
    samp_rate = 44100
    SIZE = 5 * samp_rate # 5 seconds
    A = 1
    Am = 2 * math.pi * 10
    w0 = 2 * math.pi * 512 * 2
    w2 = 2 * math.pi * 1
    output = np.cos(np.arange(0, 5, 1/samp_rate)*w0 + Am*np.cos(np.arange(0, 5, 1/samp_rate)*w2))
    plt.plot(np.arange(0, 40000), output[0:40000])
    plt.show()
    write_audio_safe("Chorus discussion system.wav", samp_rate, output)




if __name__ == "__main__":
    main()