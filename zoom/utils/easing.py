"""
Easing functions for animation transitions
Provides various easing equations for smoother animations
"""

import numpy as np

def linear(t):
    """
    Linear easing function (no easing)
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Output value (same as input for linear)
    """
    return t

def smooth_step(t):
    """
    Smooth step function using 3t² - 2t³
    Provides a smooth acceleration and deceleration
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Smoothed value between 0.0 and 1.0
    """
    return 3 * t**2 - 2 * t**3

def smoother_step(t):
    """
    Smoother step function using 6t⁵ - 15t⁴ + 10t³
    Provides an even smoother acceleration and deceleration
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Smoothed value between 0.0 and 1.0
    """
    return 6 * t**5 - 15 * t**4 + 10 * t**3

def ease_in_quad(t):
    """
    Quadratic ease-in function
    Accelerates slowly at first, then faster
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Eased value between 0.0 and 1.0
    """
    return t**2

def ease_out_quad(t):
    """
    Quadratic ease-out function
    Starts fast, then decelerates
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Eased value between 0.0 and 1.0
    """
    return 1 - (1 - t)**2

def ease_in_out_quad(t):
    """
    Quadratic ease-in-out function
    Accelerates, then decelerates
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Eased value between 0.0 and 1.0
    """
    if t < 0.5:
        return 2 * t**2
    return 1 - 2 * (1 - t)**2

def ease_in_cubic(t):
    """
    Cubic ease-in function
    Accelerates even more slowly at first
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Eased value between 0.0 and 1.0
    """
    return t**3

def ease_out_cubic(t):
    """
    Cubic ease-out function
    Starts even faster, then decelerates more gradually
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Eased value between 0.0 and 1.0
    """
    return 1 - (1 - t)**3

def ease_in_out_cubic(t):
    """
    Cubic ease-in-out function
    Smoother acceleration and deceleration than quadratic
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Eased value between 0.0 and 1.0
    """
    if t < 0.5:
        return 4 * t**3
    return 1 - 4 * (1 - t)**3

def ease_in_exp(t):
    """
    Exponential ease-in function
    Very slow start, then rapid acceleration
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Eased value between 0.0 and 1.0
    """
    if t == 0:
        return 0
    return 2**(10 * (t - 1))

def ease_out_exp(t):
    """
    Exponential ease-out function
    Very fast start, then rapid deceleration
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Eased value between 0.0 and 1.0
    """
    if t == 1:
        return 1
    return 1 - 2**(-10 * t)

def ease_in_out_exp(t):
    """
    Exponential ease-in-out function
    Slow start, rapid middle, slow end
    
    Args:
        t (float): Progress from 0.0 to 1.0
        
    Returns:
        float: Eased value between 0.0 and 1.0
    """
    if t == 0 or t == 1:
        return t
    
    if t < 0.5:
        return 0.5 * 2**(20 * t - 10)
    return 0.5 * (2 - 2**(-20 * t + 10))

def get_easing_function(name):
    """
    Get an easing function by name
    
    Args:
        name (str): Name of the easing function
        
    Returns:
        function: The easing function
        
    Raises:
        ValueError: If the easing function is not found
    """
    easing_functions = {
        "linear": linear,
        "smooth": smooth_step,
        "smoother": smoother_step,
        "ease_in": ease_in_quad,
        "ease_out": ease_out_quad,
        "ease_in_out": ease_in_out_quad,
        "ease_in_quad": ease_in_quad,
        "ease_out_quad": ease_out_quad,
        "ease_in_out_quad": ease_in_out_quad,
        "ease_in_cubic": ease_in_cubic,
        "ease_out_cubic": ease_out_cubic,
        "ease_in_out_cubic": ease_in_out_cubic,
        "ease_in_exp": ease_in_exp,
        "ease_out_exp": ease_out_exp,
        "ease_in_out_exp": ease_in_out_exp,
        "accelerate": ease_in_quad,
        "decelerate": ease_out_quad
    }
    
    if name not in easing_functions:
        raise ValueError(f"Unknown easing function: {name}")
    
    return easing_functions[name]