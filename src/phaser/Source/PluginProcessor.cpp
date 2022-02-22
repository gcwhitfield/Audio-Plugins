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
    
    // ---------- Stages (number of loops in for loop) ----------
    for (size_t i = 0; i < *stages; i++)
    {
        // create an allpass filter with coefficients designed to place pi phase at a particular frequency
        // allpass filter design from Stanford lesson on phasers
        // https://ccrma.stanford.edu/~jos/pasp/Phasing_2nd_Order_Allpass_Filters.html
        
        // logarithmically interpolate the notch angles between 100 hz and 10,000 hz
        float angle = pow(100, i / (float)*stages) * pow(10000, (1 - (i / (float)*stages)));
        float radius = 0.5;
        float a1 = -radius * 2 * cos(angle);
        float a2 = radius * radius;
        
        // update the filter state
        // filter update derived from example on JUCE IIR filtering from The Audio Programmer
        // https://github.com/TheAudioProgrammer/juceIIRFilter/blob/master/Source/PluginProcessor.cpp
        *filter.state = juce::dsp::IIR::Coefficients<float>(a2, a1, 1, 1, a1, a2);
        filter.process(juce::dsp::ProcessContextReplacing<float>(wet));
    }
    
    for (int channel = 0; channel < buffer.getNumChannels(); channel++) {
        float *data = buffer.getWritePointer(channel, 0);
        float *d = dry.getChannelPointer(channel);
        float *w = wet.getChannelPointer(channel);
        
        for (size_t i = 0; i < buffer.getNumSamples(); i++) {
            // add input audio to wet signal with 'g' parameter
            w[i] = g * d[i];
            
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
