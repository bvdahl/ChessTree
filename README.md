# Chess Tree Analyzer

A browser-based chess analysis tool that builds deep variation trees from any
position using the Stockfish engine. Everything runs **entirely in your browser** —
there's no backend, no account, and nothing to install on a server. Your positions
never leave your machine.

## What it does

- Analyze a position from a **PGN** game, a **FEN** string, or by **playing moves on
  the board**.
- Generate a tree of the strongest variations to a configurable depth, with
  per-side centipawn thresholds to control how many alternatives are explored.
- Browse the results in an interactive board and a navigable variation tree, with
  evaluations shown from White's perspective.
- Export your analysis as **PGN** (nested variations, compatible with ChessBase and
  other chess software) or **JSON**.
- Built-in **Help** guide and hover tooltips on every control.

## Running locally

Requires [Node.js](https://nodejs.org/) (18+).

```bash
npm install
npm run dev
```

Then open the URL printed in the terminal (Vite's dev server).

## Use your own engine (optional)

By default the app runs a copy of **Stockfish 16 inside your browser** — no setup,
works everywhere (including the published online version), but limited to a single
CPU core.

If you'd rather use a chess engine program you downloaded to your own computer (a
newer Stockfish, or a different UCI engine), you have two ways to do it. Either
way the engine runs only on your machine and can use all your CPU cores via the
*Engine threads* slider.

### Easiest: the desktop app

Build the installable Windows desktop app (see *Desktop app* below). In it, open
the **Engine** panel, choose **My own engine (local)**, click **Browse…**, and
pick your engine program (on Windows it ends in `.exe`). It connects
automatically — no terminal, no typing file paths.

### Browser version: the engine bridge

In the browser the app drives your engine through a small local helper called the
**engine bridge**, because a web page cannot launch a program on its own. The
bridge runs only on your machine, binds to `localhost`, and is not reachable from
the internet.

```bash
npm run bridge      # starts the bridge helper (leave it running)
# ...or run the app and the bridge together:
npm run dev:full
```

Then in the app's **Engine** panel choose **My own engine (local)**, paste the full
path to your engine program, and click **Connect**. Your choice is remembered for
next time.

> The bridge is for local use only. The published/online build always uses the
> built-in browser engine.

## Desktop app (Windows installer)

The same app can be packaged as an installable Windows program so it can be
double-clicked like any other app — and so you can pick your own engine with a
native **Browse…** dialog instead of the bridge helper. The desktop shell loads
the exact same web app; the built-in browser Stockfish is still the default.

```bash
npm run electron:dev   # run the desktop app in development (with live reload)
npm run dist           # build the Windows installer into release/
```

`npm run dist` produces a standard NSIS installer (`.exe`) in the `release/`
folder. Hand that file to users — they run it once, then launch **Chess Tree
Analyzer** from the Start menu or desktop shortcut. Nothing else to install.

> Build the Windows installer on a Windows machine. The desktop app needs the
> `electron` and `electron-builder` dev dependencies (`npm install`).

## Building for production

```bash
npm run build      # outputs to dist/
npm run preview    # preview the production build locally
```

## Tech stack

- **React** + **Vite**
- **Stockfish 16** (NNUE) compiled to WebAssembly, run in a Web Worker
  (`public/stockfish/`)
- **chess.js** for move generation, rules, and PGN/FEN parsing
- **react-chessboard** for the interactive board
- A small **local engine bridge** (Node + `ws`, in `server/`) that lets the app
  drive a native UCI engine on your own machine

## Project layout

```
src/
  App.jsx              App shell and state
  main.jsx             Entry point
  index.css            Styles
  components/          Board, EnginePanel, InputPanel, SettingsPanel, VariationTree, HelpModal
  analysis/            Tree generation, evaluation, PGN/JSON output
  engine/              UCI engine clients (shared base, browser Worker, local bridge, desktop IPC)
server/
  engine-bridge.js     Local WebSocket helper that runs a native UCI engine
  uciProcess.cjs       Shared helper that spawns a native engine (used by the bridge and desktop app)
electron/
  main.cjs             Desktop app main process (window, file dialog, engine IPC)
  preload.cjs          Safe window.desktop bridge exposed to the page
public/
  stockfish/           Stockfish WASM engine files
```
