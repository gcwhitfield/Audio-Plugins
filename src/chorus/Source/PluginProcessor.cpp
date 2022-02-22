/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
ChorusAudioProcessor::ChorusAudioProcessor()
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
}

ChorusAudioProcessor::~ChorusAudioProcessor()
{
}

//==============================================================================
const juce::String ChorusAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool ChorusAudioProcessor::acceptsMidi() const
{
   #if JucePlugin_WantsMidiInput
    return true;
   #else
    return false;
   #endif
}

bool ChorusAudioProcessor::producesMidi() const
{
   #if JucePlugin_ProducesMidiOutput
    return true;
   #else
    return false;
   #endif
}

bool ChorusAudioProcessor::isMidiEffect() const
{
   #if JucePlugin_IsMidiEffect
    return true;
   #else
    return false;
   #endif
}

double ChorusAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int ChorusAudioProcessor::getNumPrograms()
{
    return 1;   // NB: some hosts don't cope very well if you tell them there are 0 programs,
                // so this should be at least 1, even if you're not really implementing programs.
}

int ChorusAudioProcessor::getCurrentProgram()
{
    return 0;
}

void ChorusAudioProcessor::setCurrentProgram (int index)
{
}

const juce::String ChorusAudioProcessor::getProgramName (int index)
{
    return {};
}

void ChorusAudioProcessor::changeProgramName (int index, const juce::String& newName)
{
}

//==============================================================================
void ChorusAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    // Use this method as the place to do any pre-playback
    // initialisation that you need..
    
    juce::dsp::ProcessSpec spec;
    spec.maximumBlockSize = samplesPerBlock;
    spec.sampleRate = sampleRate;
    
    chorus.prepare (spec);
    chorus.reset();
    
    chorus.setRate(3);
    chorus.setDepth(0.03f);
    chorus.setCentreDelay(0);
    chorus.setFeedback(0.0f);
    chorus.setMix(0.8f);
    
    const int numInputChannels = getTotalNumInputChannels();
    const int delayBufferSize =  10 * (sampleRate + samplesPerBlock);
    mSampleRate = sampleRate;
    
    mDelayBuffer.setSize(numInputChannels, delayBufferSize);
    
    
    //juce::dsp::ProcessSpec lfoSpec = { sampleRate,samplesPerBlock,getMainBusNumOutputChannels() };
    lfo.prepare(spec);
    //type of oscillator
    lfo.initialise([](float x){return std::sin(x);}, 1000);
    lfo.setFrequency(100);
}

void ChorusAudioProcessor::releaseResources()
{
    // When playback stops, you can use this as an opportunity to free up any
    // spare memory, etc.
}

#ifndef JucePlugin_PreferredChannelConfigurations
bool ChorusAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
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

void ChorusAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    juce::ScopedNoDenormals noDenormals;
    auto totalNumInputChannels  = getTotalNumInputChannels();
    auto totalNumOutputChannels = getTotalNumOutputChannels();

    // In case we have more outputs than inputs, this code clears any output
    // channels that didn't contain input data, (because these aren't
    // guaranteed to be empty - they may contain garbage).
    // This is here to avoid people getting screaming feedback
    // when they first compile a plugin, but obviously you don't need to keep
    // this code if your algorithm always overwrites all the output channels.
    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear (i, 0, buffer.getNumSamples());

    // This is the place where you'd normally do the guts of your plugin's
    // audio processing...
    // Make sure to reset the state if your inner loop is processing
    // the samples and the outer loop is handling the channels.
    // Alternatively, you can process the samples with the channels
    // interleaved by keeping the same state.
    
    //JUCE chorus
