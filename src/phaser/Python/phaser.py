from tkinter.filedialog import Directory
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
    print("Reading audio...")

    SONG_FILE = "noise.wav"
    # step 1) read the audio, convert from stereo signal into mono
    samp_rate, audio = wavfile.read(SONG_FILE)
    samp_rate_reference, audio_reference = wavfile.read(SONG_FILE.split(".")[0] + "-phaser-reference.wav")
    audio = np.average(audio, axis=1)
    audio_reference = np.average(audio_reference, axis=1)

    plt.plot(np.arange(audio.shape[0]), audio)
    plt.show()
    plot_spectrogram(audio, samp_rate, "Spectrogram of input audio")

    # step 2) break up audio signal into many short segments
    SEGMENT_SIZE = math.ceil(samp_rate * 0.02) # size of each short time segment (20 milliseconds)
    idxs = np.arange(SEGMENT_SIZE)
    num_segments = audio.shape[0] // SEGMENT_SIZE

    # step 3) Apply phaser algorithm
    dry = audio
    wet = np.copy(audio)
    lfo_freq = 0.5 # hertz
    lfo_amp = 100
    lfo = lfo_amp * np.cos(np.arange(0, audio.shape[0]) * (lfo_freq * 2 * math.pi) / samp_rate)
    G = 1
    FEEDBACK = 0.5
    NUM_PASSES = 3 # numter of times to pass the signal through the filter for feedback
    for seg_idx in range(0, num_segments):
        # Phaser properties
        STAGES = 12
        lfo_block = lfo[idxs]
        # plt.plot(np.arange(lfo.shape[0]), lfo)
        # plt.title("LFO")
        # plt.xlabel("n")
        # plt.ylabel("Amplitude")
        # plt.show()
        # step 3.1) apply multiple allpass stages to the wet signal
        for k in range(NUM_PASSES):
            wet[idxs] = dry[idxs] + FEEDBACK*wet[idxs]
            for i in range(1, STAGES + 1):
                block = wet[idxs]
                # the i'th notch will be placed at a frequency between 'min_freq' and 
                # 'max_freq'. The exact frequency of the notch will be determined by a logarithmic 
                # interpolation between 'min_freq' and 'max_freq'
                R = 1.2
                min_freq = 100
                max_freq = 20000
                freq = pow(min_freq, (1 - (i/STAGES))) * pow(max_freq, i/STAGES) + (lfo_block[0])
                a1 = -2 * R * math.cos(freq * 100 / samp_rate)
                a2 = R * R
                filter = SecondOrderAllPassFilter(a1, a2)
                wet[idxs] = filter.process_block(block)
                
        idxs += SEGMENT_SIZE

    # step 3.2) add wet signal back to original signal, with G parameter
    wet = wet + G * dry
    
    # step 4) show spectrogram of the signal with phaser applied
    plot_spectrogram(wet, samp_rate, "Sepctrogram of wet audio")
    plot_spectrogram(dry, samp_rate, "Spectrogram of dry audio")
    plot_spectrogram(audio_reference, samp_rate_reference, "Spectrogram of reference phaser audio from Logic Pro X")

    write_audio_safe("DRY-" + SONG_FILE, samp_rate, dry)
    write_audio_safe("WET-" + SONG_FILE, samp_rate, wet)
    write_audio_safe("ORIGINAL-" + SONG_FILE, samp_rate, audio)

class SecondOrderAllPassFilter:
    def __init__(self, a1, a2):
        self.update_coefficients(a1, a2)

    def update_coefficients(self, a1, a2):
        self.a1 = a1
        self.a2 = a2

    # given a block of audio, applies allpass filter to the block
    # audio_block: a numpy array
    def process_block(self, audio_block):
        dry = np.copy(audio_block)
        wet = np.copy(audio_block)
        for i in range(0, audio_block.shape[0]):
            x_n = dry[i]                
            x_n_minus_2 = dry[(i - 2) % audio_block.shape[0]]
            y_n_minus_2 = wet[(i - 2) % audio_block.shape[0]]
            x_n_minus_1 = dry[(i - 1) % audio_block.shape[0]]
            y_n_minus_1 = wet[(i - 1) % audio_block.shape[0]]
            if i - 2 < 0:
                x_n_minus_2 = 0
                y_n_minus_2 = 0
            if i - 1 < 0:
                x_n_minus_1 = 0
                y_n_minus_1 = 0
            y_n = x_n_minus_2 + ((x_n + self.a1*(x_n_minus_1 - y_n_minus_1) - y_n_minus_2) / self.a2)
            wet[i] = y_n
        return wet
    
    def test_process_block(self, noise_len):
        b = np.array([self.a2, self.a1, 1])
        a = np.array([1, self.a1, self.a2])
        w, h = scipy.signal.freqz(b, a)
        plt.plot(w, np.angle(h))
        plt.xlabel("Frequency (radian)")
        plt.ylabel("Phase shift")
        plt.show()
        plt.plot(w, 20*np.log10(h))
        plt.title("Magnitude response of filter")
        plt.show()
        
        noise = np.random.randn(noise_len)
        noise_copy = np.copy(noise)
        samp_rate = 44100
        plot_spectrogram(noise, samp_rate, "Spectrogram of noise unfiltered")
        plt.plot(np.arange(noise.shape[0]), noise)
        plt.show()
        wet = self.process_block(noise)
    
        print("Average deviation: " + str(np.mean(np.power(wet - noise, 2))))
        plot_spectrogram(wet - noise, samp_rate, "Spectrogram of filtered noise")
        plt.plot(np.arange(wet.shape[0]), wet)
        plt.show()

if __name__ == "__main__":
    main()