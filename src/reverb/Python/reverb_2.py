from helpers import *

def main():
    # samp_rate, audio = wavfile.read("flintstones_rhodes.wav")
    # audio = np.average(audio, 1)

    samp_rate = 44100
    audio = np.zeros(44100 * 2)
    audio[0] = 1
    # audio = np.random.randn(44100)
    original_audio = np.copy(audio)

    # implementation of reverb using parameters from "freeverb" algortihm, from 
    # DSP related
    #
    # https://www.dsprelated.com/freebooks/pasp/Freeverb.html

    # feedback filters
    FB_DELAY1 = 1557
    FB_DELAY2 = 1617
    FB_DELAY3 = 1491
    FB_DELAY4 = 1422
    FB_DELAY5 = 1277
    FB_DELAY6 = 1356
    FB_DELAY7 = 1188
    FB_DELAY8 = 1116
    feedback1 = process_feedback_filter(audio, FB_DELAY1)
    feedback2 = process_feedback_filter(audio, FB_DELAY2)
    feedback3 = process_feedback_filter(audio, FB_DELAY3)
    feedback4 = process_feedback_filter(audio, FB_DELAY4)
    feedback5 = process_feedback_filter(audio, FB_DELAY5)
    feedback6 = process_feedback_filter(audio, FB_DELAY6)
    feedback7 = process_feedback_filter(audio, FB_DELAY7)
    feedback8 = process_feedback_filter(audio, FB_DELAY8)
    
    result = np.zeros(audio.shape[0] * 2)
    result += feedback1
    result += feedback2
    result += feedback3
    result += feedback4
    result += feedback5
    result += feedback6
    result += feedback7
    result += feedback8

    # allpass filters
    AP_DELAY1 = 225
    AP_DELAY2 = 556
    AP_DELAY3 = 441
    result = process_allpass_filter(result, AP_DELAY1)
    result = process_allpass_filter(result, AP_DELAY2)
    result = process_allpass_filter(result, AP_DELAY3)

    # apply mix
    MIX = 0.05
    result *= MIX
    result[np.arange(original_audio.shape[0])] += original_audio

    plt.title("Impulse response")
    plt.plot(np.arange(result.shape[0]), result)
    plt.show()
    # # plot spectrogram, view result
    # plot_spectrogram(result[0:result.shape[0]//2], samp_rate, "Noise audio processed spectrogram")

    # plot_feedback_filter_response(FB_DELAY1)
    # # plot_feedback_filter_response(FB_DELAY2)
    # # plot_feedback_filter_response(FB_DELAY3)
    # # plot_feedback_filter_response(FB_DELAY4)
    # # plot_feedback_filter_response(FB_DELAY5)
    # # plot_feedback_filter_response(FB_DELAY6)
    # # plot_feedback_filter_response(FB_DELAY7)
    # # plot_feedback_filter_response(FB_DELAY8)
    # plt.title("Response of feedback filter")
    # plt.xlabel("Frequency")
    # plt.ylabel("Amplitude (dB)")
    # plt.show()

    # w, mag, phas = plot_allpass_filter_response(AP_DELAY1)
    # plt.figure()
    # plt.semilogx(w, mag)    # Bode magnitude plot
    # plt.title("Response of allpass filter")
    # plt.figure()
    # plt.semilogx(w, phas)  # Bode phase plot
    # plt.show()

    # write_audio_safe("Processed flintstones without allpass audio (reverb 2).wav", samp_rate, result)

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