/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

//==============================================================================
/**
*/
class PhaserAudioProcessorEditor  : public juce::AudioProcessorEditor, 
                                    private juce::Slider::Listener
{
public:
    PhaserAudioProcessorEditor (PhaserAudioProcessor&);
    ~PhaserAudioProcessorEditor() override;

    //==============================================================================
    void paint (juce::Graphics&) override;
    void resized() override;

private:
    // This reference is provided as a quick way for your editor to
    // access the processor object that created it.
    PhaserAudioProcessor& audioProcessor;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (PhaserAudioProcessorEditor)
    
    // Sliders and labels for the plugin UI
    juce::Slider rateSlider;
    juce::Label rateLabel;
    juce::Slider depthSlider;
    juce::Label depthLabel;
    juce::Slider spreadSlider;
    juce::Label spreadLabel;
    juce::Slider stagesSlider;
    juce::Label stagesLabel;
    juce::Slider mixSlider;
    juce::Label mixLabel;

    void sliderValueChanged(juce::Slider *s) override;
};
