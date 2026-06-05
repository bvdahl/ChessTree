// Shared helper that launches a native UCI engine program and relays its output
// line by line. Used by BOTH:
//   - the local WebSocket bridge (server/engine-bridge.js), for the browser app
//   - the desktop app's main process (electron/main.cjs)
//
// It is written as CommonJS so the Electron main process (CommonJS) can
// `require` it directly, while the ESM bridge imports it as a default export.

const { spawn } = require("node:child_process");

class UciProcess {
  // handlers: { onLine(line), onError(err), onExit(code, signal) }
  constructor(enginePath, handlers = {}) {
    this.onLine = handlers.onLine || (() => {});
    this.onError = handlers.onError || (() => {});
    this.onExit = handlers.onExit || (() => {});
    this._buf = "";
    this.proc = null;
    this._start(String(enginePath || ""));
  }

  _start(enginePath) {
    let proc;
    try {
      proc = spawn(enginePath, [], { stdio: ["pipe", "pipe", "pipe"] });
    } catch (err) {
      // Report asynchronously so the caller's assignment completes first, and so
      // this mirrors the async "error" event path below.
      setImmediate(() => this.onError(err));
      return;
    }
    this.proc = proc;

    // A bad path surfaces here (ENOENT), asynchronously, not as a throw.
    proc.on("error", (err) => {
      if (this.proc === proc) this.proc = null;
      this.onError(err);
    });

    proc.on("exit", (code, signal) => {
      if (this.proc === proc) this.proc = null;
      this.onExit(code, signal);
    });

    proc.stdout.on("data", (chunk) => {
      this._buf += chunk.toString();
      let idx;
      while ((idx = this._buf.indexOf("\n")) >= 0) {
        const line = this._buf.slice(0, idx).replace(/\r$/, "");
        this._buf = this._buf.slice(idx + 1);
        this.onLine(line);
      }
    });

    // Native engines sometimes print banners to stderr; ignore it.
    proc.stderr.on("data", () => {});
  }

  write(cmd) {
    if (this.proc && this.proc.stdin && this.proc.stdin.writable) {
      try {
        this.proc.stdin.write(String(cmd) + "\n");
      } catch (e) {
        /* ignore */
      }
    }
  }

  kill() {
    const proc = this.proc;
    if (!proc) return;
    this.proc = null;
    try {
      proc.stdin.write("quit\n");
    } catch (e) {
      /* ignore */
    }
    try {
      proc.kill();
    } catch (e) {
      /* ignore */
    }
  }
}

module.exports = { UciProcess };
