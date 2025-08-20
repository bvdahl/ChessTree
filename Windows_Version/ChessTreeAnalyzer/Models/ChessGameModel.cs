using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;
using ChessDotNet;

namespace ChessTreeAnalyzer.Models
{
    public class ChessGameModel
    {
        public string GameInfo { get; set; } = "";
        public ProperChessBoard InitialPosition { get; set; }
        public List<SimpleMove> GameMoves { get; set; } = new List<SimpleMove>();
        public AnalysisTreeNode AnalysisTree { get; set; }
        public string SourceFile { get; set; } = "";
        public DateTime CreatedDate { get; set; } = DateTime.Now;
        public List<string> PositionHistory { get; set; } = new List<string>();

        public ChessGameModel()
        {
            InitialPosition = new ProperChessBoard();
        }



        public static ChessGameModel LoadFromPGN(string filePath)
        {
            var game = new ChessGameModel
            {
                SourceFile = filePath
            };

            try
            {
                // Read PGN file
                var pgnContent = System.IO.File.ReadAllText(filePath);
                Console.WriteLine($"Reading PGN file: {filePath}");
                Console.WriteLine($"PGN content length: {pgnContent.Length} characters");
                
                // Debug: Show first few lines to verify content
                var lines = pgnContent.Split('\n').Take(10);
                Console.WriteLine("First 10 lines of PGN:");
                foreach(var line in lines)
                {
                    Console.WriteLine($"  {line.Trim()}");
                }
                
                // Parse PGN headers for game info
                var gameDetails = ExtractGameInfo(pgnContent);
                var fileName = System.IO.Path.GetFileName(filePath);
                game.GameInfo = $"[{fileName}] {gameDetails}";
                
                // Check if there's a FEN starting position in the PGN
                // Look for FEN tag with various possible formats
                var fenPattern = @"\[FEN\s+""([^""]+)""\]";
                var fenMatch = System.Text.RegularExpressions.Regex.Match(pgnContent, fenPattern, System.Text.RegularExpressions.RegexOptions.IgnoreCase);
                
                if (fenMatch.Success && fenMatch.Groups.Count > 1)
                {
                    // Use the FEN from the PGN file
                    var startingFEN = fenMatch.Groups[1].Value.Trim();
                    game.InitialPosition = new ProperChessBoard(startingFEN);
                    Console.WriteLine($"Found FEN in PGN: {startingFEN}");
                }
                else
                {
                    // No FEN tag found - this must be a complete game from the starting position
                    var standardFEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
                    game.InitialPosition = new ProperChessBoard(standardFEN);
                    Console.WriteLine($"No FEN tag found, using standard starting position");
                    
                    // Note: If this PGN file should start from a specific position,
                    // it needs to include a [FEN "..."] tag in the headers
                }
                
                // Parse all moves from the PGN
                game.GameMoves = ParsePGNMoves(pgnContent);
                
                // Log what we loaded
                Console.WriteLine($"PGN loaded from: {filePath}");
                Console.WriteLine($"Game info: {game.GameInfo}");
                Console.WriteLine($"Moves parsed: {game.GameMoves.Count}");
                Console.WriteLine($"Initial position FEN: {game.InitialPosition.FEN}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading PGN: {ex.Message}");
                // Fallback to starting position
                game.InitialPosition = new ProperChessBoard();
                game.GameMoves.Clear();
            }
            
            return game;
        }

        public static ChessGameModel LoadFromFEN(string fenString)
        {
            var game = new ChessGameModel
            {
                InitialPosition = new ProperChessBoard(fenString),
                GameInfo = $"FEN Position: {fenString.Substring(0, Math.Min(30, fenString.Length))}..."
            };
            
            return game;
        }

        private static string ExtractGameInfo(string pgnContent)
        {
            // Extract basic game information from PGN headers
            var lines = pgnContent.Split('\n');
            string white = "", black = "", result = "", date = "";

            foreach (var line in lines)
            {
                if (line.StartsWith("[White "))
                    white = ExtractHeaderValue(line);
                else if (line.StartsWith("[Black "))
                    black = ExtractHeaderValue(line);
                else if (line.StartsWith("[Result "))
                    result = ExtractHeaderValue(line);
                else if (line.StartsWith("[Date "))
                    date = ExtractHeaderValue(line);
            }

            return $"{white} vs {black} ({date}) {result}".Trim();
        }

        private static string ExtractHeaderValue(string headerLine)
        {
            var start = headerLine.IndexOf('"');
            var end = headerLine.LastIndexOf('"');
            if (start >= 0 && end > start)
                return headerLine.Substring(start + 1, end - start - 1);
            return "";
        }

