import React from "react";

const SAMPLE_PGN = `[Event "Sample"]

1. e4 e5 2. Nc3 Nf6 3. f4 d5 4. fxe5 Nxe4 5. d3 Nxc3 6. bxc3 d4 7. Nf3 dxc3 *`;

export default function InputPanel({
  mode,
  setMode,
  pgnText,
  setPgnText,
  fenText,
  setFenText,
  disabled,
}) {
  return (
    <div className="card" style={{ opacity: disabled ? 0.6 : 1 }}>
      <h2>Position Input</h2>
      <div className="tabs">
        <button
          className={"tab" + (mode === "pgn" ? " active" : "")}
          onClick={() => setMode("pgn")}
          disabled={disabled}
        >
          PGN Game
        </button>
        <button
          className={"tab" + (mode === "fen" ? " active" : "")}
          onClick={() => setMode("fen")}
          disabled={disabled}
        >
          FEN Position
        </button>
      </div>

      {mode === "pgn" ? (
        <div className="field">
          <label>Paste a PGN game (moves form the main line)</label>
          <textarea
            value={pgnText}
            onChange={(e) => setPgnText(e.target.value)}
            placeholder="1. e4 e5 2. Nf3 ..."
            disabled={disabled}
          />
          <button
            className="btn btn-secondary"
            style={{ marginTop: 8 }}
            onClick={() => setPgnText(SAMPLE_PGN)}
            disabled={disabled}
          >
            Load sample game
          </button>
        </div>
      ) : (
        <div className="field">
          <label>Enter a FEN position</label>
          <input
            type="text"
            value={fenText}
            onChange={(e) => setFenText(e.target.value)}
            placeholder="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            disabled={disabled}
          />
          <button
            className="btn btn-secondary"
            style={{ marginTop: 8 }}
            onClick={() =>
              setFenText(
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
              )
            }
            disabled={disabled}
          >
            Use starting position
          </button>
        </div>
      )}
    </div>
  );
}
