// Local engine inside the desktop app: talks to the Electron main process over
// the safe `window.desktop` bridge, which launches a native UCI engine the
// browser cannot run directly. No terminal and no localhost server needed — the
// engine is picked with a native "Browse…" dialog.
//
// All UCI/protocol logic lives in UciEngine; this class only provides the
// transport (start / send / receive / stop) via window.desktop.

import { UciEngine, parseInfoLine } from "./uciEngine.js";

// True only when running inside the desktop shell (preload injected the bridge).
export function isDesktop() {
  return (
    typeof window !== "undefined" &&
    !!window.desktop &&
    window.desktop.isDesktop === true
  );
}

export class DesktopEngine extends UciEngine {
  constructor({ enginePath } = {}) {
    super();
    this._enginePath = enginePath || "";
    this._off = null;
  }

  _openTransport() {
    return new Promise((resolve, reject) => {
      if (!isDesktop()) {
        reject(new Error("The desktop engine is only available in the desktop app."));
        return;
      }

      let started = false;
      let settled = false;

      this._off = window.desktop.onMessage((msg) => {
        if (!msg || typeof msg !== "object") return;

        if (msg.type === "line") {
          this._emit(String(msg.data ?? ""));
        } else if (msg.type === "error") {
          const err = new Error(msg.message || "The engine reported an error.");
          if (!started) {
            settled = true;
            reject(err);
          } else {
            this._handleFatal(err);
          }
        } else if (msg.type === "exit") {
          const err = new Error(
            "The engine stopped unexpectedly. Pick the engine again to reconnect."
          );
          if (!started) {
            settled = true;
            reject(err);
          } else {
            this._handleFatal(err);
          }
        }
      });

      window.desktop
        .startEngine(this._enginePath)
        .then((res) => {
          if (settled) return;
          if (res && res.ok) {
            started = true;
            this._open = true;
            resolve();
          } else {
            reject(new Error((res && res.message) || "Could not start the engine."));
          }
        })
        .catch((err) => {
          if (!settled) reject(err);
        });
    });
  }

  _postRaw(cmd) {
    if (!isDesktop()) throw new Error("Engine not connected");
    window.desktop.sendCommand(cmd);
  }

  _closeTransport() {
    try {
      if (this._off) this._off();
    } catch (e) {
      /* ignore */
    }
    this._off = null;
    try {
      if (isDesktop()) window.desktop.stopEngine();
    } catch (e) {
      /* ignore */
    }
  }
}

export { parseInfoLine };
