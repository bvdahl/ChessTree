# Overview

Chess Tree Analyzer is a browser-based application that performs deep chess
position analysis using the Stockfish engine. It generates comprehensive game
trees from chess positions, exploring multiple variations at configurable depths.
Users can import PGN files, analyze a specific FEN position, or play moves on an
interactive board. Results can be exported as nested-variation PGN (compatible
with ChessBase and other chess software) or JSON. The tool is designed for chess
players and analysts who need to explore positions in depth.

The app runs entirely client-side in the browser — there is no backend and
nothing to install. The built-in browser Stockfish is the default and works
everywhere, including the published online version. Optionally, when running
locally, users can point the app at their own downloaded UCI engine (e.g. a
native Stockfish) via a small localhost "engine bridge" helper.

The same web app can also be packaged as an installable **Windows desktop app**
(Electron). The desktop shell loads the identical web build and adds a native
"Browse…" file dialog so non-technical users can pick their own UCI engine
without a terminal or the bridge. The built-in browser Stockfish stays the
default, and the web/published build is unchanged.

The installed desktop app **updates itself automatically** (via
electron-updater). Each `update.bat` run builds the app, stamps it with an
ever-increasing version, and publishes it to GitHub Releases; running copies
quietly download the new version and apply it (offering "Restart now", or
installing on the next app close). So after a one-time manual install of the
first auto-update-enabled build, future changes reach users with no reinstall.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Project Organization

This project is a single browser-based web app (React + Vite) living at the
project root.

- Runs entirely client-side — no backend, no install
- Stockfish 16 via WebAssembly in a Web Worker (`public/stockfish/`)
- chess.js for rules, PGN/FEN parsing, SAN/UCI conversion
- Interactive board (react-chessboard) and a navigable variation tree
- Core engine: breadth-first tree generation, per-side centipawn-threshold move
  filtering, White-perspective evaluation, nested-variation PGN export, plus JSON
  export
- Pluggable engine: a shared UCI client base (`src/engine/uciEngine.js`) with two
  transports — the bundled WASM Worker (default) and a local WebSocket bridge to a
  native engine. Selected in the in-app Engine panel; choice persists in
  localStorage
- In-app user guide (`src/components/HelpModal.jsx`, opened from the header "Help"
  link) plus hover tooltips on every control
- Started by the "Start application" workflow (`npm run dev`, port 5000)

> **Keep help in sync:** Whenever you change any control, setting, default value,
> range, label, behavior, or output in the app, also update the in-app user guide
> (`src/components/HelpModal.jsx`) and the matching control tooltips so the
> documentation never describes the app inaccurately.

## Source Layout

```
index.html             App entry HTML
vite.config.js         Vite config (port 5000, COOP/COEP headers for WASM threads)
package.json           Dependencies, scripts, and electron-builder "build" config
src/
  App.jsx              App shell, engine lifecycle and switching
  main.jsx             Entry point
  index.css            Styles
  components/          Board, EnginePanel, InputPanel, SettingsPanel, VariationTree, HelpModal
  analysis/            Tree generation, evaluation, PGN/JSON output
  engine/              UCI clients: uciEngine (shared base), stockfishEngine (Worker), bridgeEngine (WebSocket), desktopEngine (Electron IPC)
server/
  engine-bridge.js     Local, localhost-only WebSocket helper that spawns a native UCI engine
  uciProcess.cjs       Shared CommonJS helper that spawns a native UCI engine + relays lines (used by the bridge AND the desktop app)
electron/
  main.cjs             Desktop app main process: serves dist/ over a localhost http server (COOP/COEP), native file dialog, engine IPC
  preload.cjs          Exposes a safe window.desktop bridge (isDesktop, pickEngine, start/stop/send, onMessage) to the page
public/
  stockfish/           Stockfish WASM engine files
```

Scripts: `dev` (Vite, used by the Replit workflow), `build`, `preview`,
`bridge` (run the local engine helper), `dev:full` (Vite + bridge together via
`concurrently`), `electron` (run the desktop shell against the built dist/),
`electron:dev` (Vite + Electron together, live reload), `dist` (build the web app
then package a Windows installer into `release/` via electron-builder), `release`
(same as `dist` but also publishes the installer to GitHub Releases so installed
desktop apps can auto-update — this is what `update.bat` runs). The
published/online build never uses the bridge or Electron.

## Core Components

