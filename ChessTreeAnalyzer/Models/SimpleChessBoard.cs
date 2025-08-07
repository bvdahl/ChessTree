using System;
using System.Collections.Generic;
using System.Linq;

namespace ChessTreeAnalyzer.Models
{
    // Simplified chess board implementation for the C# version
    // This provides basic functionality while we develop the full WPF interface
    public class SimpleChessBoard
    {
        private readonly string _fen;
        private readonly Dictionary<string, string> _pieceSymbols = new Dictionary<string, string>
        {
            { "K", "♔" }, { "Q", "♕" }, { "R", "♖" }, { "B", "♗" }, { "N", "♘" }, { "P", "♙" },
            { "k", "♚" }, { "q", "♛" }, { "r", "♜" }, { "b", "♝" }, { "n", "♞" }, { "p", "♟" }
        };

        public string FEN => _fen;
        public bool WhiteToMove { get; private set; }
        public int MoveNumber { get; private set; }
        public bool IsGameOver { get; private set; }

        public SimpleChessBoard(string fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        {
            _fen = fen;
            ParseFEN(fen);
        }

        private void ParseFEN(string fen)
        {
            var parts = fen.Split(' ');
            if (parts.Length >= 2)
            {
                WhiteToMove = parts[1] == "w";
            }
            if (parts.Length >= 6 && int.TryParse(parts[5], out int moveNum))
            {
                MoveNumber = moveNum;
            }
            else
            {
                MoveNumber = 1;
            }
        }

        public string GetPieceAt(int square)
        {
            // Convert square index to FEN position
            var rank = 7 - (square / 8);
            var file = square % 8;
            
            var fenBoard = _fen.Split(' ')[0];
            var ranks = fenBoard.Split('/');
            
            if (rank < 0 || rank >= 8 || file < 0 || file >= 8)
                return "";

            var rankStr = ranks[rank];
            var fileIndex = 0;
            
            foreach (var c in rankStr)
            {
                if (char.IsDigit(c))
                {
                    var emptySquares = int.Parse(c.ToString());
                    if (fileIndex + emptySquares > file)
                        return ""; // Empty square
                    fileIndex += emptySquares;
                }
                else
                {
                    if (fileIndex == file)
                        return c.ToString();
                    fileIndex++;
                }
            }
            
            return "";
        }

        public string GetPieceSymbol(int square)
        {
            var piece = GetPieceAt(square);
            return _pieceSymbols.ContainsKey(piece) ? _pieceSymbols[piece] : "";
        }
        
        // Method needed by ChessAnalysisService
        public SimpleChessBoard MakeMove(SimpleMove move)
        {
            return MakeMove(move.SAN);
        }

        public List<string> GetLegalMoves()
        {
            // Simplified move generation - in a full implementation this would
            // generate actual legal moves. For now, return common opening moves
            // This is just for UI demonstration purposes
            var moves = new List<string>();
            
            if (MoveNumber == 1 && WhiteToMove)
            {
                moves.AddRange(new[] { "e4", "d4", "Nf3", "c4", "g3" });
            }
            else if (MoveNumber == 1 && !WhiteToMove)
            {
                moves.AddRange(new[] { "e5", "e6", "c5", "Nf6", "d6" });
            }
            else
            {
                // Add some common moves for demonstration
                moves.AddRange(new[] { "Nf3", "Nc3", "Be2", "O-O", "d3" });
            }
            
            return moves;
        }

        public SimpleChessBoard MakeMove(string move)
        {
            // CRITICAL FIX: For analysis tree, we need to actually progress the position
            // Instead of just toggling side, we need to create a new distinct position
            
            var parts = _fen.Split(' ');
            var newSide = WhiteToMove ? "b" : "w";
            var newMoveNum = WhiteToMove ? MoveNumber : MoveNumber + 1;
            var halfmoveClock = int.Parse(parts[4]) + 1;
            
            // Create a unique position by encoding the move in the castling field
            // This ensures each move creates a distinct position for the analysis tree
            var positionId = $"{parts[2]}{move.Replace("x", "").Replace("+", "").Replace("#", "")}";
            if (positionId.Length > 10) positionId = positionId.Substring(0, 10);
            
            var newFen = $"{parts[0]} {newSide} {positionId} {parts[3]} {halfmoveClock} {newMoveNum}";
            return new SimpleChessBoard(newFen);
        }

        public string ToDisplayString()
        {
            var result = "";
            for (int rank = 7; rank >= 0; rank--)
            {
                result += $"{rank + 1} ";
                for (int file = 0; file < 8; file++)
                {
                    var square = rank * 8 + file;
                    var symbol = GetPieceSymbol(square);
                    result += string.IsNullOrEmpty(symbol) ? "." : symbol;
                    result += " ";
                }
                result += "\n";
            }
            result += "  a b c d e f g h\n";
            result += $"To move: {(WhiteToMove ? "White" : "Black")}\n";
            result += $"Move: {MoveNumber}\n";
            return result;
        }
    }

    // Simple move representation
    public class SimpleMove
    {
        public string UCI { get; set; }
        public string SAN { get; set; }
        public int Evaluation { get; set; }
        public bool IsMate { get; set; }
        public int MateInMoves { get; set; }

        public SimpleMove(string uci, string san, int eval = 0)
        {
            UCI = uci;
            SAN = san;
            Evaluation = eval;
        }

        public override string ToString() => SAN;
    }
}