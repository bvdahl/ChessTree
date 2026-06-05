// Preload script for the desktop app.
//
// Runs in an isolated context and exposes a tiny, safe `window.desktop` API to
// the page. The page can ask the user to pick an engine file, start/stop a
// native engine, send UCI commands, and listen for the engine's output — but it
// has NO direct access to Node, the filesystem, or process spawning.

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("desktop", {
  // Marker the web app checks to know it's running inside the desktop shell.
  isDesktop: true,

  // Open the native file picker; resolves to the chosen file path, or null.
  pickEngine: () => ipcRenderer.invoke("engine:pick"),

  // Launch the native engine at `path`. Resolves to { ok: true } once spawned,
  // or { ok: false, message } if it could not be started.
  startEngine: (path) => ipcRenderer.invoke("engine:start", path),

  // Stop the running engine.
  stopEngine: () => ipcRenderer.invoke("engine:stop"),

  // Send a raw UCI command to the engine.
  sendCommand: (cmd) => ipcRenderer.send("engine:cmd", cmd),

  // Subscribe to engine messages: { type: "line"|"error"|"exit", ... }.
  // Returns an unsubscribe function.
  onMessage: (cb) => {
    const listener = (_event, msg) => cb(msg);
    ipcRenderer.on("engine:message", listener);
    return () => ipcRenderer.removeListener("engine:message", listener);
  },
});
