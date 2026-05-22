# Shard/Heat Tracker Web App

**Status**: In Progress  
**Purpose**: Interactive JavaScript app for tracking in-game resources  
**Tech Stack**: React + TypeScript + Vite + TailwindCSS

## Overview

A small, focused web application for tracking game state during Hubworld: Aidalon matches. Useful for players to quickly reference costs and manage resources like shards and heat.

## Features

- **Heat Tracking**: Track heat accumulation with +/- controls (default: 0)
- **Shard Pool Tracking**: Track available shards with +/- controls (default: 5)
- **Reset Button**: Restore both trackers to default values
- **Reusable `Tracker` component**: Generic label/value/+/- component used for both trackers
- **Dark Mode Support**: Automatic dark mode based on system preferences

### Planned

- Network count tracking
- Quick reference card info popup
- Local storage / state persistence
- Multiplayer/session support

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

```bash
# Navigate to the web_app directory
cd web_app

# Install dependencies
npm install
```

### Development

```bash
# Start the development server
npm run dev
```

The app will be available at `http://localhost:5173/`

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Tech Stack

- **React 19** + **TypeScript**
- **Vite** - build tool and dev server
- **TailwindCSS v4** - utility-first CSS (uses `@import "tailwindcss"` syntax)
- **Lucide React** - icon library

## Project Structure

```
web_app/
├── src/
│   ├── components/
│   │   └── Tracker.tsx         # Reusable label/value/+/- tracker component
│   ├── services/
│   │   └── utils.ts            # cn() helper (clsx + tailwind-merge)
│   ├── App.tsx                 # Main app: heat + shard trackers + reset
│   ├── main.tsx                # Application entry point
│   └── index.css               # Tailwind import + minimal globals
├── public/                     # Static assets
├── wireframes/                 # Layout wireframes (.drawio)
├── postcss.config.js           # PostCSS config (uses @tailwindcss/postcss)
├── package.json
└── vite.config.ts              # Vite config (polling enabled for WSL)
```

## Component: `Tracker`

Generic, reusable tracker component used for both Heat and Shards.

**Props:**

- `label: string` - Display label (e.g. "Heat", "Shards")
- `value: number` - Current value
- `onIncrement: () => void` - Handler for + button
- `onDecrement: () => void` - Handler for - button
- `className?: string` - Optional additional classes

State for the tracked values lives in `App.tsx`, along with default values (`DEFAULT_HEAT = 0`, `DEFAULT_SHARDS = 5`) and the `reset()` handler.

## Notes

- Tailwind v4: configuration via CSS (`@import "tailwindcss"`), not `tailwind.config.js`. The legacy config file is currently unused.
- `vite.config.ts` enables `usePolling` to make HMR work reliably on WSL when the project lives on a Windows-mounted drive.

## Future Enhancements

- Network count tracking
- Multi-player support (track resources for multiple players)
- Card reference popup with quick info
- In-game timer/turn tracking
- Deck composition view
- Local storage for persisting game state
- Multiplayer/session support

## Dependencies

This module is standalone and does not depend on other modules in the repository.

## See Also

- [Main README](../README.md) - Project overview
- [Planning Doc](../Planning%20Doc.md) - Comprehensive roadmap
