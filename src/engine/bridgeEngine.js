// Local engine via the bridge: talks over a localhost WebSocket to the helper
// in server/engine-bridge.js, which launches a native UCI engine (e.g. a
// downloaded Stockfish executable) that the browser cannot run directly.
//
// All UCI/protocol logic lives in UciEngine; this class only provides the
// WebSocket transport and the engine-path handshake with the bridge.

import { UciEngine } from "./uciEngine.js";

export const DEFAULT_BRIDGE_PORT = 4090;

export function bridgeUrl(port = DEFAULT_BRIDGE_PORT) {
  // The bridge runs on the user's own machine. Use localhost so it works no
  // matter whether the app was opened via localhost or 127.0.0.1.
  return `ws://localhost:${port}`;
}

const BRIDGE_DOWN_MSG =
  "Could not reach the local engine helper. Start it first by running " +
  "“npm run bridge” in a terminal, then try Connect again.";

export class BridgeEngine extends UciEngine {
  constructor({ enginePath, port = DEFAULT_BRIDGE_PORT } = {}) {
    super();
    this._enginePath = enginePath || "";
    this._url = bridgeUrl(port);
    this.ws = null;
  }

  _openTransport() {
    return new Promise((resolve, reject) => {
      let started = false;
      let ws;
      try {
        ws = new WebSocket(this._url);
      } catch (err) {
        reject(new Error(BRIDGE_DOWN_MSG));
        return;
      }
      this.ws = ws;

      const connectTimer = setTimeout(() => {
        if (!started) {
          try {
            ws.close();
          } catch (e) {
            /* ignore */
          }
          reject(new Error(BRIDGE_DOWN_MSG));
        }
      }, 8000);

      ws.addEventListener("open", () => {
        ws.send(
          JSON.stringify({ type: "start", path: this._enginePath })
        );
      });

      ws.addEventListener("message", (e) => {
        let msg;
        try {
          msg = JSON.parse(typeof e.data === "string" ? e.data : "");
        } catch (err) {
          return;
        }
        if (!msg || typeof msg !== "object") return;

        if (msg.type === "started") {
          started = true;
          this._open = true;
          clearTimeout(connectTimer);
          resolve();
        } else if (msg.type === "line") {
          this._emit(String(msg.data ?? ""));
        } else if (msg.type === "error") {
          const err = new Error(msg.message || "The engine reported an error.");
          if (!started) {
            clearTimeout(connectTimer);
            reject(err);
          } else {
            this._handleFatal(err);
          }
        } else if (msg.type === "exit") {
          const err = new Error(
            "The engine stopped unexpectedly. Check the engine file and try Connect again."
          );
          if (!started) {
            clearTimeout(connectTimer);
            reject(err);
          } else {
            this._handleFatal(err);
          }
        }
      });

      ws.addEventListener("error", () => {
        if (!started) {
          clearTimeout(connectTimer);
          reject(new Error(BRIDGE_DOWN_MSG));
        }
        // After start, the "close" handler reports the disconnect.
      });

      ws.addEventListener("close", () => {
        if (!started) {
          clearTimeout(connectTimer);
          reject(new Error(BRIDGE_DOWN_MSG));
        } else {
          this._handleFatal(
            new Error("Lost connection to the local engine helper.")
          );
        }
      });
    });
  }

  _postRaw(cmd) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error("Engine not connected");
    }
    this.ws.send(JSON.stringify({ type: "cmd", data: cmd }));
  }

  _closeTransport() {
    if (this.ws) {
      try {
        if (this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({ type: "stop-engine" }));
        }
      } catch (e) {
        /* ignore */
      }
      try {
        this.ws.close();
      } catch (e) {
        /* ignore */
      }
      this.ws = null;
    }
  }
}
