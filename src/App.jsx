import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Chess } from "chess.js";
import { StockfishEngine } from "./engine/stockfishEngine.js";
import { BridgeEngine } from "./engine/bridgeEngine.js";
import { DesktopEngine, isDesktop } from "./engine/desktopEngine.js";
import { generateTree, parsePgn } from "./analysis/analysisEngine.js";
import { treeToPgn, treeToJson, countAnalyzedNodes } from "./analysis/output.js";
import Board from "./components/Board.jsx";
import VariationTree from "./components/VariationTree.jsx";
import SettingsPanel from "./components/SettingsPanel.jsx";
import InputPanel from "./components/InputPanel.jsx";
import EnginePanel from "./components/EnginePanel.jsx";
import HelpModal from "./components/HelpModal.jsx";

const START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

const DEFAULT_SETTINGS = {
  maxDepth: 4,
  moveTimeMs: 1500,
  whiteMoves: 3,
  blackMoves: 3,
  whiteThreshold: 100,
  blackThreshold: 100,
  hashMb: 64,
  threads: 1,
};

function buildParentMap(root) {
  const map = new Map();
  const stack = [root];
  while (stack.length) {
    const n = stack.pop();
    for (const c of n.children) {
      map.set(c.id, n);
      stack.push(c);
    }
  }
  return map;
}

// Turn a raw engine/handshake error into plain language for the user.
function friendlyEngineError(err, source) {
  const msg = (err && err.message) || String(err);
  if (source === "local" && /uciok|readyok/i.test(msg)) {
    return (
      "That program started but didn't respond like a chess engine. Make sure " +
      "the path points to a UCI engine (such as Stockfish)."
    );
  }
  return msg;
}

