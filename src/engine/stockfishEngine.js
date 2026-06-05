// Built-in Stockfish engine: runs the bundled WASM build in a Web Worker.
// All UCI/protocol logic lives in UciEngine; this class only provides the
// Web Worker transport.

import { UciEngine, parseInfoLine } from "./uciEngine.js";

const ENGINE_URL = "/stockfish/stockfish-nnue-16-single.js";

export class StockfishEngine extends UciEngine {
  constructor() {
    super();
    this.worker = null;
  }

  _openTransport() {
    return new Promise((resolve, reject) => {
      try {
        this.worker = new Worker(ENGINE_URL);
      } catch (err) {
        reject(new Error("Failed to start Stockfish worker: " + err.message));
        return;
      }

      this.worker.addEventListener("message", (e) => {
        const line = typeof e.data === "string" ? e.data : "";
        this._emit(line);
      });
      this.worker.addEventListener("error", (e) => {
        this._handleFatal(
          new Error("Stockfish worker error: " + (e.message || "unknown"))
        );
      });

      this._open = true;
      resolve();
    });
  }

  _postRaw(cmd) {
    if (!this.worker) throw new Error("Engine not initialized");
    this.worker.postMessage(cmd);
  }

  _closeTransport() {
    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
  }
}

// Re-export so existing importers keep working.
export { parseInfoLine };
