# Shard/Heat Tracker Web App

**Status**: In Progress  
**Purpose**: Interactive JavaScript app for tracking in-game resources  
**Tech Stack**: React + TypeScript + Vite + TailwindCSS

## Overview

A small, focused web application for tracking game state during Hubworld: Aidalon matches. Useful for players to quickly reference costs and manage resources like shards and heat.

## Features

- **Shard Pool Tracking**: Track available shards with increment/decrement controls
- **Heat Tracking**: Monitor heat accumulation with color-coded indicators
- **Network Count Tracking**: Track network count during gameplay
- **Dark Mode Support**: Automatic dark mode based on system preferences
- **Responsive Design**: Works on desktop and mobile devices

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

- **React**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Lucide React**: Icon library

## Project Structure

```
web_app/
├── src/
│   ├── components/
│   │   ├── ShardTracker.tsx    # Shard pool tracking component
│   │   ├── HeatTracker.tsx     # Heat tracking component
│   │   └── NetworkTracker.tsx  # Network count tracking component
│   ├── services/
│   │   └── utils.ts            # Utility functions (cn helper)
│   ├── App.tsx                 # Main application component
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles with Tailwind
├── public/                     # Static assets
├── package.json                # Dependencies and scripts
├── tailwind.config.js          # Tailwind configuration
└── vite.config.ts              # Vite configuration
```

## Component Usage

### ShardTracker
Tracks the available shard pool with increment/decrement buttons and reset functionality.

### HeatTracker
Monitors heat accumulation with color-coded display (yellow → orange → red based on heat level).

### NetworkTracker
Tracks network count during gameplay with increment/decrement controls.

## Future Enhancements

- Multiplayer/session support
- Deck composition view
- In-game timer/turn tracking
- Card reference popup with quick info
- Local storage for persisting game state
- Export/import game state

## Dependencies

This module is standalone and does not depend on other modules in the repository.

## See Also

- [Main README](../README.md) - Project overview
- [Planning Doc](../Planning%20Doc.md) - Comprehensive roadmap
