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

    # feedback filters
    # random delay amounts generated with "generate_random_vals.py"
    FB_DELAY1 = 6710
    FB_DELAY2 = 5209
    FB_DELAY3 = 6860
    FB_DELAY4 = 5359
    FB_DELAY5 = 5401
    FB_DELAY6 = 6165
    FB_DELAY7 = 6905
    FB_DELAY8 = 6315
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

    plot_feedback_filter_response(FB_DELAY1)
    plot_feedback_filter_response(FB_DELAY2)
    plot_feedback_filter_response(FB_DELAY3)
    plot_feedback_filter_response(FB_DELAY4)
    plot_feedback_filter_response(FB_DELAY5)
    plot_feedback_filter_response(FB_DELAY6)
    plot_feedback_filter_response(FB_DELAY7)
    plot_feedback_filter_response(FB_DELAY8)
    plt.title("Response of feedback filters (random coeffs in [5000, 7000]")
    plt.xlabel("Frequency")
    plt.ylabel("Amplitude (dB)")
    plt.show()

    # apply mix
    MIX = 0.05
    result *= MIX
    result[np.arange(original_audio.shape[0])] += original_audio

    plt.plot(np.arange(0, result.shape[0]//2), result[0:result.shape[0]//2])
    plt.title("Impulse response of reverb (random coeffs in [5000, 7000)")
    plt.show()

    # write_audio_safe("Processed flintstones with random coefficients (reverb 5).wav", samp_rate, result)

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