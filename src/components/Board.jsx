import React from "react";
import { Chessboard } from "react-chessboard";

export default function Board({
  fen,
  draggable = false,
  onPieceDrop,
  animationMs = 300,
}) {
  return (
    <Chessboard
      position={fen}
      animationDuration={animationMs}
      arePiecesDraggable={draggable}
      onPieceDrop={
        onPieceDrop ? (from, to) => onPieceDrop(from, to) : undefined
      }
      customBoardStyle={{
        borderRadius: "10px",
        boxShadow: "0 8px 24px rgba(0,0,0,0.45)",
      }}
      customDarkSquareStyle={{ backgroundColor: "#3a5a40" }}
      customLightSquareStyle={{ backgroundColor: "#dad7cd" }}
    />
  );
}
