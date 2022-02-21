/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
PhaserAudioProcessorEditor::PhaserAudioProcessorEditor (PhaserAudioProcessor& p)
    : AudioProcessorEditor (&p), audioProcessor (p)
{
    // Make sure that before the constructor has finished, you've set the
    // editor's size to whatever you need it to be.
    setSize (700, 300);

    // add listeners to the sliders
    stagesSlider.addListener(this);
    depthSlider.addListener(this);
    rateSlider.addListener(this);
    spreadSlider.addListener(this);
    mixSlider.addListener(this);

    // set default values to the sliders
    stagesSlider.setSliderStyle(juce::Slider::Rotary);
    stagesSlider.setRange(1, 10, 1);
    stagesSlider.setTextBoxStyle(juce::Slider::NoTextBox, false, 90, 0);
    stagesSlider.setPopupDisplayEnabled(true, false, this);
    stagesSlider.setValue(5);
    mixSlider.setSliderStyle(juce::Slider::Rotary);
    mixSlider.setRange(0, 100, 1);
    mixSlider.setTextBoxStyle(juce::Slider::NoTextBox, false, 90, 0);
    mixSlider.setPopupDisplayEnabled(true, false, this);
    mixSlider.setTextValueSuffix("%");
    mixSlider.setValue(0);
    depthSlider.setSliderStyle(juce::Slider::Rotary);
    depthSlider.setRange(0, 100, 1);
    depthSlider.setTextBoxStyle(juce::Slider::NoTextBox, false, 90, 0);
    depthSlider.setPopupDisplayEnabled(true, false, this);
    depthSlider.setTextValueSuffix("%");
    depthSlider.setValue(50);
    spreadSlider.setSliderStyle(juce::Slider::Rotary);
    spreadSlider.setRange(0, 100, 1);
    spreadSlider.setTextBoxStyle(juce::Slider::NoTextBox, false, 90, 0);
    spreadSlider.setPopupDisplayEnabled(true, false, this);
    spreadSlider.setTextValueSuffix("%");
    spreadSlider.setValue(50);
    rateSlider.setSliderStyle(juce::Slider::Rotary);
    rateSlider.setRange(0.1, 10);
    rateSlider.setTextBoxStyle(juce::Slider::NoTextBox, false, 90, 0);
    rateSlider.setPopupDisplayEnabled(true, false, this);
    rateSlider.setTextValueSuffix("Hz");
    rateSlider.setValue(1);

    addAndMakeVisible(&stagesSlider);
    addAndMakeVisible(&mixSlider);
    addAndMakeVisible(&depthSlider);
    addAndMakeVisible(&spreadSlider);
    addAndMakeVisible(&rateSlider);

    // add labels to the sliders
    addAndMakeVisible(&stagesLabel);
    stagesLabel.setText("Stages", juce::dontSendNotification);
    stagesLabel.attachToComponent(&stagesSlider, false);
    addAndMakeVisible(&mixLabel);
    mixLabel.setText("Mix", juce::dontSendNotification);
    mixLabel.attachToComponent(&mixSlider, false);
    addAndMakeVisible(&depthLabel);
    depthLabel.setText("Depth", juce::dontSendNotification);
    depthLabel.attachToComponent(&depthSlider, false);
    addAndMakeVisible(&spreadLabel);
    spreadLabel.setText("Spread", juce::dontSendNotification);
    spreadLabel.attachToComponent(&spreadSlider, false);
    addAndMakeVisible(&rateLabel);
    rateLabel.setText("Rate", juce::dontSendNotification);
    rateLabel.attachToComponent(&rateSlider, false);
    
    // initialize parameters in audio processor
    *(audioProcessor.mix) = mixSlider.getValue() / 100;
    *(audioProcessor.depth) = depthSlider.getValue();
    *(audioProcessor.spread) = spreadSlider.getValue();
    *(audioProcessor.stages) = stagesSlider.getValue();
    *(audioProcessor.rate) = rateSlider.getValue();
}

PhaserAudioProcessorEditor::~PhaserAudioProcessorEditor()
{

}

//==============================================================================
void PhaserAudioProcessorEditor::paint (juce::Graphics& g)
{
    // (Our component is opaque, so we must completely fill the background with a solid colour)
    g.fillAll (getLookAndFeel().findColour (juce::ResizableWindow::backgroundColourId));

    g.setColour (juce::Colours::white);
    g.setFont (15.0f);
    g.drawFittedText ("Phaser!", getLocalBounds().getWidth() / 2 - 35, 10, 75, 75, juce::Justification::centred, 1);
}

void PhaserAudioProcessorEditor::resized()
{
    // This is generally where you'll want to lay out the positions of any
    // subcomponents in your editor..

    // sets the positions and size of the subcomponents with arguments (x, y, width, height)
    stagesSlider.setBounds(100, 100, 75, 75);
    rateSlider.setBounds(200, 100, 75, 75);
    spreadSlider.setBounds(300, 100, 75, 75);
    depthSlider.setBounds(400, 100, 75, 75);
    mixSlider.setBounds(500, 100, 75, 75);
}

void PhaserAudioProcessorEditor::sliderValueChanged(juce::Slider *s)
{
    *(audioProcessor.mix) = mixSlider.getValue() / 100;
    *(audioProcessor.depth) = depthSlider.getValue();
    *(audioProcessor.spread) = spreadSlider.getValue();
    *(audioProcessor.stages) = stagesSlider.getValue();
    *(audioProcessor.rate) = rateSlider.getValue();
}
