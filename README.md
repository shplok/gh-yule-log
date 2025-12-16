# gh-yule-log

A tiny [GitHub CLI](https://cli.github.com/) extension that turns your terminal into a festive, animated Yule log using a classic `curses` fire effect.

## Requirements

- `gh` (GitHub CLI) installed and configured
- `python3` available in your `PATH`
- A terminal that supports ANSI colors and `curses`

On macOS you will typically also need to run this in a real terminal (Terminal.app, iTerm2, etc.), not inside an IDE-integrated pseudo-terminal that might not fully support `curses`.

## Installation

From the directory containing this repository (for local development):

```bash
gh extension install .
```

Or from GitHub (once this repo is pushed, replace the owner as needed):

```bash
gh extension install <your-user-or-org>/gh-yule-log
```

## Usage

Run the extension with:

```bash
gh yule-log
```

- Your terminal will fill with a flickering, colored fire effect.
- Press any key to exit.

## How it works

- The `gh-yule-log` executable is the GitHub CLI extension entrypoint.
- It simply invokes `python3 fire.py`, which uses the Python `curses` module to:
  - Draw colored characters across the full screen.
  - Simulate heat propagation upward from the bottom row.
  - Continuously update the display until you press a key.
