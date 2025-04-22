#!/usr/bin/env .venv/bin/python
import pyboy
from pyboy.utils import WindowEvent
import time
import os
import numpy as np
import wave
import cv2
import subprocess
import shutil
import json

def test_screen_recorder_with_sound():
    """
    Test for the screen recorder with sound support (Issue #368).
    Creates a video file with mp4 with sound from GameBoy gameplay.
    """
    print("\n=== Screen Recorder with Sound Test (Issue #368) ===")
    print("This test records both video and audio from a GameBoy game.")
    print("We'll record Tetris gameplay with its sound effects.\n")
    
    # Initialize PyBoy with a ROM that produces sound
    #This is hardcoded and needs to be updated, or changed each use.
    rom_path = "roms/Wario Land - Super Mario Land 3 (World).gb"
    print(f"1. Loading ROM: {rom_path}")
    print("   Enabling sound and screen recording...")
    
    # Define keybinds for the emulator as a JSON string
    keybinds = json.dumps({
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
        "a": "a",
        "b": "s",
        "start": "return",
        "select": "backspace"
    })
    # creates a new instance of the emulator, enables sound emulation, pauses for one second
    pyboy_instance = pyboy.PyBoy(rom_path, sound_emulated=True, keybinds=keybinds)
    time.sleep(1)
    


    # Create output directory if it doesn't exist, if it does, it deleted it and creates a new directory
    output_dir = "test_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # Initialize arrays to store frames and audio samples
    frames = []
    all_left_samples = []
    all_right_samples = []
    
    # Get sample rate for audio
    sample_rate = pyboy_instance.sound.sample_rate
    
    # Start the game by simulating the start button for gamelauncher
    print("\n2. Starting game sequence and recording...")
    pyboy_instance.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy_instance.tick()
    pyboy_instance.send_input(WindowEvent.RELEASE_BUTTON_START)
    pyboy_instance.tick()
    pyboy_instance.send_input(WindowEvent.PRESS_BUTTON_A)
    pyboy_instance.tick()
    pyboy_instance.send_input(WindowEvent.RELEASE_BUTTON_A)
    pyboy_instance.tick()
    
    # Record for 5 seconds (300 frames at 60fps)
    for frame in range(300):
        # Tick the emulator
        pyboy_instance.tick()
        
        # Capture the screen and convert to RGB to compile frames into a video format
        screen = pyboy_instance.screen.ndarray
        rgb_frame = cv2.cvtColor(screen, cv2.COLOR_RGBA2RGB)
        frames.append(rgb_frame)
        
        # Get audio samples for left and right channels
        audio_samples = pyboy_instance.sound.ndarray
        left_channel = audio_samples[:, 0]
        right_channel = audio_samples[:, 1]
        all_left_samples.extend(left_channel)
        all_right_samples.extend(right_channel)
        
        # Show progress to user
        if frame % 60 == 0:
            print(f"   Recording... {frame//60}/5 seconds")
    
    # Stop the emulator
    pyboy_instance.stop()
    
    print("\n3. Creating video file with sound...")
    
    #  create the video file
    video_file = os.path.join(output_dir, "gameplay.mp4")
    temp_video = os.path.join(output_dir, "temp_video.mp4")
    
    # Initialize video writer to make the mp4 video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, 60.0, (160, 144))
    
    # Write frames
    for frame in frames:
        out.write(frame)
    out.release()
    
    # Save audio to WAV
    audio_file = os.path.join(output_dir, "temp_audio.wav")
    


    #save audio by converting 8 bit to 16 bit audio. Creates a stereo stream with left and right samples into one single array
    scale = 32768 // 128  # Scale 8-bit to 16-bit
    left_samples = np.array(all_left_samples, dtype=np.int16) * scale
    right_samples = np.array(all_right_samples, dtype=np.int16) * scale
    
    stereo_samples = np.empty(len(left_samples) + len(right_samples), dtype=np.int16)
    stereo_samples[0::2] = left_samples
    stereo_samples[1::2] = right_samples
    

    # writes the processed audio data into a WAV file
    with wave.open(audio_file, 'wb') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo_samples.tobytes())
    


    # Combine video and audio using ffmpeg to create a synchronized mp4 with video and audio aligned
    cmd = [
        'ffmpeg', '-y',
        '-i', temp_video,
        '-i', audio_file,
        '-c:v', 'copy',
        '-c:a', 'aac',
        video_file
    ]
    subprocess.run(cmd, check=True)
    

    # deletes the temporary video file that had no audio and delets the wav file that was used for adding audio
    os.remove(temp_video)
    os.remove(audio_file)

    # prints success message and the mp4 file
    print(f"\n=== Test Complete ===")
    print(f"Created video file with sound: {os.path.abspath(video_file)}")

if __name__ == "__main__":
    test_screen_recorder_with_sound() 


