# Contributing

Thank you for helping improve FuProfile Unlocker.

## Before opening an issue

- Use only RAW files that you have the right to share.
- Do not upload Adobe DCP files, Lightroom application files, API keys, or private photographs.
- Check the verified-camera list and existing issues first. A model being absent does not by
  itself mean that it is incompatible.
- For a camera compatibility report, include the exact Make, Model, file extension, operating
  system, and Lightroom/Camera Raw version. A public sample link is optional.

## Development setup

FuProfile Unlocker requires Python 3.11 or newer. Install the project in a virtual environment:

```sh
python -m venv .venv
python -m pip install -e .
```

ExifTool and the platform dcpTool binary are required for end-to-end profile generation. See
`WINDOWS_BUILD_CN.md` or `MACOS_BUILD_CN.md` for platform-specific setup.

Run the unit tests before submitting a change:

```sh
python -m unittest discover -s tests -v
```

## Pull requests

- Keep shared behavior in the common Python code; avoid separate Windows and macOS forks.
- Add or update tests for behavior changes.
- Do not add RAW binaries, generated DCP files, build output, release archives, or Adobe profiles.
- Preserve third-party attribution and license boundaries described in `THIRD_PARTY_NOTICES.md`.
- Explain user-visible changes and the validation performed.
