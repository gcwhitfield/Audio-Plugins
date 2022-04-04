from curses import delay_output
import numpy as np
from scipy.io import wavfile 
import scipy.signal
from matplotlib import pyplot as plt
import math
import random
from helpers import * 

def main():
    samp_rate, audio = wavfile.read("clap.wav")
    audio = np.average(audio, 1)
    
    plot_spectrogram(audio, samp_rate, "Clap audio spectrogram")

    # step 1) apply the feedback filters to the audio
    primes = [2, 79, 191, 311, 439, 577, 701, 853, 997, 1129, 1291, 1453, 1601, 1753, 4219, 12097, 19927]
    NUM_FEEDBACK_FILTERS = 200
    delay_min = int(samp_rate * 0.01)
    delay_max = int(samp_rate * 0.02)
    result = np.zeros(audio.shape[0] * 6) # by default, the output audio is 3 times as long as the input audio

    for i in np.arange(0, NUM_FEEDBACK_FILTERS):
        delay_amount = int(random.randint(delay_min, delay_max))
        # delay_amount = primes[(i+5) % len(primes)]
        processed_audio = process_feedback_filter(audio, delay_amount)
        idxs = np.arange(processed_audio.shape[0]) + delay_amount
        result[idxs] += processed_audio

    # step 2) apply allpass filters to smooth out the long reverberations
    NUM_ALLPASS_FILTERS = 200
    for i in range(NUM_ALLPASS_FILTERS):
        result = process_allpass_filter(result, int(samp_rate * 0.5))
    

    plot_spectrogram(result[0:result.shape[0]], samp_rate, "Clap audio spectrogram after feedback filters")
    write_audio_safe("processed_clap.wav", samp_rate, result)

if __name__ == "__main__":
    main()