"""
Scale Converter for NPQG Universe Zoom Animation
Utilities for converting between different scale representations
"""

import numpy as np

# Define scale constants
PLANCK_LENGTH = 1.616255e-35  # meters
PLANCK_TIME = 5.391247e-44  # seconds
SPEED_OF_LIGHT = 299792458  # m/s

# Define scale ranges for different phenomena
SCALES = {
    "universe": {"min": 1e26, "max": 1e27, "unit": "m"},
    "galaxy_cluster": {"min": 1e22, "max": 1e24, "unit": "m"},
    "galaxy": {"min": 1e20, "max": 1e22, "unit": "m"},
    "solar_system": {"min": 1e10, "max": 1e13, "unit": "m"},
    "star": {"min": 1e8, "max": 1e10, "unit": "m"},
    "planet": {"min": 1e6, "max": 1e8, "unit": "m"},
    "mountain": {"min": 1e3, "max": 1e5, "unit": "m"},
    "human": {"min": 1e0, "max": 2e0, "unit": "m"},
    "cell": {"min": 1e-6, "max": 1e-4, "unit": "m"},
    "molecule": {"min": 1e-10, "max": 1e-8, "unit": "m"},
    "atom": {"min": 1e-11, "max": 1e-10, "unit": "m"},
    "nucleus": {"min": 1e-15, "max": 1e-14, "unit": "m"},
    "nucleon": {"min": 1e-15, "max": 1e-15, "unit": "m"},
    "quark": {"min": 1e-18, "max": 1e-16, "unit": "m"},
    "point_potential": {"min": 1e-60, "max": 1e-40, "unit": "m"}
}

def format_scale(scale_value, format_type="scientific"):
    """
    Format a scale value for display
    
    Args:
        scale_value (float): The scale value in meters
        format_type (str, optional): Format type ('scientific', 'power', or 'human')
        
    Returns:
        str: Formatted scale string
    """
    if format_type == "scientific":
        # Scientific notation (1.23e+20)
        return f"{scale_value:.2e}"
    
    elif format_type == "power":
        # Power of ten (10^20)
        power = int(np.floor(np.log10(scale_value)))
        return f"10^{power}"
    
    elif format_type == "human":
        # Human-readable with units
        scale_abs = abs(scale_value)
        
        if scale_abs >= 1e24:
            return f"{scale_abs/1e24:.2f} Yottameters"
        elif scale_abs >= 1e21:
            return f"{scale_abs/1e21:.2f} Zettameters"
        elif scale_abs >= 1e18:
            return f"{scale_abs/1e18:.2f} Exameters"
        elif scale_abs >= 1e15:
            return f"{scale_abs/1e15:.2f} Petameters"
        elif scale_abs >= 1e12:
            return f"{scale_abs/1e12:.2f} Terameters"
        elif scale_abs >= 1e9:
            return f"{scale_abs/1e9:.2f} Gigameters"
        elif scale_abs >= 1e6:
            return f"{scale_abs/1e6:.2f} Megameters"
        elif scale_abs >= 1e3:
            return f"{scale_abs/1e3:.2f} Kilometers"
        elif scale_abs >= 1:
            return f"{scale_abs:.2f} Meters"
        elif scale_abs >= 1e-2:
            return f"{scale_abs*1e2:.2f} Centimeters"
        elif scale_abs >= 1e-3:
            return f"{scale_abs*1e3:.2f} Millimeters"
        elif scale_abs >= 1e-6:
            return f"{scale_abs*1e6:.2f} Micrometers"
        elif scale_abs >= 1e-9:
            return f"{scale_abs*1e9:.2f} Nanometers"
        elif scale_abs >= 1e-12:
            return f"{scale_abs*1e12:.2f} Picometers"
        elif scale_abs >= 1e-15:
            return f"{scale_abs*1e15:.2f} Femtometers"
        elif scale_abs >= 1e-18:
            return f"{scale_abs*1e18:.2f} Attometers"
        elif scale_abs >= 1e-21:
            return f"{scale_abs*1e21:.2f} Zeptometers"
        elif scale_abs >= 1e-24:
            return f"{scale_abs*1e24:.2f} Yoctometers"
        else:
            # Very small scales in terms of Planck length
            planck_units = scale_abs / PLANCK_LENGTH
            return f"{planck_units:.2f} Planck lengths"
    
    else:
        raise ValueError(f"Unknown format type: {format_type}")

