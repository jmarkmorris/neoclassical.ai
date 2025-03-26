"""
Configuration loader for NPQG Universe Zoom Animation
Handles loading and validating JSON configuration files
"""

import json
import os

class ConfigLoader:
    """Loads and validates JSON configuration files"""
    
    def __init__(self, config_path):
        """
        Initialize the config loader with a path to a JSON file
        
        Args:
            config_path (str): Path to the JSON configuration file
        """
        self.config_path = config_path
        
    def load(self):
        """
        Load and validate the configuration file
        
        Returns:
            dict: The validated configuration data
        
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the configuration file is not valid JSON
            ValueError: If the configuration data is missing required keys
        """
        # Convert relative path to absolute path if needed
        if not os.path.isabs(self.config_path):
            self.config_path = os.path.abspath(self.config_path)
            
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        print(f"Loading configuration from: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"Invalid JSON in configuration file: {self.config_path}", 
                    e.doc, 
                    e.pos
                )
        
        # Process file paths in the config (make them absolute)
        config = self._resolve_paths(config)
        
        self._validate_config(config)
        return config
        
    def _resolve_paths(self, config):
        """
        Resolve relative paths in the configuration to absolute paths
        
        Args:
            config (dict): The configuration data
            
        Returns:
            dict: Configuration with resolved paths
        """
        # Get the base directory (directory containing the config file)
        base_dir = os.path.dirname(self.config_path)
        
        # Process audio paths if they exist
        if "audio" in config and config["audio"]:
            # Background music
            if "background_music" in config["audio"] and config["audio"]["background_music"]:
                bg_music = config["audio"]["background_music"]
                if not os.path.isabs(bg_music):
                    config["audio"]["background_music"] = os.path.join(base_dir, bg_music)
            
            # Narration files
            if "narration_timings" in config["audio"]:
                for i, cue in enumerate(config["audio"]["narration_timings"]):
                    if "audio_file" in cue and cue["audio_file"]:
                        audio_file = cue["audio_file"]
                        if not os.path.isabs(audio_file):
                            config["audio"]["narration_timings"][i]["audio_file"] = os.path.join(base_dir, audio_file)
        
        return config
    
    def _validate_config(self, config):
        """
        Validate the configuration data
        
        Args:
            config (dict): The configuration data to validate
            
        Raises:
            ValueError: If the configuration data is missing required keys or has invalid values
        """
        # Check required top-level keys
        required_keys = ["global_settings", "scenes", "animation_sequence"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required key in config: {key}")
        
        # Validate global settings
        self._validate_global_settings(config["global_settings"])
        
        # Validate scenes
        self._validate_scenes(config["scenes"])
        
        # Validate animation sequence
        self._validate_animation_sequence(config["animation_sequence"], config["scenes"])
    
    def _validate_global_settings(self, settings):
        """Validate global settings section"""
        required_settings = ["default_zoom_rate", "background_color", "scale_range"]
        for setting in required_settings:
            if setting not in settings:
                raise ValueError(f"Missing required global setting: {setting}")
        
        # Validate scale range
        if len(settings["scale_range"]) != 2:
            raise ValueError("Scale range must be a list of two numbers [min, max]")
        
        # Validate numeric values
        if not isinstance(settings["default_zoom_rate"], (int, float)) or settings["default_zoom_rate"] <= 0:
            raise ValueError("default_zoom_rate must be a positive number")
    
    def _validate_scenes(self, scenes):
        """Validate scenes section"""
        if not scenes or not isinstance(scenes, list):
            raise ValueError("Scenes must be a non-empty list")
        
        scene_names = set()
        for scene in scenes:
            # Check required scene keys
            if "name" not in scene:
                raise ValueError("Each scene must have a name")
            
            if "scale" not in scene:
                raise ValueError(f"Scene {scene['name']} is missing a scale value")
            
            if "objects" not in scene or not isinstance(scene["objects"], list):
                raise ValueError(f"Scene {scene['name']} must have an objects list")
            
            # Check for duplicate scene names
            if scene["name"] in scene_names:
                raise ValueError(f"Duplicate scene name: {scene['name']}")
            
            scene_names.add(scene["name"])
            
            # Validate objects
            for obj in scene["objects"]:
                if "label" not in obj:
                    raise ValueError(f"Object in scene {scene['name']} is missing a label")
                
                if "position" not in obj:
                    raise ValueError(f"Object '{obj.get('label', 'unnamed')}' in scene {scene['name']} is missing a position")
                
                if "radius" not in obj:
                    raise ValueError(f"Object '{obj.get('label', 'unnamed')}' in scene {scene['name']} is missing a radius")
    
    def _validate_animation_sequence(self, sequence, scenes):
        """Validate animation sequence section"""
        if not sequence or not isinstance(sequence, list):
            raise ValueError("Animation sequence must be a non-empty list")
        
        # Create a set of scene names for quick lookup
        scene_names = {scene["name"] for scene in scenes}
        
        prev_to_scene = None
        
        for i, transition in enumerate(sequence):
            # Check required transition keys
            if "from_scene" not in transition:
                raise ValueError(f"Transition {i} is missing a from_scene")
            
            if "to_scene" not in transition:
                raise ValueError(f"Transition {i} is missing a to_scene")
            
            if "direction" not in transition:
                raise ValueError(f"Transition {i} is missing a direction")
            
            # Check that scenes exist
            if transition["from_scene"] not in scene_names:
                raise ValueError(f"Transition {i} references unknown from_scene: {transition['from_scene']}")
            
            if transition["to_scene"] not in scene_names:
                raise ValueError(f"Transition {i} references unknown to_scene: {transition['to_scene']}")
            
            # Check direction value
            if transition["direction"] not in ["in", "out"]:
                raise ValueError(f"Transition {i} has invalid direction: {transition['direction']}. Must be 'in' or 'out'")
            
            # Check sequence continuity (transitions should connect)
            if i > 0 and transition["from_scene"] != prev_to_scene:
                raise ValueError(
                    f"Transition sequence discontinuity: Transition {i-1} ends at '{prev_to_scene}' "
                    f"but Transition {i} starts from '{transition['from_scene']}'"
                )
            
            prev_to_scene = transition["to_scene"]