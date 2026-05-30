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

## Project layout

```
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
