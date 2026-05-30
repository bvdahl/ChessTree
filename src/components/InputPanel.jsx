import React, { useRef } from "react";

const SAMPLE_PGN = `[Event "Sample"]

1. e4 e5 2. Nc3 Nf6 3. f4 d5 4. fxe5 Nxe4 5. d3 Nxc3 6. bxc3 d4 7. Nf3 dxc3 *`;

export default function InputPanel({
  mode,
  setMode,
  pgnText,
  setPgnText,
  fenText,
  setFenText,
  boardMoves,
  onUndoBoardMove,
  onResetBoard,
  disabled,
}) {
  const fileRef = useRef(null);

  function handleFile(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setPgnText(String(reader.result || ""));
    reader.readAsText(file);
    // Allow re-selecting the same file later.
    e.target.value = "";
  }

  return (
    <div className="card" style={{ opacity: disabled ? 0.6 : 1 }}>
      <h2>Position Input</h2>
      <div className="tabs">
        <button
          className={"tab" + (mode === "pgn" ? " active" : "")}
          onClick={() => setMode("pgn")}
          disabled={disabled}
          title="Analyse from a recorded game: paste or upload a PGN game"
        >
          PGN Game
        </button>
        <button
          className={"tab" + (mode === "fen" ? " active" : "")}
          onClick={() => setMode("fen")}
          disabled={disabled}
          title="Analyse a single position from its FEN code"
        >
          FEN Position
        </button>
        <button
          className={"tab" + (mode === "board" ? " active" : "")}
          onClick={() => setMode("board")}
          disabled={disabled}
          title="Set up a position by dragging the pieces on the board"
        >
          Play on Board
        </button>
      </div>

      {mode === "pgn" && (
        <div className="field">
          <label>Paste a PGN game (moves form the main line)</label>
          <textarea
            value={pgnText}
            onChange={(e) => setPgnText(e.target.value)}
            placeholder="1. e4 e5 2. Nf3 ..."
            disabled={disabled}
            title="Paste the moves of a game here. These moves become the main line the analysis starts from."
          />
          <input
            ref={fileRef}
            type="file"
            accept=".pgn,.txt"
            style={{ display: "none" }}
            onChange={handleFile}
          />
          <div className="btn-group" style={{ marginTop: 8 }}>
            <button
              className="btn btn-secondary"
              onClick={() => fileRef.current && fileRef.current.click()}
              disabled={disabled}
              title="Load a .pgn (or .txt) game file from your computer"
            >
              ↑ Upload PGN file
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setPgnText(SAMPLE_PGN)}
              disabled={disabled}
              title="Fill the box with an example game so you can try the app right away"
            >
              Load sample game
            </button>
          </div>
        </div>
      )}

      {mode === "fen" && (
        <div className="field">
          <label>Enter a FEN position</label>
          <input
            type="text"
            value={fenText}
            onChange={(e) => setFenText(e.target.value)}
            placeholder="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            disabled={disabled}
            title="Paste a FEN code describing the exact position you want to analyse"
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
            title="Reset the FEN box to the normal chess starting position"
          >
            Use starting position
          </button>
        </div>
      )}

      {mode === "board" && (
        <div className="field">
          <label>
            Drag pieces on the board to play into a position. Those moves become
            the main line.
          </label>
          <div className="moves-preview">
            {boardMoves && boardMoves.length
              ? boardMoves.map((m) => m.san).join(" ")
              : "No moves yet — the analysis will start from the position you set up."}
          </div>
          <div className="btn-group" style={{ marginTop: 8 }}>
            <button
              className="btn btn-secondary"
              onClick={onUndoBoardMove}
              disabled={disabled || !boardMoves || !boardMoves.length}
              title="Take back the last move you played on the board"
            >
              ↶ Undo move
            </button>
            <button
              className="btn btn-secondary"
              onClick={onResetBoard}
              disabled={disabled || !boardMoves || !boardMoves.length}
              title="Clear all your moves and start over from the initial position"
            >
              ⟲ Reset board
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
