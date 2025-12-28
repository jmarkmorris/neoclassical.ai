# viz3d three.js prototype

Minimal labeled-sphere prototype with S-curve zoom and drag pan.

## Run locally
Use a local web server so ES modules load correctly.

```bash
cd viz3d/prototype
python3 -m http.server 5173
```

Then open `http://localhost:5173/`.

## Controls
- Double tap a sphere to descend into its contents.
- Pinch to zoom (trackpad pinch supported, auto-warp near objects).
- Drag to pan.
