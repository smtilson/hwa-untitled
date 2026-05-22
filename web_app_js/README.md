# HWA Tracker - Vanilla JS Version

**Status**: In Progress
**Purpose**: Static (no-build) version of the Shard/Heat Tracker for easy GitHub Pages hosting
**Tech Stack**: HTML + CSS + Vanilla JavaScript

## Overview

A no-build version of the Hubworld: Aidalon resource tracker. Mirrors the functionality of [`web_app_react`](../web_app_react/) but uses only HTML, CSS, and vanilla JavaScript so it can be served as a fully static site (e.g. GitHub Pages) with no toolchain.

## Features

- **Heat Tracking**: +/- controls (default: 0)
- **Shard Pool Tracking**: +/- controls (default: 5)
- **Reset Button**: Restore both trackers to default values
- **Reusable `createTracker` factory**: Generic label/value/+/- component used for both trackers
- **Dark Mode Support**: Automatic via `prefers-color-scheme`

## File Structure

```
web_app_js/
├── index.html      # Page markup, includes scripts and styles
├── styles.css      # All styling (uses CSS variables for theming)
├── tracker.js      # Reusable createTracker() factory
├── app.js          # App entry: instantiates trackers + wires reset
└── README.md
```

## Running Locally

Just open `index.html` in a browser:

```bash
xdg-open index.html        # Linux
open index.html            # macOS
start index.html           # Windows
```

Or serve it with any static server, e.g.:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000/web_app_js/
```

## Deploying to GitHub Pages

Because there is no build step, you can host the contents of this folder directly:

1. Push the repo to GitHub.
2. In repo Settings → Pages, choose the branch and set the folder to `/web_app_js`.
3. The site will be served at `https://<user>.github.io/<repo>/`.

## Component: `createTracker(options)`

Factory that returns a tracker control.

**Options:**

- `label: string` - Display label (e.g. `"Heat"`)
- `value: number` - Initial value
- `onChange?: (newValue: number) => void` - Called whenever the value changes
- `min?: number` - Minimum value (default `0`)

**Returns:**

- `element: HTMLElement` - The root DOM node to append
- `getValue(): number` - Read current value
- `setValue(v: number): void` - Programmatically set value (used by Reset)

## Customizing the Look

Search for `blech` in `styles.css` to find the dimensions and colors that are most likely to want tweaking (box size, button size, colors, etc.).

## See Also

- [`web_app_react/`](../web_app_react/) - React/TypeScript version
- [Main README](../README.md) - Project overview
- [Planning Doc](../Planning%20Doc.md) - Roadmap
