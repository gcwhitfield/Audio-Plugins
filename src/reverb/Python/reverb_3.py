from helpers import *

def main():
    samp_rate, audio = wavfile.read("flintstones_rhodes.wav")
    audio = np.average(audio, 1)

    # samp_rate = 44100
    # audio = np.zeros(44100 * 2)
    # audio[0] = 1
    # audio = np.random.randn(44100)
    original_audio = np.copy(audio)

    # implementation of reverb using parameters from "freeverb" algortihm, from 
    # DSP related
    #
    # https://www.dsprelated.com/freebooks/pasp/Freeverb.html

    result = np.zeros(audio.shape[0] * 2)

    # allpass filters
    AP_DELAY1 = 225
    AP_DELAY2 = 556
    AP_DELAY3 = 441
    AP_DELAY4 = 322
    AP_DELAY5 = 411
    result = process_allpass_filter(audio, AP_DELAY1)
    result = process_allpass_filter(result, AP_DELAY2)
    result = process_allpass_filter(result, AP_DELAY3)
    result = process_allpass_filter(result, AP_DELAY4)
    result = process_allpass_filter(result, AP_DELAY5)

    # apply mix
    MIX = 1
    result *= MIX
    result[np.arange(original_audio.shape[0])] += original_audio

    plt.title("Impulse response of network without allpass")
    plt.plot(np.arange(result.shape[0]), result)
    plt.show()
    # plot spectrogram, view result
    plot_spectrogram(result[0:result.shape[0]//2], samp_rate, "Noise audio processed spectrogram")

    write_audio_safe("Processed flintstones (reverb 3).wav", samp_rate, result)

def plot_feedback_filter_response(delay):
    b = np.zeros(delay)
    b[b.shape[0] - 1] = 1
    a = np.zeros(delay)
    a[0] = 1
    a[a.shape[0] - 1] = -0.84
    w, h = scipy.signal.freqz(b, a)
    plt.plot(w, 20 * np.log10(abs(h)))

def plot_allpass_filter_response(delay):
    b = np.zeros(delay)
    b[b.shape[0] - 1] = 1
    b[0] = -0.5
    a = np.zeros(delay)
    a[0] = 1
    a[a.shape[0] - 1] = -0.5
    w, mag, phas = scipy.signal.bode((b, a))
    return w, mag, phas

if __name__ == "__main__":
    main()