**Chess Analysis Engine** (`src/analysis/`): Orchestrates position analysis using
Stockfish. Uses a tree-based data structure to represent chess variations
hierarchically, with each node containing a chess position, the move that led to
it, and an engine evaluation.

**Engine Integration** (`src/engine/`): A shared UCI client base (`uciEngine.js`)
handles the protocol — handshake, option limits, multi-PV analysis, and lifecycle —
independent of transport. Three transports extend it: `stockfishEngine.js` (the
bundled WASM build in a Web Worker, the default), `bridgeEngine.js` (a localhost
WebSocket to `server/engine-bridge.js`), and `desktopEngine.js` (Electron IPC over
the `window.desktop` bridge). The last two both spawn a user-supplied native UCI
engine via the shared `server/uciProcess.cjs` helper. App.jsx picks the local
transport at runtime: `DesktopEngine` when `isDesktop()` (running in the Electron
shell), otherwise `BridgeEngine`. All expose the same interface, so the analysis
layer is unchanged.

**Desktop shell** (`electron/`): `main.cjs` is the Electron main process. It
serves the Vite build (`dist/`) over a localhost HTTP server with the same
COOP/COEP headers Vite uses (so absolute asset paths and the WASM engine work
exactly as on the web — not `file://`), opens a native "Browse…" file dialog, and
spawns/relays the native engine over IPC using `server/uciProcess.cjs`.
`preload.cjs` exposes only a small, safe `window.desktop` API (context-isolated,
no Node access in the page). The web build is untouched; `isDesktop()` is false in
a normal browser, so nothing changes there.

**User Interface** (`src/components/`): Interactive chess board, engine panel
(built-in vs. own engine), input panel (PGN / FEN / play-on-board), settings
panel, navigable variation tree, and the in-app Help guide.

## Data Processing Pipeline

**Input Processing**: Accepts PGN (extracting positions from a game), a direct FEN
position, or moves played on the board. chess.js handles move validation and board
state throughout.

**Analysis Configuration**: Configurable parameters include analysis depth
(half-moves), time per position, move count per side, and centipawn thresholds for
move filtering. Separate thresholds can be set for White and Black.

**Tree Generation**: Builds the game tree by analyzing the strongest moves from
each position. Move filtering is applied based on centipawn thresholds to focus on
the most relevant variations.

## Output Generation

**Export Formats**: Results can be exported as nested-variation **PGN** (compatible
with chess databases such as ChessBase) or **JSON** for programmatic processing.

# External Dependencies

- **Stockfish 16 (WebAssembly)**: The default chess engine, bundled in
  `public/stockfish/` and run in a Web Worker. Communicates via the UCI protocol.
- **chess.js**: Chess rules, move validation, and PGN/FEN parsing and notation
  conversion.
- **react-chessboard**: Interactive chess board UI component.
- **React + Vite**: Application framework and build tooling.
- **ws** (Node): WebSocket server used only by the optional local engine bridge
  (`server/engine-bridge.js`); not part of the browser bundle.
- **concurrently** (dev): runs Vite and the bridge/Electron together via
  `npm run dev:full` / `npm run electron:dev`.
- **electron** (dev): the desktop shell runtime. Not part of the browser bundle.
- **electron-builder** (dev): packages the Windows installer via `npm run dist`,
  and publishes it to GitHub Releases via `npm run release`.
- **electron-updater**: runtime auto-update for the desktop app. On launch the
  installed app checks the project's public GitHub Releases for a newer published
  version and updates itself. Publishing a build needs a GitHub token (classic,
  `repo` scope) in the `GH_TOKEN` environment variable; `update.bat` prompts for
  it, remembers it (`setx`), and before each build verifies the token can
  actually publish — if it lacks the `repo` permission the script stops with a
  plain-language message and offers to replace the saved token. Every run is also
  saved to `C:\Apps\chesstree-update-log.txt`.
- **cross-env** (dev): sets env vars cross-platform for `npm run electron:dev`.
- **A native UCI engine (optional, user-supplied)**: any Stockfish/UCI executable
  the user has on their own machine, launched by the bridge (browser) or the
  desktop app (Electron) when they pick "My own engine".

# Version Control / GitHub

The web app lives at the project root so it can be synced to GitHub directly. A
`.gitignore` keeps Replit/workspace-only files (`.replit`, `replit.md`, `.local`,
`.agents`, caches, etc.) out of the published repository, leaving a clean
web-only project (`index.html`, `package.json`, `package-lock.json`,
`vite.config.js`, `README.md`, `.gitignore`, `src/`, `public/`, `server/`).
