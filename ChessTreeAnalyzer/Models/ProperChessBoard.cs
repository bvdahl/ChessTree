using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ChessTreeAnalyzer.Models
{
    // A proper chess board implementation that maintains legal positions
    public class ProperChessBoard
    {
        private char[,] board = new char[8, 8];
        private bool whiteToMove;
        private string castlingRights;
        private string enPassantSquare;
        private int halfmoveClock;
        private int fullmoveNumber;
        
        // Cache the current FEN to avoid recalculation
        private string cachedFen;
        
        public bool WhiteToMove => whiteToMove;
        public int MoveNumber => fullmoveNumber;
        public string FEN => cachedFen;
        
        public ProperChessBoard(string fen = null)
        {
            if (string.IsNullOrEmpty(fen))
                fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
            
            ParseFEN(fen);
            cachedFen = fen;
        }
        
        private void ParseFEN(string fen)
        {
            var parts = fen.Split(' ');
            if (parts.Length < 6)
                throw new ArgumentException($"Invalid FEN: {fen}");
            
            // Parse board position
            var ranks = parts[0].Split('/');
            if (ranks.Length != 8)
                throw new ArgumentException($"Invalid FEN board: {parts[0]}");
            
            for (int rank = 7; rank >= 0; rank--)
            {
                int file = 0;
                foreach (char c in ranks[7 - rank])
                {
                    if (char.IsDigit(c))
                    {
                        int emptySquares = c - '0';
                        for (int i = 0; i < emptySquares && file < 8; i++)
                        {
                            board[rank, file++] = ' ';
                        }
                    }
                    else if (file < 8)
                    {
                        board[rank, file++] = c;
                    }
                }
            }
            
            // Parse other FEN components
            whiteToMove = parts[1] == "w";
            castlingRights = parts[2];
            enPassantSquare = parts[3];
            halfmoveClock = int.Parse(parts[4]);
            fullmoveNumber = int.Parse(parts[5]);
        }
        
        public ProperChessBoard MakeMove(string uciMove)
        {
            // Parse UCI move format (e.g., "e2e4", "e7e8q")
            if (uciMove.Length < 4)
                return new ProperChessBoard(cachedFen);
            
            int fromFile = uciMove[0] - 'a';
            int fromRank = uciMove[1] - '1';
            int toFile = uciMove[2] - 'a';
            int toRank = uciMove[3] - '1';
            
            // Validate coordinates
            if (fromFile < 0 || fromFile > 7 || fromRank < 0 || fromRank > 7 ||
                toFile < 0 || toFile > 7 || toRank < 0 || toRank > 7)
            {
                return new ProperChessBoard(cachedFen);
            }
            
            // Create a new board state
            var newBoard = new char[8, 8];
            Array.Copy(board, newBoard, 64);
            
            // Get the piece being moved
            char piece = newBoard[fromRank, fromFile];
            char captured = newBoard[toRank, toFile];
            
            // Make the move
            newBoard[toRank, toFile] = piece;
            newBoard[fromRank, fromFile] = ' ';
            
            // Handle castling
            if (char.ToLower(piece) == 'k' && Math.Abs(toFile - fromFile) == 2)
            {
                // King-side castling
                if (toFile == 6)
                {
                    newBoard[fromRank, 5] = newBoard[fromRank, 7]; // Move rook
                    newBoard[fromRank, 7] = ' ';
                }
                // Queen-side castling
                else if (toFile == 2)
                {
                    newBoard[fromRank, 3] = newBoard[fromRank, 0]; // Move rook
                    newBoard[fromRank, 0] = ' ';
                }
            }
            
            // Handle en passant capture
            if (char.ToLower(piece) == 'p' && toFile != fromFile && captured == ' ')
            {
                // This is an en passant capture
                int capturedPawnRank = whiteToMove ? toRank - 1 : toRank + 1;
                newBoard[capturedPawnRank, toFile] = ' ';
            }
            
            // Handle pawn promotion
            if (uciMove.Length == 5)
            {
                char promotionPiece = uciMove[4];
                if (whiteToMove)
                    promotionPiece = char.ToUpper(promotionPiece);
                newBoard[toRank, toFile] = promotionPiece;
            }
            
            // Update castling rights
            string newCastlingRights = UpdateCastlingRights(piece, fromFile, fromRank, toFile, toRank, captured);
            
            // Update en passant square
            string newEnPassant = "-";
            if (char.ToLower(piece) == 'p' && Math.Abs(toRank - fromRank) == 2)
            {
                int epRank = whiteToMove ? fromRank + 1 : fromRank - 1;
                newEnPassant = $"{(char)('a' + fromFile)}{epRank + 1}";
            }
            
            // Update move counters
            int newHalfmove = (char.ToLower(piece) == 'p' || captured != ' ') ? 0 : halfmoveClock + 1;
            int newFullmove = whiteToMove ? fullmoveNumber : fullmoveNumber + 1;
            
            // Build new FEN
            string newFen = BuildFEN(newBoard, !whiteToMove, newCastlingRights, newEnPassant, newHalfmove, newFullmove);
            
            return new ProperChessBoard(newFen);
        }
        
        private string UpdateCastlingRights(char piece, int fromFile, int fromRank, int toFile, int toRank, char captured)
        {
            if (castlingRights == "-")
                return "-";
            
            var rights = new StringBuilder(castlingRights);
            
            // King moves
            if (piece == 'K')
            {
                rights.Replace("K", "").Replace("Q", "");
            }
            else if (piece == 'k')
            {
                rights.Replace("k", "").Replace("q", "");
            }
            
            // Rook moves or is captured
            if (piece == 'R' || captured == 'R')
            {
                if (fromRank == 0 || toRank == 0)
                {
                    if (fromFile == 7 || toFile == 7) rights.Replace("K", "");
                    if (fromFile == 0 || toFile == 0) rights.Replace("Q", "");
                }
            }
            if (piece == 'r' || captured == 'r')
            {
                if (fromRank == 7 || toRank == 7)
                {
                    if (fromFile == 7 || toFile == 7) rights.Replace("k", "");
                    if (fromFile == 0 || toFile == 0) rights.Replace("q", "");
                }
            }
            
            string result = rights.ToString();
            return string.IsNullOrEmpty(result) ? "-" : result;
        }
        
        private string BuildFEN(char[,] board, bool whiteToMove, string castling, string enPassant, int halfmove, int fullmove)
        {
            var fen = new StringBuilder();
            
            // Build board position
            for (int rank = 7; rank >= 0; rank--)
            {
                int emptyCount = 0;
                for (int file = 0; file < 8; file++)
                {
                    char piece = board[rank, file];
                    if (piece == ' ')
                    {
                        emptyCount++;
                    }
                    else
                    {
                        if (emptyCount > 0)
                        {
                            fen.Append(emptyCount);
                            emptyCount = 0;
                        }
                        fen.Append(piece);
                    }
                }
                if (emptyCount > 0)
                {
                    fen.Append(emptyCount);
                }
                if (rank > 0)
                {
                    fen.Append('/');
                }
            }
            
            // Add other FEN components
            fen.Append(' ');
            fen.Append(whiteToMove ? 'w' : 'b');
            fen.Append(' ');
            fen.Append(castling);
            fen.Append(' ');
            fen.Append(enPassant);
            fen.Append(' ');
            fen.Append(halfmove);
            fen.Append(' ');
            fen.Append(fullmove);
            
            return fen.ToString();
        }
        
        public string GetPieceSymbol(int square)
        {
            int rank = square / 8;
            int file = square % 8;
            
            if (rank < 0 || rank > 7 || file < 0 || file > 7)
                return "";
            
            char piece = board[rank, file];
            if (piece == ' ')
                return "";
            
            // Unicode chess symbols
            var symbols = new Dictionary<char, string>
            {
                ['K'] = "♔", ['Q'] = "♕", ['R'] = "♖", ['B'] = "♗", ['N'] = "♘", ['P'] = "♙",
                ['k'] = "♚", ['q'] = "♛", ['r'] = "♜", ['b'] = "♝", ['n'] = "♞", ['p'] = "♟"
            };
            
            return symbols.ContainsKey(piece) ? symbols[piece] : piece.ToString();
        }
        
        public bool IsGameOver()
        {
            // Simplified game over check - would need full chess rules for complete implementation
            return false;
        }
        
        public string GetPieceAt(int square)
        {
            int rank = square / 8;
            int file = square % 8;
            if (rank < 0 || rank > 7 || file < 0 || file > 7)
                return "";
            char piece = board[rank, file];
            return piece == ' ' ? "" : piece.ToString();
        }
        
        public string ToDisplayString()
        {
            var result = new StringBuilder();
            for (int rank = 7; rank >= 0; rank--)
            {
                result.Append($"{rank + 1} ");
                for (int file = 0; file < 8; file++)
                {
                    char piece = board[rank, file];
                    result.Append(piece == ' ' ? "." : piece.ToString());
                    result.Append(" ");
                }
                result.AppendLine();
            }
            result.AppendLine("  a b c d e f g h");
            result.AppendLine($"To move: {(whiteToMove ? "White" : "Black")}");
            result.AppendLine($"Move: {fullmoveNumber}");
            return result.ToString();
        }
    }
}