// Stockfish engine client: wraps the WASM worker and speaks UCI.
// Scores returned by Stockfish are relative to the side to move; callers
// receive raw relative scores and normalize to White's perspective themselves.

const ENGINE_URL = "/stockfish/stockfish-nnue-16-single.js";

export class StockfishEngine {
  constructor() {
    this.worker = null;
    this.ready = false;
    this._listeners = new Set();
    this._initPromise = null;
  }

  async init({ hashMb = 64, threads = 1 } = {}) {
    if (this._initPromise) return this._initPromise;

    this._initPromise = new Promise((resolve, reject) => {
      try {
        this.worker = new Worker(ENGINE_URL);
      } catch (err) {
        reject(new Error("Failed to start Stockfish worker: " + err.message));
        return;
      }

      const onMessage = (e) => {
        const line = typeof e.data === "string" ? e.data : "";
        for (const fn of this._listeners) fn(line);
      };
      this.worker.addEventListener("message", onMessage);
      this.worker.addEventListener("error", (e) => {
        reject(new Error("Stockfish worker error: " + (e.message || "unknown")));
      });

      const waitFor = (token, timeoutMs = 15000) =>
        new Promise((res, rej) => {
          const timer = setTimeout(
            () => rej(new Error(`Timed out waiting for "${token}"`)),
            timeoutMs
          );
          const handler = (line) => {
            if (line.startsWith(token)) {
              clearTimeout(timer);
              this._listeners.delete(handler);
              res();
            }
          };
          this._listeners.add(handler);
        });

      // Capture the engine's real option limits from the uci handshake so the
      // UI can present honest Hash/Threads ranges (this build caps Threads = 1).
      this.maxThreads = 1;
      this.maxHash = 1024;
      const optHandler = (line) => {
        if (line.startsWith("option name Threads")) {
          const m = line.match(/max (\d+)/);
          if (m) this.maxThreads = parseInt(m[1], 10);
        } else if (line.startsWith("option name Hash")) {
          const m = line.match(/max (\d+)/);
          if (m) this.maxHash = parseInt(m[1], 10);
        }
      };

      (async () => {
        try {
          this._listeners.add(optHandler);
          this.send("uci");
          await waitFor("uciok");
          this._listeners.delete(optHandler);
          this.send(`setoption name Hash value ${hashMb}`);
          this.send(`setoption name Threads value ${threads}`);
          this.send("isready");
          await waitFor("readyok");
          this.ready = true;
          resolve();
        } catch (err) {
          this._listeners.delete(optHandler);
          reject(err);
        }
      })();
    });

    return this._initPromise;
  }

  send(cmd) {
    if (!this.worker) throw new Error("Engine not initialized");
    this.worker.postMessage(cmd);
  }

  async newGame() {
    this.send("ucinewgame");
    this.send("isready");
    await new Promise((resolve) => {
      const handler = (line) => {
        if (line.startsWith("readyok")) {
          this._listeners.delete(handler);
          resolve();
        }
      };
      this._listeners.add(handler);
    });
  }

  // Apply engine options (hash size in MB, thread count) at runtime, clamped to
  // the limits this build reports. Resolves once the engine acknowledges.
  async configure({ hashMb, threads } = {}) {
    if (!this.worker) throw new Error("Engine not initialized");
    if (hashMb != null) {
      const h = Math.max(1, Math.min(hashMb, this.maxHash || hashMb));
      this.send(`setoption name Hash value ${h}`);
    }
    if (threads != null) {
      const t = Math.max(1, Math.min(threads, this.maxThreads || 1));
      this.send(`setoption name Threads value ${t}`);
    }
    this.send("isready");
    await new Promise((resolve) => {
      const handler = (line) => {
        if (line.startsWith("readyok")) {
          this._listeners.delete(handler);
          resolve();
        }
      };
      this._listeners.add(handler);
    });
  }

  // Analyze a FEN. Returns up to multiPv entries:
  //   { multipv, scoreType: 'cp'|'mate', scoreValue, uci, pv: string[], depth }
  // scoreValue is RELATIVE to the side to move (raw engine value).
  analyze(fen, { multiPv = 3, moveTimeMs = 2000 } = {}, signal) {
    return new Promise((resolve, reject) => {
      if (!this.ready) {
        reject(new Error("Engine not ready"));
        return;
      }

      const results = new Map();
      let settled = false;

      const cleanup = () => {
        this._listeners.delete(handler);
        if (signal) signal.removeEventListener("abort", onAbort);
        clearTimeout(safetyTimer);
        if (abortTimer) clearTimeout(abortTimer);
      };

      const finish = () => {
        if (settled) return;
        settled = true;
        cleanup();
        const sorted = [...results.values()].sort(
          (a, b) => a.multipv - b.multipv
        );
        resolve(sorted);
      };

      let abortTimer = null;
      const onAbort = () => {
        if (settled) return;
        this.send("stop");
        // Resolve promptly with partial results if bestmove is delayed/lost.
        abortTimer = setTimeout(finish, 1500);
      };

      const handler = (line) => {
        // Capture any info line carrying a principal variation. With MultiPV=1
        // Stockfish often omits the "multipv" token, so we key off " pv ".
        if (line.startsWith("info") && line.includes(" pv ")) {
          const parsed = parseInfoLine(line);
          if (parsed && parsed.uci) {
            results.set(parsed.multipv, parsed);
          }
        } else if (line.startsWith("bestmove")) {
          finish();
        }
      };

      this._listeners.add(handler);
      if (signal) {
        if (signal.aborted) {
          // Resolve empty immediately.
          this._listeners.delete(handler);
          resolve([]);
          return;
        }
        signal.addEventListener("abort", onAbort);
      }

      // Safety net in case bestmove never arrives.
      const safetyTimer = setTimeout(finish, moveTimeMs + 8000);

      this.send(`setoption name MultiPV value ${multiPv}`);
      this.send(`position fen ${fen}`);
      this.send(`go movetime ${moveTimeMs}`);
    });
  }

  stop() {
    if (this.worker) this.send("stop");
  }

  dispose() {
    if (this.worker) {
      try {
        this.send("quit");
      } catch (e) {
        // ignore
      }
      this.worker.terminate();
      this.worker = null;
    }
    this.ready = false;
    this._initPromise = null;
    this._listeners.clear();
  }
}

export function parseInfoLine(line) {
  const parts = line.split(/\s+/);
  const out = {
    multipv: 1,
    scoreType: "cp",
    scoreValue: 0,
    uci: null,
    pv: [],
    depth: 0,
  };

  for (let i = 0; i < parts.length; i++) {
    const tok = parts[i];
    if (tok === "multipv") {
      out.multipv = parseInt(parts[i + 1], 10) || 1;
    } else if (tok === "depth") {
      out.depth = parseInt(parts[i + 1], 10) || 0;
    } else if (tok === "score") {
      const kind = parts[i + 1];
      const val = parseInt(parts[i + 2], 10);
      if (kind === "cp") {
        out.scoreType = "cp";
        out.scoreValue = val;
      } else if (kind === "mate") {
        out.scoreType = "mate";
        out.scoreValue = val;
      }
      i += 2;
    } else if (tok === "pv") {
      out.pv = parts.slice(i + 1);
      out.uci = out.pv[0] || null;
      break;
    }
  }

  return out.uci ? out : null;
}
