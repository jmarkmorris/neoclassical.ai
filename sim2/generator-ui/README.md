# Generator UI (Prototype)

This is a minimal generator UI + backend for building sim2 run files.

## Run

```bash
python sim2/generator-ui/server.py --port 8000
```

Open `http://127.0.0.1:8000` in a browser.

## What it does

- Loads a base run file from `sim2/json/`.
- Generates new `architrinos` with the selected distributions.
- Shows a live preview on a canvas facsimile.
- Saves a generated JSON file back to `sim2/json/`.

## Notes

- Generation is deterministic with the chosen seed.
- The backend uses only the Python standard library.
- Output files are written to `sim2/json/` with the provided name.

