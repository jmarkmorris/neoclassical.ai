# Generator UI (Prototype)

This is a minimal generator UI + backend for building orbit-visualizer run files.

## Run

```bash
python orbit-visualizer/generator-ui/server.py --port 8000
```

Open `http://127.0.0.1:8000` in a browser.

## What it does

- Loads a base run file from `orbit-visualizer/json/`.
- Generates new `architrinos` with the selected distributions.
- Shows a live preview on a canvas facsimile.
- Saves a generated JSON file back to `orbit-visualizer/json/`.

## Notes

- Generation is deterministic with the chosen seed.
- The backend uses only the Python standard library.
- Output files are written to `orbit-visualizer/json/` with the provided name.

