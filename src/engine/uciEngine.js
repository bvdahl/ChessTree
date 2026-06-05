// Shared UCI engine client.
//
// Holds all the protocol logic (handshake, options, analysis, MultiPV parsing)
// that is identical no matter HOW we talk to the engine. Subclasses provide the
// transport:
//   - StockfishEngine: a WebAssembly Web Worker running in the browser.
//   - BridgeEngine: a WebSocket to a local helper that drives a native engine.
//
// Scores returned by the engine are relative to the side to move; callers
// receive raw relative scores and normalize to White's perspective themselves.

export class UciEngine {
  constructor() {
    this.ready = false;
    this._open = false;
    this._listeners = new Set();
    this._initPromise = null;
    this._fatal = null; // set during init() to reject on a transport failure
    this.onFatal = null; // optional callback for failures AFTER init succeeds
    this.maxThreads = 1;
    this.maxHash = 1024;
    this.name = "";
  }

  // --- Transport hooks implemented by subclasses ---
  // _openTransport(): Promise that resolves once the transport is ready to carry
  //   UCI lines. Must call this._emit(line) for every incoming line, and reject
  //   if the transport cannot be established (before the engine is usable).
  // _postRaw(cmd): send a raw UCI command string to the engine.
  // _closeTransport(): tear the transport down.

  _emit(line) {
    for (const fn of this._listeners) fn(line);
  }

  // Route an unexpected transport/engine failure. During init() it rejects the
  // pending init; afterwards it notifies the app via onFatal.
  _handleFatal(err) {
    this.ready = false;
    this._open = false;
    if (this._fatal) {
      this._fatal(err);
    } else if (this.onFatal) {
      this.onFatal(err);
    }
  }

  _waitFor(token, timeoutMs = 15000) {
    return new Promise((resolve, reject) => {
      const handler = (line) => {
        if (line.startsWith(token)) {
          clearTimeout(timer);
          this._listeners.delete(handler);
          resolve();
        }
      };
      const timer = setTimeout(() => {
        this._listeners.delete(handler);
        reject(new Error(`Timed out waiting for "${token}"`));
      }, timeoutMs);
      this._listeners.add(handler);
    });
  }

  async init({ hashMb = 64, threads = 1 } = {}) {
    if (this._initPromise) return this._initPromise;

    this._initPromise = new Promise((resolve, reject) => {
      let settled = false;
      const fail = (err) => {
        if (settled) return;
        settled = true;
        this._fatal = null;
        reject(err);
      };
      const succeed = () => {
        if (settled) return;
        settled = true;
        this._fatal = null;
        resolve();
      };
      // Transport failures during startup land here.
      this._fatal = fail;

      (async () => {
        try {
          await this._openTransport();

          // Capture the engine's real limits + name from the uci handshake so
          // the UI can show honest Hash/Threads ranges.
          this.maxThreads = 1;
          this.maxHash = 1024;
          this.name = "";
          const optHandler = (line) => {
            if (line.startsWith("id name ")) {
              this.name = line.slice("id name ".length).trim();
            } else if (line.startsWith("option name Threads")) {
              const m = line.match(/max (\d+)/);
              if (m) this.maxThreads = parseInt(m[1], 10);
            } else if (line.startsWith("option name Hash")) {
              const m = line.match(/max (\d+)/);
              if (m) this.maxHash = parseInt(m[1], 10);
            }
          };

          this._listeners.add(optHandler);
          try {
            this.send("uci");
            await this._waitFor("uciok");
          } finally {
            this._listeners.delete(optHandler);
          }

          this.send(`setoption name Hash value ${hashMb}`);
          this.send(`setoption name Threads value ${threads}`);
          this.send("isready");
          await this._waitFor("readyok");
          this.ready = true;
          succeed();
        } catch (err) {
          fail(err);
        }
      })();
    });

    // Swallow rejection here so callers that don't await don't crash; callers
    // that do await still see the rejection.
    this._initPromise.catch(() => {});
    return this._initPromise;
  }

  send(cmd) {
    this._postRaw(cmd);
  }

  async newGame() {
    this.send("ucinewgame");
    this.send("isready");
    await this._waitFor("readyok");
  }

  // Apply engine options (hash size in MB, thread count) at runtime, clamped to
  // the limits this engine reports. Resolves once the engine acknowledges.
  async configure({ hashMb, threads } = {}) {
    if (!this._open) throw new Error("Engine not initialized");
    if (hashMb != null) {
      const h = Math.max(1, Math.min(hashMb, this.maxHash || hashMb));
      this.send(`setoption name Hash value ${h}`);
    }
    if (threads != null) {
      const t = Math.max(1, Math.min(threads, this.maxThreads || 1));
      this.send(`setoption name Threads value ${t}`);
    }
    this.send("isready");
    await this._waitFor("readyok");
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
        // engines often omit the "multipv" token, so we key off " pv ".
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
    if (this._open) {
      try {
        this.send("stop");
      } catch (e) {
        // ignore
      }
    }
  }

  dispose() {
    if (this._open) {
      try {
        this.send("quit");
      } catch (e) {
        // ignore
      }
    }
    try {
      this._closeTransport();
    } catch (e) {
      // ignore
    }
    this.ready = false;
    this._open = false;
    this._initPromise = null;
    this._fatal = null;
    this.onFatal = null;
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
