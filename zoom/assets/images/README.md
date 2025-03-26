# Custom Images for NPQG Universe Zoom Animation

This directory contains the custom images used in the NPQG Universe Zoom Animation.

## Directory Structure

Images should be placed in the appropriate subdirectory based on the scale they represent:

- `universe/` - Images for the Universe scale (10^26 m)
- `galaxy_cluster/` - Images for the Galaxy Cluster scale (10^23 m)
- `galaxy/` - Images for the Galaxy scale (10^21 m)
- `black_hole/` - Images for the Black Hole scale (10^12 m)
- `solar_system/` - Images for the Solar System scale (10^11 m)
- `star/` - Images for the Star scale (10^9 m)
- `molecule/` - Images for the Molecule scale (10^-8 m)
- `atom/` - Images for the Atom scale (10^-10 m)
- `electron/` - Images for the Electron scale (10^-15 m)
- `quark/` - Images for the Quark scale (10^-18 m)
- `point_potential/` - Images for the Point Potential scale (10^-60 m)

## Image Requirements

- Supported formats: PNG, JPG, JPEG, SVG
- Square images work best (to fit properly within circles)
- Transparent backgrounds (PNG with alpha channel) are recommended
- Higher resolutions provide better results during animation

## How to Use

1. Place your custom images in the appropriate subdirectory
2. Images will be automatically detected and used by the animation
3. If multiple images are available in a directory, the first one will be used by default
4. The animation will automatically scale and fit your images to the appropriate size

## Configuration

You can enable or disable custom images by setting the `use_custom_images` option in the `global_settings` section of `zoom_config.json`:

```json
"global_settings": {
  "use_custom_images": true
}
```

Set to `false` to use only the programmatically generated visualizations.