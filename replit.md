# Overview

Chess Tree Analyzer is a browser-based application that performs deep chess
position analysis using the Stockfish engine. It generates comprehensive game
trees from chess positions, exploring multiple variations at configurable depths.
Users can import PGN files, analyze a specific FEN position, or play moves on an
interactive board. Results can be exported as nested-variation PGN (compatible
with ChessBase and other chess software) or JSON. The tool is designed for chess
players and analysts who need to explore positions in depth.

The app runs entirely client-side in the browser — there is no backend and
nothing to install.

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
package.json           Dependencies and scripts (dev/build/preview)
src/
  App.jsx              App shell and state
  main.jsx             Entry point
  index.css            Styles
  components/          Board, InputPanel, SettingsPanel, VariationTree, HelpModal
  analysis/            Tree generation, evaluation, PGN/JSON output
  engine/              Stockfish Web Worker interface
public/
  stockfish/           Stockfish WASM engine files
```

## Core Components

**Chess Analysis Engine** (`src/analysis/`): Orchestrates position analysis using
Stockfish. Uses a tree-based data structure to represent chess variations
hierarchically, with each node containing a chess position, the move that led to
it, and an engine evaluation.

**Stockfish Integration** (`src/engine/`): Manages UCI protocol communication with
the Stockfish WebAssembly engine running in a Web Worker, including multi-PV
analysis for generating multiple candidate moves per position.

**User Interface** (`src/components/`): Interactive chess board, input panel
(PGN / FEN / play-on-board), settings panel, navigable variation tree, and the
in-app Help guide.

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

- **Stockfish 16 (WebAssembly)**: The chess engine, bundled in
  `public/stockfish/` and run in a Web Worker. Communicates via the UCI protocol.
- **chess.js**: Chess rules, move validation, and PGN/FEN parsing and notation
  conversion.
- **react-chessboard**: Interactive chess board UI component.
- **React + Vite**: Application framework and build tooling.

# Version Control / GitHub

The web app lives at the project root so it can be synced to GitHub directly. A
`.gitignore` keeps Replit/workspace-only files (`.replit`, `replit.md`, `.local`,
`.agents`, caches, etc.) out of the published repository, leaving a clean
web-only project (`index.html`, `package.json`, `package-lock.json`,
`vite.config.js`, `README.md`, `.gitignore`, `src/`, `public/`).
