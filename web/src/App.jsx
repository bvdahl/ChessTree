import React, { useEffect, useMemo, useRef, useState } from "react";
import { Chess } from "chess.js";
import { StockfishEngine } from "./engine/stockfishEngine.js";
import { generateTree, parsePgn } from "./analysis/analysisEngine.js";
import { treeToPgn, treeToJson, countAnalyzedNodes } from "./analysis/output.js";
import Board from "./components/Board.jsx";
import VariationTree from "./components/VariationTree.jsx";
import SettingsPanel from "./components/SettingsPanel.jsx";
import InputPanel from "./components/InputPanel.jsx";

const START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

const DEFAULT_SETTINGS = {
  maxDepth: 4,
  moveTimeMs: 1500,
  whiteMoves: 3,
  blackMoves: 3,
  whiteThreshold: 100,
  blackThreshold: 100,
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

  const [mode, setMode] = useState("pgn");
  const [pgnText, setPgnText] = useState("");
  const [fenText, setFenText] = useState(START_FEN);

  const [settings, setSettings] = useState(DEFAULT_SETTINGS);

  const [tree, setTree] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const engine = new StockfishEngine();
    engineRef.current = engine;
    engine
      .init({ hashMb: 64, threads: 1 })
      .then(() => setEngineState("ready"))
      .catch((err) => {
        setEngineState("error");
        setEngineError(err.message || String(err));
      });
    return () => engine.dispose();
  }, []);

  const parentMap = useMemo(
    () => (tree ? buildParentMap(tree) : new Map()),
    [tree]
  );

  const boardFen = selectedNode ? selectedNode.fen : fenText || START_FEN;

  function getInputParams() {
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
        <div className="engine-status">
          <span className={"dot " + engineState} />
          {engineState === "loading" && "Loading engine…"}
          {engineState === "ready" && "Engine ready"}
          {engineState === "error" && "Engine failed"}
        </div>
      </header>

      <div className="layout">
        <div className="column left">
          {engineState === "error" && (
            <div className="error-box">
              Could not start the engine: {engineError}
            </div>
          )}
          {error && <div className="error-box">{error}</div>}

          <InputPanel
            mode={mode}
            setMode={setMode}
            pgnText={pgnText}
            setPgnText={setPgnText}
            fenText={fenText}
            setFenText={setFenText}
            disabled={running}
          />

          <SettingsPanel
            settings={settings}
            onChange={setSettings}
            disabled={running}
          />

          <div className="card">
            {!running ? (
              <button
                className="btn btn-primary"
                onClick={handleRun}
                disabled={engineState !== "ready"}
              >
                ▶ Generate Tree
              </button>
            ) : (
              <button className="btn btn-danger" onClick={handleStop}>
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
            <Board fen={boardFen} />
          </div>
          <div className="board-nav">
            <button
              className="btn btn-secondary"
              onClick={navParent}
              disabled={!selectedNode || !parentMap.get(selectedNode.id)}
            >
              ← Back
            </button>
            <button
              className="btn btn-secondary"
              onClick={navChild}
              disabled={!selectedNode || !selectedNode.children.length}
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
