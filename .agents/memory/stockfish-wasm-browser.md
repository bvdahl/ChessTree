---
name: Stockfish WASM in the browser (web/)
description: How the browser Chess Tree web app runs Stockfish via WASM worker; non-obvious gotchas.
---

The `web/` app runs Stockfish 16 (npm `stockfish@16`) as a classic Web Worker.

- Use the single-threaded build (`stockfish-nnue-16-single.js` + `.wasm`) copied
  into `web/public/stockfish/`. The single build only needs its `.wasm` sibling;
  it does NOT need the 40MB `nn-*.nnue` file — it runs with "classical evaluation
  enabled" (Use NNUE defaults to false in this build). So no big net download.
- Multi-threaded builds require cross-origin isolation (COOP `same-origin` +
  COEP `require-corp`). Vite is configured with those headers anyway, but threads
  are capped at 1 in the single build (option `Threads max 1`), so the Threads
  setting is effectively cosmetic.
- **Worker vs raw module postMessage differ:** as a Web Worker you call the
  *worker's* `postMessage('uci')` (no second arg) — the bundled postscript adds
  the internal `myEngine.postMessage(line, true)` for you. If you ever load the
  raw module directly in Node via `require()` (returns the emscripten factory),
  call `engine.postMessage(cmd)` with NO second arg — passing `true` there makes
  it silently swallow commands (no `uciok`). This cost real debugging time.

**Why:** validating the engine in Node was flaky because of the postMessage arg
mismatch; the actual product path (browser worker) was fine all along. Verify the
real engine by a temporary on-ready self-run in `App.jsx` and read browser console
logs, rather than fighting a Node harness.

**How to apply:** for engine changes, confirm `uciok`/`readyok` in browser console
first; algorithm logic (tree build, filtering, PGN/JSON) is pure JS and best tested
with a deterministic mock engine returning the multipv shape
`{multipv, scoreType, scoreValue, uci, pv, depth}`.
