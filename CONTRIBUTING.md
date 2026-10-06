# Contributing to Sys-Info

Sys-Info combines a Python collector with a Tauri/React desktop application.

## Validation

Collector:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Windows desktop build:

```powershell
npm ci --prefix gui
.\scripts\prepare_build.ps1
npm run build --prefix gui
cargo check --manifest-path gui/src-tauri/Cargo.toml
```

## Platform notes

- Windows is the primary/full desktop target.
- The Python collector is partially portable to Linux and macOS.
- Hardware details backed by CIM, PowerShell, Registry or Windows-specific commands must degrade gracefully on non-Windows systems.

Use sanitized system information in tests and issue reports.
