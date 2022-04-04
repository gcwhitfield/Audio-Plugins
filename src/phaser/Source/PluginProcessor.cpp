/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
PhaserAudioProcessor::PhaserAudioProcessor()
#ifndef JucePlugin_PreferredChannelConfigurations
     : AudioProcessor (BusesProperties()
                     #if ! JucePlugin_IsMidiEffect
                      #if ! JucePlugin_IsSynth
                       .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                      #endif
                       .withOutput ("Output", juce::AudioChannelSet::stereo(), true)
                     #endif
                       )
#endif
{
    addParameter(mix = new juce::AudioParameterFloat(
        "mix", // parameter ID
        "Mix", // paremeter name
        0.0, // min value
        1.0, // max value
        0.0)); // default value
    addParameter(stages = new juce::AudioParameterInt(
        "stages",
        "Stages",
        1, 
        10, 
        1
    ));
    addParameter(depth = new juce::AudioParameterFloat(
        "depth",
        "Depth", 
        0.0, 
        100.0, 
        0.0));
    addParameter(spread = new juce::AudioParameterFloat(
        "spread", 
        "Spread", 
        0.0, 
        100.0, 
        0.0));
    addParameter(rate = new juce::AudioParameterFloat(
        "rate", 
        "Rate", 
        0.1, 
        10.0,
        0.1));
}

PhaserAudioProcessor::~PhaserAudioProcessor()
{
}

//==============================================================================
const juce::String PhaserAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool PhaserAudioProcessor::acceptsMidi() const
{
   #if JucePlugin_WantsMidiInput
    return true;
   #else
    return false;
   #endif
}

bool PhaserAudioProcessor::producesMidi() const
{
   #if JucePlugin_ProducesMidiOutput
    return true;
   #else
    return false;
   #endif
}

bool PhaserAudioProcessor::isMidiEffect() const
{
   #if JucePlugin_IsMidiEffect
    return true;
   #else
    return false;
   #endif
}

double PhaserAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int PhaserAudioProcessor::getNumPrograms()
{
    return 1;   // NB: some hosts don't cope very well if you tell them there are 0 programs,
                // so this should be at least 1, even if you're not really implementing programs.
}

int PhaserAudioProcessor::getCurrentProgram()
{
    return 0;
}

void PhaserAudioProcessor::setCurrentProgram (int index)
{
}

const juce::String PhaserAudioProcessor::getProgramName (int index)
{
    return {};
}

void PhaserAudioProcessor::changeProgramName (int index, const juce::String& newName)
{
}

//==============================================================================
void PhaserAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    // Use this method as the place to do any pre-playback
    // initialisation that you need..
    
    // IIR filter initialization taken from TheAudioProgrammer's example code on JUCE IIR Filters
    // https://github.com/TheAudioProgrammer/juceIIRFilter/blob/master/Source/PluginProcessor.cpp
    
    juce::dsp::ProcessSpec spec;
    spec.sampleRate = sampleRate;
    spec.maximumBlockSize = samplesPerBlock;
    spec.numChannels = getTotalNumInputChannels();
    
    filter.prepare(spec);
    filter.reset();
}

void PhaserAudioProcessor::releaseResources()
{
    // When playback stops, you can use this as an opportunity to free up any
    // spare memory, etc.
}

#ifndef JucePlugin_PreferredChannelConfigurations
bool PhaserAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
  #if JucePlugin_IsMidiEffect
    juce::ignoreUnused (layouts);
    return true;
  #else
    // This is the place where you check if the layout is supported.
    // In this template code we only support mono or stereo.
    // Some plugin hosts, such as certain GarageBand versions, will only
    // load plugins that support stereo bus layouts.
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
     && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

    // This checks if the input layout matches the output layout
   #if ! JucePlugin_IsSynth
    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;
   #endif

    return true;
  #endif
}
#endif

void PhaserAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    juce::ScopedNoDenormals noDenormals;
    auto totalNumInputChannels  = getTotalNumInputChannels();
    auto totalNumOutputChannels = getTotalNumOutputChannels();

    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear (i, 0, buffer.getNumSamples());
    
    juce::AudioBuffer<float> bufferCopy = buffer;
    juce::dsp::AudioBlock<float> dry (buffer);
    juce::dsp::AudioBlock<float> wet (bufferCopy);
    float g = 1.0;
    
    size_t num_passes = 3; // the number of times that the input buffer is paessed through the
    // system

    for (int channel = 0; channel < buffer.getNumChannels(); channel++) {
        float *d = dry.getChannelPointer(channel);
        float *w = wet.getChannelPointer(channel);
        for (size_t k = 0; k < num_passes; k++) {
            // ---------- Stages (number of notches added to signal) ----------
            for (size_t i = 1; i < *stages + 1; i++) {
                // create an allpass filter with coefficients designed to place pi phase at a particular frequency
                // allpass filter design from Stanford lesson on phasers
                // https://ccrma.stanford.edu/~jos/pasp/Phasing_2nd_Order_Allpass_Filters.html
                
                // logarithmically place the notch frequencies between 100 hz and 20,000 hz
                float freq = pow(100, i / (float)*stages) * pow(20000, (1 - (i / (float)*stages)));
                float radius = 1.2;
                float a1 = -radius * 2 * cos(freq / getSampleRate());
                float a2 = radius * radius;
                
                // Convolve the signal with an allpass filter
                for (size_t j = 0; j < buffer.getNumSamples(); j++) {
                    float x_n = d[j];
                    float x_n_minus_2 = d[(j-2) % buffer.getNumSamples()];
                    float y_n_minus_2 = w[(j-2) % buffer.getNumSamples()];
                    float x_n_minus_1 = d[(j-1) % buffer.getNumSamples()];
                    float y_n_minus_1 = w[(j-1) % buffer.getNumSamples()];
                    if (j  <= 1) {
                        x_n_minus_2 = 0;
                        y_n_minus_2 = 0;
                    }
                    if (j <= 0) {
                        x_n_minus_1 = 0;
                        y_n_minus_1 = 0;
                    }
                    float y_n = x_n_minus_2 + ((x_n + a1*(x_n_minus_1 - y_n_minus_1) - y_n_minus_2) / a2);
                    w[i] = y_n;
                }
            }
        }
    }

    for (int channel = 0; channel < buffer.getNumChannels(); channel++) {
        float *data = buffer.getWritePointer(channel, 0);
        float *d = dry.getChannelPointer(channel);
        float *w = wet.getChannelPointer(channel);
        
        for (size_t i = 0; i < buffer.getNumSamples(); i++) {
            // add input audio to wet signal with 'g' parameter
            w[i] += g * d[i];
            w[i] /= 2.0f;
            
            // --------- Mix ----------
            data[i] = d[i]*(1.0 - *mix) + w[i]*(*mix);
        }

    }
}

//==============================================================================
bool PhaserAudioProcessor::hasEditor() const
{
    return true; // (change this to false if you choose to not supply an editor)
}

juce::AudioProcessorEditor* PhaserAudioProcessor::createEditor()
{
    return new PhaserAudioProcessorEditor (*this);
}

//==============================================================================
void PhaserAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    // You should use this method to store your parameters in the memory block.
    // You could do that either as raw data, or use the XML or ValueTree classes
    // as intermediaries to make it easy to save and load complex data.
}

void PhaserAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    // You should use this method to restore your parameters from this memory block,
    // whose contents will have been created by the getStateInformation() call.
}

//==============================================================================
// This creates new instances of the plugin..
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new PhaserAudioProcessor();
}
