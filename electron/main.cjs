// Desktop app main process.
//
// Wraps the existing browser app (the Vite build in dist/) in a native window so
// it can be installed and double-clicked, and so the user can pick their own
// chess engine through a real "Browse…" file dialog. The built-in browser
// Stockfish remains the default; the desktop shell only ADDS the ability to run
// a native engine without a terminal.
//
// To make the bundled WebAssembly engine and absolute asset paths work exactly
// as they do on the web, we serve dist/ over a tiny localhost HTTP server (with
// the same COOP/COEP headers Vite uses) and load that URL — rather than file://,
// which would break absolute paths and cross-origin isolation.

const { app, BrowserWindow, dialog, ipcMain } = require("electron");
const path = require("node:path");
const http = require("node:http");
const fs = require("node:fs");
const { UciProcess } = require("../server/uciProcess.cjs");

let currentEngine = null;
let server = null;

// A fixed localhost port keeps the app's origin stable across launches, so the
// user's saved settings (chosen engine, analysis options — stored in
// localStorage, which is keyed to the origin) persist. If the port is busy we
// fall back to an OS-assigned one.
const PREFERRED_PORT = 47615;

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".wasm": "application/wasm",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".map": "application/json; charset=utf-8",
};

// Serve one file out of dist/ with the same cross-origin isolation headers Vite
// uses, so the WASM engine and absolute asset paths behave exactly as on the web.
function serveStatic(req, res) {
  const root = path.join(__dirname, "..", "dist");
  try {
    const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
    let filePath = path.join(root, urlPath === "/" ? "index.html" : urlPath);

    // Guard against path traversal outside dist/.
    if (filePath !== root && !filePath.startsWith(root + path.sep)) {
      res.writeHead(403);
      res.end();
      return;
    }

    // Single-page app fallback: unknown paths serve index.html.
    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
      filePath = path.join(root, "index.html");
    }

    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, {
      "Content-Type": MIME[ext] || "application/octet-stream",
      "Cross-Origin-Opener-Policy": "same-origin",
      "Cross-Origin-Embedder-Policy": "require-corp",
      "Cross-Origin-Resource-Policy": "same-origin",
    });
    fs.createReadStream(filePath).pipe(res);
  } catch (e) {
    res.writeHead(500);
    res.end();
  }
}

// Bind the server to a port, resolving on success and rejecting on error.
function listenOn(srv, port) {
  return new Promise((resolve, reject) => {
    const onError = (err) => {
      srv.removeListener("listening", onListening);
      reject(err);
    };
    const onListening = () => {
      srv.removeListener("error", onError);
      resolve();
    };
    srv.once("error", onError);
    srv.once("listening", onListening);
    srv.listen(port, "127.0.0.1");
  });
}

// Serve dist/ on 127.0.0.1, preferring a fixed port (stable origin → persisted
// settings) and falling back to any free port if it's already in use.
async function startStaticServer() {
  const srv = http.createServer(serveStatic);
  try {
    await listenOn(srv, PREFERRED_PORT);
  } catch (e) {
    await listenOn(srv, 0);
  }
  return srv;
}

// In dev the page is served by Vite, which may not be up yet — retry briefly.
function loadDevUrl(win, url, attempt = 0) {
  win.loadURL(url).catch(() => {
    if (attempt < 40 && !win.isDestroyed()) {
      setTimeout(() => loadDevUrl(win, url, attempt + 1), 500);
    }
  });
}

async function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 880,
    backgroundColor: "#0f1115",
    title: "Chess Tree Analyzer",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  // Plain desktop app — no menu bar needed.
  win.removeMenu();

  // Keep the renderer locked to the app: no popups, and no navigating away to
  // external origins (everything we serve is on 127.0.0.1).
  win.webContents.setWindowOpenHandler(() => ({ action: "deny" }));
  win.webContents.on("will-navigate", (event, url) => {
    try {
      const host = new URL(url).hostname;
      if (host !== "127.0.0.1" && host !== "localhost") event.preventDefault();
    } catch (e) {
      event.preventDefault();
    }
  });

  const devUrl = process.env.ELECTRON_DEV_URL;
  if (devUrl) {
    loadDevUrl(win, devUrl);
  } else {
    server = await startStaticServer();
    const { port } = server.address();
    win.loadURL(`http://127.0.0.1:${port}/`);
  }
}

// --- Engine IPC ---------------------------------------------------------------

ipcMain.handle("engine:pick", async (event) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  const filters =
    process.platform === "win32"
      ? [
          { name: "Programs", extensions: ["exe"] },
          { name: "All files", extensions: ["*"] },
        ]
      : [{ name: "All files", extensions: ["*"] }];

  const result = await dialog.showOpenDialog(win, {
    title: "Choose your chess engine program",
    properties: ["openFile"],
    filters,
  });

  if (result.canceled || !result.filePaths.length) return null;
  return result.filePaths[0];
});

ipcMain.handle("engine:start", async (event, enginePath) => {
  if (currentEngine) {
    currentEngine.kill();
    currentEngine = null;
  }

  const p = String(enginePath || "").trim();
  if (!p) return { ok: false, message: "No engine path was provided." };

  const sender = event.sender;
  const send = (msg) => {
    if (!sender.isDestroyed()) sender.send("engine:message", msg);
  };

  currentEngine = new UciProcess(p, {
    onLine: (line) => send({ type: "line", data: line }),
    onError: (err) => {
      currentEngine = null;
      send({
        type: "error",
        message:
          "Could not start that engine: " +
          err.message +
          ". Check that the file is a real engine program.",
      });
    },
    onExit: (code, signal) => {
      currentEngine = null;
      send({ type: "exit", code, signal });
    },
  });

  return { ok: true };
});

ipcMain.on("engine:cmd", (event, cmd) => {
  if (currentEngine) currentEngine.write(cmd);
});

ipcMain.handle("engine:stop", async () => {
  if (currentEngine) {
    currentEngine.kill();
    currentEngine = null;
  }
  return { ok: true };
});

// --- App lifecycle ------------------------------------------------------------

app.whenReady().then(createWindow);

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on("window-all-closed", () => {
  if (currentEngine) {
    currentEngine.kill();
    currentEngine = null;
  }
  if (server) {
    try {
      server.close();
    } catch (e) {
      /* ignore */
    }
    server = null;
  }
  if (process.platform !== "darwin") app.quit();
});
