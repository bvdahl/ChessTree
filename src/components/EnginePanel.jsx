import React, { useEffect, useState } from "react";

// Lets the user pick which chess engine powers the analysis:
//   - "builtin": the Stockfish that ships with the app and runs in the browser.
//   - "local":   their own engine program, launched by the local bridge helper.
export default function EnginePanel({
  source,
  path,
  status, // "loading" | "ready" | "error"
  error,
  name,
  desktop, // true when running inside the installed desktop app
  onChooseBuiltin,
  onConnectLocal,
  onBrowse, // returns a Promise resolving to a chosen file path, or null
  disabled,
}) {
  const [pathInput, setPathInput] = useState(path || "");

  // Keep the text box in sync if the saved path changes from outside.
  useEffect(() => {
    setPathInput(path || "");
  }, [path]);

  const local = source === "local";
  const connecting = local && status === "loading";

  // Desktop app: open the native file picker, then connect to the chosen engine.
  async function handleBrowse() {
    if (!onBrowse) return;
    const chosen = await onBrowse();
    if (chosen) {
      setPathInput(chosen);
      onConnectLocal(chosen);
    }
  }

  return (
    <div className="card" style={{ opacity: disabled ? 0.6 : 1 }}>
      <h2>Engine</h2>
      <div className="tabs">
        <button
          className={"tab" + (!local ? " active" : "")}
          onClick={onChooseBuiltin}
          disabled={disabled}
          title="Use the Stockfish engine built into the app. Runs in your browser — nothing to install."
        >
          Built-in (browser)
        </button>
        <button
          className={"tab" + (local ? " active" : "")}
          onClick={() => onConnectLocal(pathInput)}
          disabled={disabled}
          title={
            desktop
              ? "Use a chess engine program you downloaded to your own computer. Click Browse to pick it."
              : "Use a chess engine program you downloaded to your own computer (needs the bridge helper running)."
          }
        >
          My own engine (local)
        </button>
      </div>

      {!local && (
        <p className="muted" style={{ marginTop: 4 }}>
          Stockfish 16 runs right here in your browser. Best choice for most
          people — no setup needed.
        </p>
      )}

      {local && (
        <div className="field">
          <label>Path to your engine program</label>
          <input
            type="text"
            value={pathInput}
            onChange={(e) => setPathInput(e.target.value)}
            placeholder="e.g. C:\\Users\\you\\Downloads\\stockfish\\stockfish.exe"
            disabled={disabled}
            title="The full path to your downloaded engine. On Windows it ends in .exe; on Mac/Linux it's the program file you can run."
            onKeyDown={(e) => {
              if (e.key === "Enter" && !disabled) onConnectLocal(pathInput);
            }}
          />
          <div className="btn-group" style={{ marginTop: 8 }}>
            {desktop && (
              <button
                className="btn btn-secondary"
                onClick={handleBrowse}
                disabled={disabled}
                title="Open a file window to find your engine program on this computer"
              >
                Browse…
              </button>
            )}
            <button
              className="btn btn-secondary"
              onClick={() => onConnectLocal(pathInput)}
              disabled={disabled || !pathInput.trim()}
              title={
                desktop
                  ? "Start the selected engine and connect to it"
                  : "Launch your engine through the local bridge and connect to it"
              }
            >
              {connecting ? "Connecting…" : "Connect"}
            </button>
          </div>

          {desktop ? (
            <p className="muted" style={{ marginTop: 8 }}>
              Click <em>Browse…</em> to find your engine program on this computer
              (on Windows it ends in <code>.exe</code>), then it connects
              automatically. No terminal needed. Everything stays on your
              computer.
            </p>
          ) : (
            <p className="muted" style={{ marginTop: 8 }}>
              First, start the bridge helper: open a terminal in this project and
              run <code>npm run bridge</code> (or run{" "}
              <code>npm run dev:full</code> to start the app and the bridge
              together). Then paste the full path to your engine above and click
              Connect. Everything stays on your computer.
            </p>
          )}

          {status === "ready" && (
            <p className="muted" style={{ marginTop: 4, color: "#2e7d32" }}>
              Connected{name ? ` to ${name}` : ""}.
            </p>
          )}
          {status === "error" && error && (
            <div className="error-box" style={{ marginTop: 8 }}>
              {error}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
