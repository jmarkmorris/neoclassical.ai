# neoclassical.ai three.js prototype

Minimal labeled-sphere prototype with S-curve zoom and drag pan.

## Run locally
Use a local web server so ES modules load correctly.

```bash
cd viz3d/prototype
python3 -m http.server 5173
```

Then open `http://localhost:5173/`.

## Controls
- Click/tap a sphere to descend into its contents.
- Pinch in/out to zoom (trackpad pinch supported).
- Drag to pan.

## Deployed to GitHub Pages
This app is published as the Pages root at `https://jmarkmorris.github.io/neoclassical.ai/`.

If I free up the neoclassical.ai domain from wordpress github can also use that url.

### Refresh deployed webapp from the viz3d/prototype with a tested snapshot to `/docs` 
From the repo root:

```bash
mkdir -p docs
rsync -a --delete viz3d/prototype/ docs/
```
I then need to go to github and promote depot to main.

Commit and push. In GitHub repo settings → Pages, set Source to `main` and Folder to `/docs`.

