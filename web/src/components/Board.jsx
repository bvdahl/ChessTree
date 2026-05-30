import React from "react";
import { Chessboard } from "react-chessboard";

export default function Board({ fen }) {
  return (
    <Chessboard
      position={fen}
      arePiecesDraggable={false}
      customBoardStyle={{
        borderRadius: "10px",
        boxShadow: "0 8px 24px rgba(0,0,0,0.45)",
      }}
      customDarkSquareStyle={{ backgroundColor: "#3a5a40" }}
      customLightSquareStyle={{ backgroundColor: "#dad7cd" }}
    />
  );
}
