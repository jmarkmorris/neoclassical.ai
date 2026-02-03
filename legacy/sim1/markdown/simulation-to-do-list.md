Based on a comparison between design.md and the codebase, here are the main features that haven't been fully implemented yet, as of Mar 24, 2025:

  Unimplemented Features

  1. Coordinate System Mapping Legend
    - Design specifies a legend showing scale (implemented), translational velocity, and camera orientation (theta/phi)
    - Only the scale factor is currently displayed
  2. Multiple Types of Tracers Simultaneously
    - Design mentions ability to have multiple types of tracers overlaid
    - Current implementation doesn't allow enabling both Line Tracers and Dot3D Tracers simultaneously
  3. Coordinate Translation Handling
    - Design specifies translation when simulation coordinates are offset from origin
    - Current implementation only handles scaling but not translation of coordinates
  4. Coordinate Rotation
    - Design discusses rotation when simulation coordinates are oriented differently
    - Not currently implemented in the visualization
  5. Camera Orientation Display
    - The camera angles (theta/phi) should be displayed but aren't shown in the visualization
  6. Complete Testing Framework
    - Design mentions testing and validation requirements
    - No formal testing framework is implemented

  Partially Implemented Features

  1. Automatic Scaling
    - Scaling exists but doesn't explicitly check if particles move outside display space
  2. Tracer Configuration
    - The tracer color options don't exactly match design's specification
    - Opacity variation for Dot3D tracers isn't precisely as specified
  3. Documentation
    - Default values aren't fully documented at the top of their respective files as specified
  4. Example Configuration
    - example_config.json exists but doesn't include all possible configuration options

  These could be areas for future enhancement if you'd like to make the implementation more aligned with the original design
  document.


  More: 
  
  - add lines of action to spiral
  - check out sim30.json -- odd behaviour
  - we have a v=0 issue on calculating action. What are we to do when v<1? Shouldn't the divisor approach 1 as v goes to 0?
  - need to revise action to consider velocity of receiver, both radial to the emission and orthogonal.