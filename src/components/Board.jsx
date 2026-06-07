import React from "react";
import { Chessboard } from "react-chessboard";

// A soft amber wash on the from/to squares of the last move played into the
// shown position (used to follow the move under analysis, and when viewing a
// move in the tree).
const HIGHLIGHT_STYLE = { background: "rgba(227, 179, 65, 0.45)" };

export default function Board({
  fen,
  draggable = false,
  onPieceDrop,
  animationMs = 300,
  highlight = null,
}) {
  const squareStyles = {};
  if (highlight && highlight.from && highlight.to) {
    squareStyles[highlight.from] = HIGHLIGHT_STYLE;
    squareStyles[highlight.to] = HIGHLIGHT_STYLE;
  }

  return (
    <Chessboard
      position={fen}
      animationDuration={animationMs}
      arePiecesDraggable={draggable}
      onPieceDrop={
        onPieceDrop ? (from, to) => onPieceDrop(from, to) : undefined
      }
      customSquareStyles={squareStyles}
      customBoardStyle={{
        borderRadius: "10px",
        boxShadow: "0 8px 24px rgba(0,0,0,0.45)",
      }}
      customDarkSquareStyle={{ backgroundColor: "#3a5a40" }}
      customLightSquareStyle={{ backgroundColor: "#dad7cd" }}
    />
  );
}
