# imWEBs Desktop App

This folder contains a standalone desktop UI for creating `imWEBs` model and scenario config files and running the existing Python workflow directly.

## Why this shape

The UI calls the library in-process instead of using shell commands or a local web server. That keeps packaging and error handling simple and lets the app stream Python log output directly into the window.

## What is included

- A PySide6 wizard-style desktop window with domain steps: Project Location, imWEBs Structure, Delineation and Rotation, BMP, Model Config Workflows, and Scenarios
- Background-managed config files (users only edit fields in the UI)
- Background execution for long-running model generation steps
- A thin service layer that writes config files and calls the `imWEBs` library API

## Run from source

From the repository root:

```powershell
pip install -e .
pip install -e .\desktop_app
imwebs-desktop
```

If you do not want to install the desktop app package, you can also run:

```powershell
python -m desktop_app.imwebs_desktop
```

## Packaging direction

This repository includes a Windows packaging workflow so end users do not need Python.

### Build a standalone app and installer

From the repository root:

```powershell
cd .\desktop_app
.\packaging\build_windows_installer.ps1 -AppVersion 0.1.0
```

Outputs:

- Standalone folder: `desktop_app\dist\imWEBs-Desktop\`
- Installer EXE (if Inno Setup is installed): `desktop_app\dist\installer\imwebs-desktop-<version>-setup.exe`

Notes:

- The script bundles the Python runtime and dependencies using PyInstaller.
- If Inno Setup (`iscc`) is not installed, the standalone app is still produced.
- Install Inno Setup to generate the final click-through installer.

### In-app update hosting (recommended)

Use GitHub Releases as the installer host for the `Check Update` button.

Required release asset format:

- Attach a Windows installer `.exe` to each release.
- Name should include `setup` or `installer` (for example `imwebs-desktop-0.1.1-setup.exe`).

Recommended release flow:

1. Build installer with `packaging/build_windows_installer.ps1`.
2. Create tag `vX.Y.Z` in GitHub.
3. Create GitHub Release for that tag.
4. Upload the installer EXE as a release asset.

The desktop app checks:

- `https://api.github.com/repos/hawklorry/imWEBs-Python/releases/latest`

and downloads the installer asset when a newer version is available.

## Notes

- The app writes INI files in the background using the same section and key names as the existing library.
- Running the UI follows a six-step wizard and includes model workflows plus scenario generation directly in-step.
- Advancing through the wizard saves the current step and validates the configuration before moving forward.
- Users do not need to manage config file paths directly; the app handles those paths internally.
- The current UI is intentionally direct and close to the library surface. It is meant as a solid foundation, not a finished product design.