def get_scale_name(scale_value):
    """
    Get the name of the scale level for a given value
    
    Args:
        scale_value (float): The scale value in meters
        
    Returns:
        str: Name of the closest scale level
    """
    scale_abs = abs(scale_value)
    closest_scale = None
    min_distance = float('inf')
    
    for scale_name, scale_info in SCALES.items():
        # Check if the value is within the scale range
        if scale_info["min"] <= scale_abs <= scale_info["max"]:
            return scale_name
        
        # Otherwise find the closest scale
        min_dist = min(abs(np.log10(scale_abs) - np.log10(scale_info["min"])),
                      abs(np.log10(scale_abs) - np.log10(scale_info["max"])))
        
        if min_dist < min_distance:
            min_distance = min_dist
            closest_scale = scale_name
    
    return closest_scale

def calculate_zoom_factor(start_scale, end_scale, seconds, frames_per_second=60):
    """
    Calculate the per-frame zoom factor for smooth animation
    
    Args:
        start_scale (float): Starting scale in meters
        end_scale (float): Ending scale in meters
        seconds (float): Duration of the zoom animation in seconds
        frames_per_second (int, optional): Animation frame rate
        
    Returns:
        float: Per-frame zoom factor (multiply camera scale by this value each frame)
    """
    # Calculate the total number of frames
    total_frames = seconds * frames_per_second
    
    # Calculate the logarithmic scale difference
    log_start = np.log10(start_scale)
    log_end = np.log10(end_scale)
    log_diff = log_end - log_start
    
    # Calculate the per-frame zoom factor
    # This ensures exponential zooming that appears uniform
    return 10**(log_diff / total_frames)

def get_physical_constants_for_scale(scale_value):
    """
    Get relevant physical constants and phenomena for a given scale
    
    Args:
        scale_value (float): The scale value in meters
        
    Returns:
        dict: Dictionary of relevant physical constants and phenomena
    """
    scale_abs = abs(scale_value)
    constants = {}
    
    # Universe scale (10^26)
    if scale_abs >= 1e25:
        constants["Observable Universe Diameter"] = "93 billion light years"
        constants["Age of Universe"] = "13.8 billion years"
        constants["Cosmic Microwave Background"] = "2.7 K"
    
    # Galaxy Cluster scale (10^23)
    elif scale_abs >= 1e22:
        constants["Typical Galaxy Cluster Size"] = "5-30 million light years"
        constants["Galaxy Cluster Mass"] = "10^14-10^15 solar masses"
        constants["Intracluster Medium Temperature"] = "10^7-10^8 K"
    
    # Galaxy scale (10^21)
    elif scale_abs >= 1e20:
        constants["Milky Way Diameter"] = "100,000 light years"
        constants["Milky Way Mass"] = "1-1.5 trillion solar masses"
        constants["Galactic Rotation Period"] = "225-250 million years"
    
    # Solar System scale (10^11)
    elif scale_abs >= 1e10:
        constants["Solar System Diameter"] = "~9 billion km"
        constants["Earth-Sun Distance"] = "1 AU (149.6 million km)"
        constants["Speed of Light"] = "299,792,458 m/s"
    
    # Star scale (10^9)
    elif scale_abs >= 1e8:
        constants["Sun Diameter"] = "1,392,700 km"
        constants["Sun Mass"] = "1.989 × 10^30 kg"
        constants["Sun Surface Temperature"] = "5,778 K"
    
    # Molecular scale (10^-9)
    elif scale_abs >= 1e-10:
        constants["DNA Double Helix Diameter"] = "2 nm"
        constants["Water Molecule Size"] = "~0.3 nm"
        constants["Van der Waals Forces"] = "~10^-11 N"
    
    # Atomic scale (10^-10)
    elif scale_abs >= 1e-11:
        constants["Hydrogen Atom Diameter"] = "~0.1 nm"
        constants["Bohr Radius"] = "5.29 × 10^-11 m"
        constants["Ionization Energy of Hydrogen"] = "13.6 eV"
    
    # Nuclear scale (10^-15)
    elif scale_abs >= 1e-14:
        constants["Proton Diameter"] = "~1.75 fm"
        constants["Nuclear Binding Energy"] = "~1-8 MeV per nucleon"
        constants["Strong Force Range"] = "~1-3 fm"
    
    # Quark scale (10^-18)
    elif scale_abs >= 1e-18:
        constants["Quark Size"] = "< 10^-18 m"
        constants["Quark Confinement Energy"] = "~200 MeV"
        constants["QCD Coupling Constant"] = "~0.1"
    
    # Point potential scale (10^-40 to 10^-60)
    else:
        constants["Planck Length"] = "1.616 × 10^-35 m"
        constants["Planck Time"] = "5.391 × 10^-44 s"
        constants["Planck Energy"] = "1.956 × 10^9 J"
    
    return constants