        public ProperChessBoard GetCurrentPosition()
        {
            Console.WriteLine($"=== CALCULATING POSITION FROM PGN ===");
            Console.WriteLine($"Number of moves to apply: {GameMoves.Count}");
            Console.WriteLine($"Initial FEN from PGN tags: {InitialPosition.FEN}");
            
            // Log the moves we're about to apply
            if (GameMoves.Count > 0)
            {
                Console.WriteLine("Moves to apply:");
                for (int i = 0; i < GameMoves.Count; i++)
                {
                    Console.WriteLine($"  {i + 1}. {GameMoves[i].SAN}");
                }
            }
            
            try
            {
                // Create a ChessDotNet game to apply moves
                ChessGame game;
                
                // Check if we have a custom starting position
                if (InitialPosition.FEN != "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
                {
                    // If there's a FEN tag and no moves, use it directly
                    if (GameMoves.Count == 0)
                    {
                        Console.WriteLine("Using FEN position from PGN file (no moves to apply)");
                        return new ProperChessBoard(InitialPosition.FEN);
                    }
                    
                    // Create game from FEN position
                    game = new ChessGame(InitialPosition.FEN);
                }
                else
                {
                    // Standard starting position
                    game = new ChessGame();
                }
                
                Console.WriteLine($"Position before applying moves: {game.GetFen()}");
                
                // Apply all moves from the PGN
                int moveNumber = 0;
                int successfulMoves = 0;
                var positionHistory = new List<string>();
                
                foreach (var move in GameMoves)
                {
                    moveNumber++;
                    string fenBefore = game.GetFen();
                    Console.WriteLine($"\n--- Processing move {moveNumber}: {move.SAN} ---");
                    Console.WriteLine($"Position before: {fenBefore}");
                    
                    try
                    {
                        // Convert SAN to coordinate move
                        var coordMove = ConvertSANToMove(move.SAN, game);
                        
                        if (coordMove != null)
                        {
                            var result = game.ApplyMove(coordMove, true);
                            if (result != ChessDotNet.MoveType.Invalid)
                            {
                                successfulMoves++;
                                string newFen = game.GetFen();
                                
                                // Format move number
                                string moveLabel = (moveNumber % 2 == 1) ? 
                                    $"{(moveNumber + 1) / 2}. {move.SAN}" : 
                                    $"{moveNumber / 2}... {move.SAN}";
                                
                                positionHistory.Add($"{moveLabel}\n   FEN: {newFen}");
                                Console.WriteLine($"SUCCESS: Applied {move.SAN} as {coordMove.OriginalPosition}->{coordMove.NewPosition}");
                                Console.WriteLine($"New position: {newFen}");
                            }
                            else
                            {
                                Console.WriteLine($"FAILED: Move {move.SAN} was invalid");
                                Console.WriteLine($"Attempted: {coordMove.OriginalPosition}->{coordMove.NewPosition}");
                                positionHistory.Add($"ERROR at move {moveNumber}: {move.SAN} - Invalid move");
                                break;
                            }
                        }
                        else
                        {
                            Console.WriteLine($"FAILED: Could not parse move {move.SAN}");
                            Console.WriteLine($"Position stuck at: {game.GetFen()}");
                            positionHistory.Add($"ERROR at move {moveNumber}: {move.SAN} - Could not parse");
                            break;
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"EXCEPTION on move {moveNumber} ({move.SAN}): {ex.Message}");
                        positionHistory.Add($"ERROR at move {moveNumber}: {move.SAN} - {ex.Message}");
                        break;
                    }
                }
                
                // Store position history for UI display
                PositionHistory = positionHistory;
                
                Console.WriteLine($"\n=== POSITION HISTORY ===");
                foreach (var pos in positionHistory)
                {
                    Console.WriteLine(pos);
                }
                Console.WriteLine($"\nMove application summary: {successfulMoves}/{GameMoves.Count} moves applied successfully");
                
                // Get the final FEN position after all moves
                string finalFen = game.GetFen();
                Console.WriteLine($"=== POSITION CALCULATION COMPLETE ===");
                Console.WriteLine($"Final position after applying {GameMoves.Count} moves:");
                Console.WriteLine($"FEN: {finalFen}");
                
                return new ProperChessBoard(finalFen);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error calculating position: {ex.Message}");
                Console.WriteLine("Falling back to initial position");
                return new ProperChessBoard(InitialPosition.FEN);
            }
        }

        public void SaveAnalysisAsPGN(string filePath)
        {
            if (AnalysisTree == null)
                throw new InvalidOperationException("No analysis to save");

            var pgn = GeneratePGNFromAnalysis();
            System.IO.File.WriteAllText(filePath, pgn);
        }

        public void SaveAnalysisAsJSON(string filePath)
        {
            if (AnalysisTree == null)
                throw new InvalidOperationException("No analysis to save");

            var json = JsonConvert.SerializeObject(AnalysisTree, Formatting.Indented);
            System.IO.File.WriteAllText(filePath, json);
        }

        private string GeneratePGNFromAnalysis()
        {
            var pgn = $"[Event \"Chess Tree Analysis\"]\n";
            pgn += $"[Date \"{DateTime.Now:yyyy.MM.dd}\"]\n";
            pgn += $"[White \"Analysis\"]\n";
            pgn += $"[Black \"Analysis\"]\n";
            pgn += $"[Result \"*\"]\n";
            pgn += $"[FEN \"{InitialPosition.FEN}\"]\n\n";

            if (AnalysisTree != null)
            {
                pgn += GenerateVariationsFromTree(AnalysisTree, 1);
            }

            return pgn;
        }

        private string GenerateVariationsFromTree(AnalysisTreeNode node, int moveNumber)
        {
            // TODO: Implement PGN generation from analysis tree
            // This is a simplified version
            return "Analysis tree conversion to PGN format";
        }

        private Move ConvertSANToMove(string san, ChessGame game)
        {
            // Get all valid moves and find the one that matches the SAN
            var validMoves = game.GetValidMoves(game.WhoseTurn);
            string sanClean = san.Replace("+", "").Replace("#", "").Replace("!", "").Replace("?", "");
            
            // Log for debugging
            System.Diagnostics.Debug.WriteLine($"Converting SAN '{san}' for {game.WhoseTurn}");
            System.Diagnostics.Debug.WriteLine($"Found {validMoves.Count()} valid moves");
            
            // Handle castling
            if (san == "O-O" || san == "0-0")
            {
                foreach (var move in validMoves)
                {
                    if ((game.WhoseTurn == Player.White && move.OriginalPosition.ToString() == "E1" && move.NewPosition.ToString() == "G1") ||
                        (game.WhoseTurn == Player.Black && move.OriginalPosition.ToString() == "E8" && move.NewPosition.ToString() == "G8"))
                    {
                        return move;
                    }
                }
            }
            else if (san == "O-O-O" || san == "0-0-0")
            {
                foreach (var move in validMoves)
                {
                    if ((game.WhoseTurn == Player.White && move.OriginalPosition.ToString() == "E1" && move.NewPosition.ToString() == "C1") ||
                        (game.WhoseTurn == Player.Black && move.OriginalPosition.ToString() == "E8" && move.NewPosition.ToString() == "C8"))
                    {
                        return move;
                    }
                }
            }
            
            // Clean up the SAN for easier parsing
            bool isCapture = sanClean.Contains("x");
            sanClean = sanClean.Replace("x", "");
            
            // Try to match each valid move
            foreach (var move in validMoves)
            {
                string from = move.OriginalPosition.ToString().ToUpper();
                string to = move.NewPosition.ToString().ToUpper();
                
                // For debugging
                System.Diagnostics.Debug.WriteLine($"  Testing move {from}->{to}");
                
                // Check if destination matches
                if (!sanClean.ToUpper().Contains(to))
                    continue;
                
                // For pawn moves (starts with lowercase letter or is 2 chars like "e4")
                if (char.IsLower(san[0]))
                {
                    var piece = game.GetPieceAt(move.OriginalPosition);
                    if (piece == null) continue;
                    
                    // Check if it's a pawn
                    if (piece.GetType().Name.Contains("Pawn"))
                    {
                        // For pawn captures, check the file
                        if (isCapture)
                        {
                            char fromFile = char.ToUpper(san[0]);
                            if (from[0] == fromFile && to == sanClean.ToUpper().Substring(sanClean.Length - 2))
                            {
                                System.Diagnostics.Debug.WriteLine($"  Matched pawn capture: {san} -> {from}->{to}");
                                return move;
                            }
                        }
                        // For regular pawn moves
                        else if (sanClean.ToUpper() == to)
                        {
                            System.Diagnostics.Debug.WriteLine($"  Matched pawn move: {san} -> {from}->{to}");
                            return move;
                        }
                    }
                }
                // For piece moves (starts with uppercase letter)
                else
                {
                    var piece = game.GetPieceAt(move.OriginalPosition);
                    if (piece == null) continue;
                    
                    char expectedPiece = san[0];
                    char actualPiece = GetPieceLetter(piece);
                    
                    if (expectedPiece == actualPiece)
                    {
                        // Check for disambiguation (like Nbd2 vs Nfd2)
                        if (sanClean.Length > 3)
                        {
                            // There's disambiguation
                            char disambig = sanClean[1];
                            if (char.IsLower(disambig))
                            {
                                // File disambiguation
                                if (from[0] != char.ToUpper(disambig))
                                    continue;
                            }
                            else if (char.IsDigit(disambig))
                            {
                                // Rank disambiguation
                                if (from[1] != disambig)
                                    continue;
                            }
                        }
                        
                        System.Diagnostics.Debug.WriteLine($"  Matched piece move: {san} -> {from}->{to}");
                        return move;
                    }
                }
            }
            
            System.Diagnostics.Debug.WriteLine($"WARNING: Could not find valid move for SAN: {san}");
            return null;
        }
        
        private bool DoesMoveMathSAN(string san, Move move, ChessGame game)
        {
            // Clean the SAN notation
            string sanClean = san.Replace("+", "").Replace("#", "").Replace("x", "").Replace("=", "").ToLower();
            string dest = move.NewPosition.ToString().ToLower();
            
            // Castling
            if (san == "O-O" || san == "0-0")
                return dest == "g1" || dest == "g8";
            if (san == "O-O-O" || san == "0-0-0")
                return dest == "c1" || dest == "c8";
            
            // Check if destination matches
            if (!sanClean.Contains(dest))
                return false;
            
            // For pawn moves (starts with file letter)
            if (sanClean.Length <= 3 && char.IsLetter(sanClean[0]) && char.IsLower(sanClean[0]))
            {
                // It's a pawn move if it starts with a lowercase letter
                return true;
            }
            
            // For piece moves, verify piece type
            var piece = game.GetPieceAt(move.OriginalPosition);
            if (piece != null)
            {
                char expectedPiece = char.ToLower(sanClean[0]);
                char actualPiece = char.ToLower(GetPieceLetter(piece));
                
                // Special case: pawn moves don't have piece letter
                if (actualPiece == 'p' && char.IsLower(sanClean[0]))
                    return true;
                    
                return expectedPiece == actualPiece;
            }
            
            return false;
        }
        
        private char GetPieceLetter(Piece piece)
        {
            // Get the piece type name and return the first letter
            string typeName = piece.GetType().Name;
            switch (typeName)
            {
                case "King": return 'K';
                case "Queen": return 'Q';
                case "Rook": return 'R';
                case "Bishop": return 'B';
                case "Knight": return 'N';
                case "Pawn": return 'P';
                default: return '?';
            }
        }
        
        private bool IsMoveMatch(string san, Move move, ChessGame game)
        {
            // More robust matching logic
            string sanClean = san.Replace("+", "").Replace("#", "").Replace("x", "").Replace("=", "");
            string dest = move.NewPosition.ToString().ToLower();
            
            // Check for castling
            if ((san == "O-O" || san == "0-0") && move.NewPosition.File == ChessDotNet.File.G)
                return true;
            if ((san == "O-O-O" || san == "0-0-0") && move.NewPosition.File == ChessDotNet.File.C)
                return true;
            
            // For pawn moves - they start with lowercase letters
            if (char.IsLower(sanClean[0]) || sanClean.Length == 2)
            {
                // Pawn moves are simple: e4, exd5, etc.
                return sanClean.ToLower().Contains(dest);
            }
            
            // For piece moves - check if the destination matches
            return sanClean.ToLower().Contains(dest);
        }
        
        private static List<SimpleMove> ParsePGNMoves(string pgnContent)
        {
            var moves = new List<SimpleMove>();
            
            try
            {
                // Extract move text from PGN (everything after headers)
                var lines = pgnContent.Split('\n');
                var moveText = "";
                bool inMoves = false;
                
                foreach (var line in lines)
                {
                    if (!line.StartsWith("[") && !string.IsNullOrWhiteSpace(line))
                    {
                        inMoves = true;
                        moveText += line + " ";
                    }
                }
                
                if (inMoves)
                {
                    // For your PGN: "1. e4 e5 2. Nc3 Nf6 3. f4 d5 4. fxe5 Nxe4 5. d3 Nxc3 6. bxc3 d4 7. Nf3 dxc3 *"
                    Console.WriteLine($"Parsing move text: {moveText}");
                    
                    // Clean up the move text and split by spaces
                    var cleanedText = moveText.Replace("*", "").Trim();
                    var tokens = cleanedText.Split(new char[] { ' ', '\t', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries);
                    
                    foreach (var token in tokens)
                    {
                        var cleanToken = token.Trim();
                        
                        // Skip move numbers (1., 2., etc.), result symbols, and empty tokens
                        if (string.IsNullOrEmpty(cleanToken) ||
                            cleanToken.EndsWith(".") ||
                            cleanToken == "*" || 
                            cleanToken == "1-0" || 
                            cleanToken == "0-1" || 
                            cleanToken == "1/2-1/2")
                        {
                            continue;
                        }
                        
                        // This should be a move in Standard Algebraic Notation
                        Console.WriteLine($"Adding move: {cleanToken}");
                        moves.Add(new SimpleMove(cleanToken, cleanToken, 0));
                    }
                }
                
                Console.WriteLine($"Parsed {moves.Count} moves from PGN");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error parsing PGN moves: {ex.Message}");
            }
            
            return moves;
        }
    }
}