//    juce::dsp::AudioBlock<float> sampleBlock (buffer);
//    chorus.process (juce::dsp::ProcessContextReplacing<float> (sampleBlock));
    
    //Own chorus
    //lfo.setFrequency(1.0);
    //std::cout << lfo.getFrequency() + "\n";
    //juce::Logger::outputDebugString(lfo.getFrequency() + "\n");

    float lfoOffset = std::max((10.0f * lfo.processSample(0.0f) + 10.0f), 0.0f) + 30;
    
    std::cout << lfoOffset;
    std::cout << "\n";
    const int bufferLength = buffer.getNumSamples();
    const int delayBufferLength = mDelayBuffer.getNumSamples();

    float delayTime1 = lfoOffset; //+ juce::Random::getSystemRandom().nextInt(1); //~30-50ms
    float delayTime2 = juce::Random::getSystemRandom().nextInt(10) + lfoOffset;
    float delayTime3 = 0;

    //delayTime1 = 30;
    //delayTime2 = 50;
    // Think about:
    /*
     Mag/phase of each system -- and delay lines
     1 + e^-j*omega*T
     
     why are phaser and chorus implemented differently
     */
    for (int channel = 0; channel < totalNumInputChannels; ++channel)
    {
        //buffer.applyGain(0.3);
        const float *bufferData = buffer.getReadPointer(channel);
        const float *delayBufferData = mDelayBuffer.getReadPointer(channel);

        fillDelayBuffer(channel, bufferLength, delayBufferLength, bufferData, delayBufferData);
        getFromDelayBuffer(buffer, channel, bufferLength, delayBufferLength, bufferData, delayBufferData, delayTime1);
        //getFromDelayBuffer(buffer, channel, bufferLength, delayBufferLength, bufferData, delayBufferData, delayTime2);


        

        // ..do something to the data...
    }

    mWritePosition += bufferLength;
    mWritePosition %= delayBufferLength;
    
    //buffer.applyGain(3.0);
}

void ChorusAudioProcessor::fillDelayBuffer(int channel, const int bufferLength, const int delayBufferLength, const float *bufferData, const float *delayBufferData)
{
    // Copy data from main buffer to delay buffer
    if(delayBufferLength > bufferLength + mWritePosition)
    {
        mDelayBuffer.copyFromWithRamp(channel, mWritePosition, bufferData, bufferLength, 0.8, 0.8);
    }
    
    else
    {
        int bufferRemaining = delayBufferLength - mWritePosition;
        mDelayBuffer.copyFromWithRamp(channel, mWritePosition, bufferData, bufferRemaining, 0.8, 0.8);
        mDelayBuffer.copyFromWithRamp(channel, 0, bufferData, bufferLength - bufferRemaining, 0.8, 0.8);
    }
}

void ChorusAudioProcessor::getFromDelayBuffer(juce::AudioBuffer<float>& buffer, int channel, const int bufferLength, const int delayBufferLength, const float *bufferData, const float *delayBufferData, float delayTime)
{
//    float offset_float = mSampleRate * delayTime / 1000;
////    std::cout << offset_float;
////    std::cout << "\n";
//    int offset = static_cast<int> (offset_float);
////    std::cout << offset;
////    std::cout << "\n";
//    int readPosition = static_cast<int> (delayBufferLength + mWritePosition - offset) % delayBufferLength;
    const int readPosition = static_cast<int> (delayBufferLength + mWritePosition - (mSampleRate * delayTime / 1000)) % delayBufferLength;
    
    if(delayBufferLength > bufferLength + readPosition)
    {
        buffer.addFromWithRamp(channel, 0, delayBufferData + readPosition, bufferLength, 1.0, 1.0);
    }
    
    else
    {
        int bufferRemaining = delayBufferLength - readPosition;
        buffer.addFromWithRamp(channel, 0, delayBufferData + readPosition, bufferRemaining, 1.0, 1.0);
        buffer.addFromWithRamp(channel, bufferRemaining, delayBufferData, bufferLength - bufferRemaining, 1.0, 1.0);
    }
}

//==============================================================================
bool ChorusAudioProcessor::hasEditor() const
{
    return true; // (change this to false if you choose to not supply an editor)
}

juce::AudioProcessorEditor* ChorusAudioProcessor::createEditor()
{
    return new ChorusAudioProcessorEditor (*this);
}

//==============================================================================
void ChorusAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    // You should use this method to store your parameters in the memory block.
    // You could do that either as raw data, or use the XML or ValueTree classes
    // as intermediaries to make it easy to save and load complex data.
}

void ChorusAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    // You should use this method to restore your parameters from this memory block,
    // whose contents will have been created by the getStateInformation() call.
}

//==============================================================================
// This creates new instances of the plugin..
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new ChorusAudioProcessor();
}
