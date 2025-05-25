# 🎧 Bluetooth Lighting + Audio Reactive System

This system connects to any Bluetooth lighting device with a **"QHM-"** prefix in its Bluetooth name and runs on **macOS**.

Here are the lights I used: https://amzn.to/3FaI5o5

> Support for Windows and Linux is coming soon!

## 🚀 Setup Instructions

### 1. Install BlackHole

Install the 2-channel virtual audio driver using Homebrew:

brew install blackhole-2ch

This enables audio loopback, allowing your system audio to be captured and analyzed in real-time.

### 2. Install Python Dependencies

Make sure you have Python 3.8+ installed, then install the required packages:

pip install bleak  
pip install numpy  
pip install matplotlib  
pip install sounddevice

### 3. Configure Audio Output (macOS Only)

To route system audio through BlackHole **and still hear it** through your speakers or headphones:

1. Open **Audio MIDI Setup** (found in `/Applications/Utilities/`)
2. Click the **`+`** button and choose **"Create Multi-Output Device"**
3. In the right panel, check:
   - ✅ **BlackHole 2ch**
   - ✅ Your actual output device (e.g., MacBook Speakers, Headphones, etc.)
4. Set the **Multi-Output Device** as the system output in **System Settings > Sound**

You’re now ready to run the system! It will listen to your music and react with lights accordingly 🎵💡

## Thank You

Special thanks to **Akashcraft** for reverse engieering the bluetooth protocol for these type of lights. Your contributions helped light the way — literally. 
