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
            Console.WriteLine($"GetCurrentPosition: Starting with {GameMoves.Count} moves to apply");
            Console.WriteLine($"Initial position FEN: {InitialPosition.FEN}");
            
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
                
                // Apply all moves from the PGN
                foreach (var move in GameMoves)
                {
                    try
                    {
                        // Parse the SAN move to find source and destination squares
                        bool moveApplied = false;
                        
                        // Get all valid moves for the current player
                        var validMoves = game.GetValidMoves(game.WhoseTurn);
                        
                        foreach (var validMove in validMoves)
                        {
                            // Check if this move matches our SAN notation
                            // The SAN property is populated after making the move, so we need to test it
                            var testGame = new ChessGame(game.GetFen());
                            var moveType = testGame.ApplyMove(validMove, true);
                            if (!ChessDotNet.MoveType.Invalid.HasFlag(moveType))
                            {
                                // Compare the move coordinates with our SAN
                                // This is a simplified check - we'll improve it if needed
                                if (IsMoveMatch(move.SAN, validMove, game))
                                {
                                    // This is the correct move! Apply it to our actual game
                                    game.ApplyMove(validMove, true);
                                    Console.WriteLine($"Applied move: {move.SAN}");
                                    moveApplied = true;
                                    break;
                                }
                            }
                        }
                        
                        if (!moveApplied)
                        {
                            Console.WriteLine($"Warning: Could not apply move {move.SAN}");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error applying move {move.SAN}: {ex.Message}");
                    }
                }
                
                // Get the final FEN position after all moves
                string finalFen = game.GetFen();
                Console.WriteLine($"Final position after {GameMoves.Count} moves: {finalFen}");
                
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