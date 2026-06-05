// Local engine bridge.
//
// This is a tiny helper that runs ONLY on your own computer. The Chess Tree
// Analyzer runs in your browser, and browsers cannot launch a native program
// such as a downloaded Stockfish .exe. This bridge does that for you: it opens
// a localhost WebSocket, the app connects to it, tells it which engine file to
// run, and the bridge relays UCI messages back and forth.
//
// Run it with:   npm run bridge
// or run it together with the web app:   npm run dev:full
//
// It listens on 127.0.0.1 only, so nothing on your network or the internet can
// reach it. Stop it with Ctrl+C.

import { WebSocketServer } from "ws";
import uciProcessModule from "./uciProcess.cjs";

const { UciProcess } = uciProcessModule;

const PORT = Number(process.env.ENGINE_BRIDGE_PORT) || 4090;
const HOST = "127.0.0.1";

// Security: a browser lets ANY website open a WebSocket to localhost (there is no
// CORS preflight for WebSockets). Since this bridge can launch programs, we must
// not accept connections from arbitrary web pages — otherwise a malicious site
// you happen to have open could drive it. We therefore only accept handshakes
// whose Origin is this app running on localhost. Browsers always send a truthful
// Origin header that web pages cannot forge. Non-browser clients (e.g. a test
// script or CLI) send no Origin and are allowed, because a web page cannot reach
// this case.
function isAllowedOrigin(origin) {
  if (!origin) return true; // not a browser page
  try {
    const host = new URL(origin).hostname;
    return host === "localhost" || host === "127.0.0.1" || host === "::1";
  } catch (e) {
    return false;
  }
}

const wss = new WebSocketServer({
  host: HOST,
  port: PORT,
  verifyClient: ({ origin }) => {
    const ok = isAllowedOrigin(origin);
    if (!ok) {
      console.warn(
        `[engine-bridge] rejected a connection from origin "${origin}". ` +
          "Only the app running on localhost may use the bridge."
      );
    }
    return ok;
  },
});

console.log(`[engine-bridge] listening on ws://${HOST}:${PORT}`);
console.log(
  "[engine-bridge] Leave this window open. In the app, choose “My own engine”, " +
    "paste the full path to your engine, and click Connect."
);

wss.on("connection", (ws) => {
  let engine = null;

  const sendJson = (obj) => {
    if (ws.readyState === ws.OPEN) ws.send(JSON.stringify(obj));
  };

  const killEngine = () => {
    if (!engine) return;
    const proc = engine;
    engine = null;
    proc.kill();
  };

  ws.on("message", (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw.toString());
    } catch (e) {
      return;
    }
    if (!msg || typeof msg !== "object") return;

    if (msg.type === "start") {
      killEngine();
      const enginePath = String(msg.path || "").trim();
      if (!enginePath) {
        sendJson({ type: "error", message: "No engine path was provided." });
        return;
      }

      engine = new UciProcess(enginePath, {
        onLine: (line) => sendJson({ type: "line", data: line }),
        onError: (err) => {
          engine = null;
          sendJson({
            type: "error",
            message:
              "Could not start that engine: " +
              err.message +
              ". Check that the path points to a real engine program.",
          });
        },
        onExit: (code, signal) => {
          engine = null;
          sendJson({ type: "exit", code, signal });
        },
      });

      sendJson({ type: "started" });
      return;
    }

    if (msg.type === "cmd") {
      if (engine) engine.write(msg.data);
      return;
    }

    if (msg.type === "stop-engine") {
      killEngine();
      return;
    }
  });

  ws.on("close", killEngine);
  ws.on("error", killEngine);
});

wss.on("error", (err) => {
  if (err && err.code === "EADDRINUSE") {
    console.error(
      `[engine-bridge] Port ${PORT} is already in use. Is the bridge already ` +
        "running? You can pick another port with ENGINE_BRIDGE_PORT."
    );
  } else {
    console.error("[engine-bridge] server error:", err.message);
  }
  process.exit(1);
});
