# OpenDataLoader Isolated Install Report

- Environment: `tools/opendataloader_env`, Python 3.12, OpenJDK 17.0.19.
- Version: OpenDataLoader PDF 2.5.0, released wheel 22.6 MB.
- Strategy: create venv → upgrade pip tooling → `pip download --no-deps` → offline `pip install --no-index --no-deps`.
- Import smoke: passed.
- One-PDF conversion: 4.53s, JSON 226,254 bytes, Markdown 102,763 bytes plus images.
- Five-PDF batch: 25.80s, all JSON/Markdown outputs produced.

This avoids dependency resolution stalls that caused prior 304s timeouts and does not modify the primary WAVE environment. Wheel remains in the isolated wheelhouse as the versioned install input.