function download(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function App() {
  const engineRef = useRef(null);
  const abortRef = useRef(null);

  const [engineState, setEngineState] = useState("loading"); // loading|ready|error
  const [engineError, setEngineError] = useState("");
  const [engineCaps, setEngineCaps] = useState({ maxThreads: 1, maxHash: 1024 });
  const [engineSource, setEngineSource] = useState(
    () => localStorage.getItem("engineSource") || "builtin"
  );
  const [enginePath, setEnginePath] = useState(
    () => localStorage.getItem("enginePath") || ""
  );
  const [engineName, setEngineName] = useState("");

  const [mode, setMode] = useState("pgn");
  const [pgnText, setPgnText] = useState("");
  const [fenText, setFenText] = useState(START_FEN);
  const [boardMoves, setBoardMoves] = useState([]);

  const [settings, setSettings] = useState(DEFAULT_SETTINGS);

  const [tree, setTree] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState("");
  const [helpOpen, setHelpOpen] = useState(false);

  // Build (or rebuild) the engine for the chosen source and connect to it.
  const startEngine = useCallback(async (source, path = "") => {
    if (engineRef.current) {
      try {
        engineRef.current.dispose();
      } catch (e) {
        /* ignore */
      }
      engineRef.current = null;
    }

    setEngineState("loading");
    setEngineError("");
    setEngineName("");

    const engine =
      source === "local"
        ? isDesktop()
          ? new DesktopEngine({ enginePath: path })
          : new BridgeEngine({ enginePath: path })
        : new StockfishEngine();
    engineRef.current = engine;

    // Surface failures that happen AFTER a successful connect (engine crash,
    // bridge closed, etc.) instead of leaving a stale "ready" state.
    engine.onFatal = (err) => {
      if (engineRef.current !== engine) return;
      setEngineState("error");
      setEngineError(friendlyEngineError(err, source));
    };

    try {
      await engine.init({
        hashMb: DEFAULT_SETTINGS.hashMb,
        threads: DEFAULT_SETTINGS.threads,
      });
      if (engineRef.current !== engine) return;
      setEngineState("ready");
      setEngineName(engine.name || "");
      // A native engine may advertise absurd limits (hundreds of threads, terabytes
      // of hash). Honour the engine's real reported max, but keep the sliders
      // meaningful by clamping to what this machine can actually use.
      const reportedThreads = engine.maxThreads || 1;
      const reportedHash = engine.maxHash || 1024;
      if (source === "local") {
        const cpuCap = navigator.hardwareConcurrency || 1;
        // navigator.deviceMemory is in GB (spec-capped at 8); fall back to 4 GB.
        const memCapMb = (navigator.deviceMemory || 4) * 1024;
        setEngineCaps({
          maxThreads: Math.max(1, Math.min(reportedThreads, cpuCap)),
          maxHash: Math.min(reportedHash, memCapMb),
        });
      } else {
        // Built-in browser engine: keep the conservative defaults.
        setEngineCaps({
          maxThreads: reportedThreads,
          maxHash: Math.min(reportedHash, 1024),
        });
      }
    } catch (err) {
      if (engineRef.current !== engine) return;
      setEngineState("error");
      setEngineError(friendlyEngineError(err, source));
    }
  }, []);

  // Start the saved engine once on load, and dispose on unmount.
  useEffect(() => {
    startEngine(engineSource, enginePath);
    return () => {
      if (engineRef.current) {
        try {
          engineRef.current.dispose();
        } catch (e) {
          /* ignore */
        }
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleChooseBuiltin() {
    setEngineSource("builtin");
    localStorage.setItem("engineSource", "builtin");
    startEngine("builtin");
  }

  function handleConnectLocal(path) {
    const trimmed = (path || "").trim();
    setEngineSource("local");
    setEnginePath(trimmed);
    localStorage.setItem("engineSource", "local");
    localStorage.setItem("enginePath", trimmed);
    startEngine("local", trimmed);
  }

  const parentMap = useMemo(
    () => (tree ? buildParentMap(tree) : new Map()),
    [tree]
  );

  // Position the user is building by dragging pieces (board input mode).
  const boardSetupFen = useMemo(() => {
    const c = new Chess();
    for (const m of boardMoves) {
      try {
        c.move(m.san ?? { from: m.uci.slice(0, 2), to: m.uci.slice(2, 4) });
      } catch (e) {
        break;
      }
    }
    return c.fen();
  }, [boardMoves]);

  const boardInteractive = mode === "board" && !running && !selectedNode;
  const boardFen = selectedNode
    ? selectedNode.fen
    : mode === "board"
    ? boardSetupFen
    : fenText || START_FEN;

  function handlePieceDrop(from, to) {
    if (!boardInteractive) return false;
    const c = new Chess(boardSetupFen);
    let mv;
    try {
      mv = c.move({ from, to, promotion: "q" });
    } catch (e) {
      return false;
    }
    if (!mv) return false;
    setBoardMoves((prev) => [...prev, { san: mv.san, uci: mv.lan }]);
    return true;
  }

  function undoBoardMove() {
    setBoardMoves((prev) => prev.slice(0, -1));
  }

  function resetBoard() {
    setBoardMoves([]);
    setTree(null);
    setSelectedNode(null);
  }

  function getInputParams() {
    if (mode === "board") {
      return { startFen: START_FEN, gameMoves: boardMoves };
    }
    if (mode === "pgn") {
      if (!pgnText.trim()) throw new Error("Please paste a PGN game first.");
      const { startFen, gameMoves } = parsePgn(pgnText);
      if (!gameMoves.length) {
        throw new Error("No valid moves found in the PGN.");
      }
      return { startFen, gameMoves };
    }
    const fen = fenText.trim();
    if (!fen) throw new Error("Please enter a FEN position first.");
    try {
      // Validate.
      // eslint-disable-next-line no-new
      new Chess(fen);
    } catch (e) {
      throw new Error("That FEN is not valid.");
    }
    return { startFen: fen, gameMoves: [] };
  }

  async function handleRun() {
    setError("");
    if (engineState !== "ready") {
      setError("The engine is not ready yet.");
      return;
    }
    let params;
    try {
      params = getInputParams();
    } catch (e) {
      setError(e.message);
      return;
    }

    setRunning(true);
    setProgress({ analyzed: 0, queued: 0, depth: 0, line: "" });
    setTree(null);
    setSelectedNode(null);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      await engineRef.current.newGame();
      await engineRef.current.configure({
        hashMb: settings.hashMb,
        threads: settings.threads,
      });
      const root = await generateTree(
        engineRef.current,
        { ...params, settings },
        (p) => setProgress({ ...p }),
        controller.signal
      );
      setTree(root);
      setSelectedNode(root);
    } catch (e) {
      setError("Analysis failed: " + (e.message || String(e)));
    } finally {
      setRunning(false);
      abortRef.current = null;
    }
  }

  function handleStop() {
    if (abortRef.current) abortRef.current.abort();
    if (engineRef.current) engineRef.current.stop();
  }

  function navParent() {
    if (!selectedNode) return;
    const p = parentMap.get(selectedNode.id);
    if (p) setSelectedNode(p);
  }
  function navChild() {
    if (!selectedNode || !selectedNode.children.length) return;
    setSelectedNode(selectedNode.children[0]);
  }

  const analyzedCount = tree ? countAnalyzedNodes(tree) : 0;
  const maxProgress = progress
    ? Math.max(progress.analyzed, progress.analyzed + progress.queued)
    : 1;
  const progressPct =
    progress && maxProgress > 0
      ? Math.round((progress.analyzed / maxProgress) * 100)
      : 0;

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">♞</div>
          <div>
            <h1>Chess Tree Analyzer</h1>
            <p>Deep variation trees, powered by Stockfish in your browser</p>
          </div>
        </div>
        <div className="topbar-right">
          <button
            className="help-link"
            onClick={() => setHelpOpen(true)}
            title="Open the user guide — how to use every part of this app"
          >
            <span aria-hidden="true">?</span> Help
          </button>
          <div
            className="engine-status"
            title={
              engineState === "ready"
                ? engineSource === "local"
                  ? "Connected to your own engine through the local bridge"
                  : "The built-in chess engine is loaded and ready to analyse"
                : engineState === "loading"
                ? engineSource === "local"
                  ? "Connecting to your own engine…"
                  : "The chess engine is still loading in your browser"
                : "The chess engine is not connected"
            }
          >
            <span className={"dot " + engineState} />
            {engineState === "loading" &&
              (engineSource === "local" ? "Connecting…" : "Loading engine…")}
            {engineState === "ready" &&
              (engineName
                ? engineName
                : engineSource === "local"
                ? "Engine connected"
                : "Engine ready")}
            {engineState === "error" && "Engine not connected"}
          </div>
        </div>
      </header>

      <HelpModal open={helpOpen} onClose={() => setHelpOpen(false)} />

      <div className="layout">
        <div className="column left">
          {engineState === "error" && engineSource !== "local" && (
            <div className="error-box">
              Could not start the engine: {engineError}
            </div>
          )}
          {error && <div className="error-box">{error}</div>}

          <EnginePanel
            source={engineSource}
            path={enginePath}
            status={engineState}
            error={engineError}
            name={engineName}
            desktop={isDesktop()}
            onChooseBuiltin={handleChooseBuiltin}
            onConnectLocal={handleConnectLocal}
            onBrowse={() =>
              isDesktop() ? window.desktop.pickEngine() : Promise.resolve(null)
            }
            disabled={running}
          />

          <InputPanel
            mode={mode}
            setMode={setMode}
            pgnText={pgnText}
            setPgnText={setPgnText}
            fenText={fenText}
            setFenText={setFenText}
            boardMoves={boardMoves}
            onUndoBoardMove={undoBoardMove}
            onResetBoard={resetBoard}
            disabled={running}
          />

          <SettingsPanel
            settings={settings}
            onChange={setSettings}
            disabled={running}
            maxThreads={engineCaps.maxThreads}
            maxHash={engineCaps.maxHash}
            localEngine={engineSource === "local"}
          />

          <div className="card">
            {!running ? (
              <button
                className="btn btn-primary"
                onClick={handleRun}
                disabled={engineState !== "ready"}
                title="Start analysing the chosen position and build the variation tree"
              >
                ▶ Generate Tree
              </button>
            ) : (
              <button
                className="btn btn-danger"
                onClick={handleStop}
                title="Stop the analysis now and keep whatever has been worked out so far"
              >
                ■ Stop Analysis
              </button>
            )}

            {progress && (
              <div className="progress">
                <div className="progress-bar">
                  <span style={{ width: `${progressPct}%` }} />
                </div>
                <div className="progress-text">
                  <span>{progress.analyzed} analyzed</span>
                  <span>{progress.queued} queued</span>
                </div>
                {progress.line && (
                  <div className="progress-line" title={progress.line}>
                    Exploring: {progress.line}
                  </div>
                )}
              </div>
            )}

            {tree && !running && (
              <div className="btn-group" style={{ marginTop: 12 }}>
                <button
                  className="btn btn-secondary"
                  onClick={() =>
                    download(
                      "chess-tree.pgn",
                      treeToPgn(tree),
                      "application/x-chess-pgn"
                    )
                  }
                  title="Download the whole tree as a PGN file (opens in ChessBase, Lichess, and most chess software)"
                >
                  ↓ PGN
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() =>
                    download(
                      "chess-tree.json",
                      treeToJson(tree),
                      "application/json"
                    )
                  }
                  title="Download the tree as structured JSON data for use in your own scripts or tools"
                >
                  ↓ JSON
                </button>
              </div>
            )}

            {tree && !running && (
              <p className="muted" style={{ marginTop: 10 }}>
                {analyzedCount} analyzed positions in the tree.
              </p>
            )}
          </div>
        </div>

        <div className="column center">
          <div className="board-wrap">
            <Board
              fen={boardFen}
              draggable={boardInteractive}
              onPieceDrop={handlePieceDrop}
            />
          </div>
          <div className="board-nav">
            <button
              className="btn btn-secondary"
              onClick={navParent}
              disabled={!selectedNode || !parentMap.get(selectedNode.id)}
              title="Go to the previous move (the parent of the current move in the tree)"
            >
              ← Back
            </button>
            <button
              className="btn btn-secondary"
              onClick={navChild}
              disabled={!selectedNode || !selectedNode.children.length}
              title="Go forward into the first follow-up move of the current move"
            >
              Forward →
            </button>
          </div>
          <div className="board-meta">
            <strong style={{ fontSize: 13 }}>
              {selectedNode && selectedNode.move
                ? `Move: ${selectedNode.move.san}`
                : "Starting position"}
            </strong>
            <div className="fen">{boardFen}</div>
          </div>
        </div>

        <VariationTree
          root={tree}
          selectedId={selectedNode ? selectedNode.id : null}
          onSelect={setSelectedNode}
        />
      </div>
    </div>
  );
}
