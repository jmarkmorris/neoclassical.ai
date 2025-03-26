"""
Audio Controller for NPQG Universe Zoom Animation
Handles background music and narration cues
"""

import os
from manim import *

class AudioController:
    """Controls audio playback for the animation"""
    
    def __init__(self, audio_config=None):
        """
        Initialize the audio controller
        
        Args:
            audio_config (dict, optional): Audio configuration from the JSON config
        """
        self.config = audio_config or {}
        self.background_music = self.config.get("background_music")
        self.volume = self.config.get("volume", 0.5)
        self.narration_cues = self.config.get("narration_timings", [])
        
        # Sort narration cues by timestamp
        if self.narration_cues:
            self.narration_cues.sort(key=lambda x: x["timestamp"])
        
        self.current_narration_index = 0
        self.sound_objects = []
    
    def start_background_music(self):
        """Start playing background music"""
        if not self.background_music:
            return
            
        if os.path.exists(self.background_music):
            # Create a sound object for the background music
            sound = self._get_sound_object(self.background_music, self.volume, loop=True)
            if sound:
                self.sound_objects.append(sound)
                sound.play()
                print(f"Playing background music: {self.background_music}")
        else:
            print(f"Warning: Background music file not found: {self.background_music}")
            # Create a directory for the audio files if it doesn't exist
            audio_dir = os.path.dirname(self.background_music)
            if not os.path.exists(audio_dir):
                try:
                    os.makedirs(audio_dir, exist_ok=True)
                    print(f"Created directory: {audio_dir}")
                except Exception as e:
                    print(f"Error creating directory {audio_dir}: {e}")
    
    def check_narration_cues(self, current_time):
        """
        Check if we need to play any narration cues at the current time
        
        Args:
            current_time (float): The current animation time in seconds
        """
        # Skip if no narration cues or already processed all cues
        if (not self.narration_cues or 
            self.current_narration_index >= len(self.narration_cues)):
            return
        
        # Check if we need to play any narration now
        while (self.current_narration_index < len(self.narration_cues) and 
               self.narration_cues[self.current_narration_index]["timestamp"] <= current_time):
            
            cue = self.narration_cues[self.current_narration_index]
            audio_file = cue["audio_file"]
            volume = cue.get("volume", self.volume)
            
            # Only try to play if the file exists
            if audio_file and os.path.exists(audio_file):
                self._play_narration(audio_file, volume)
            else:
                print(f"Warning: Narration audio file not found: {audio_file}")
                # Create the directory for narration files if it doesn't exist
                if audio_file:
                    narration_dir = os.path.dirname(audio_file)
                    if not os.path.exists(narration_dir):
                        try:
                            os.makedirs(narration_dir, exist_ok=True)
                            print(f"Created directory: {narration_dir}")
                        except Exception as e:
                            print(f"Error creating directory {narration_dir}: {e}")
            
            self.current_narration_index += 1
    
    def _play_narration(self, audio_file, volume):
        """
        Play a narration audio file
        
        Args:
            audio_file (str): Path to the audio file
            volume (float): Playback volume from 0.0 to 1.0
        """
        if os.path.exists(audio_file):
            # Create a sound object for the narration
            sound = self._get_sound_object(audio_file, volume)
            if sound:
                self.sound_objects.append(sound)
                sound.play()
                print(f"Playing narration: {audio_file}")
        else:
            print(f"Warning: Narration audio file not found: {audio_file}")
    
    def _get_sound_object(self, file_path, volume, loop=False):
        """
        Create a sound object for an audio file
        
        Args:
            file_path (str): Path to the audio file
            volume (float): Playback volume from 0.0 to 1.0
            loop (bool, optional): Whether to loop the audio
            
        Returns:
            object: A sound object or None if not supported
        """
        try:
            # Try to use the appropriate audio backend
            # Implementation depends on the environment
            print(f"Would create sound object for: {file_path} (volume: {volume}, loop: {loop})")
            
            # In a real implementation, this would return an actual sound object
            # For now, we return a dummy object to simulate the behavior
            return DummySoundObject(file_path, volume, loop)
        except Exception as e:
            print(f"Warning: Failed to create sound object: {e}")
            return None
    
    def stop_all(self):
        """Stop all audio playback"""
        for sound in self.sound_objects:
            sound.stop()
        self.sound_objects = []


class DummySoundObject:
    """Dummy sound object for testing"""
    
    def __init__(self, file_path, volume, loop):
        """Initialize the dummy sound object"""
        self.file_path = file_path
        self.volume = volume
        self.loop = loop
        self.playing = False
    
    def play(self):
        """Start playback"""
        self.playing = True
        print(f"Playing {self.file_path} at volume {self.volume}" +
              (" (looping)" if self.loop else ""))
    
    def stop(self):
        """Stop playback"""
        if self.playing:
            self.playing = False
            print(f"Stopped {self.file_path}")