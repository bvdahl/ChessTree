using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;

namespace ChessTreeAnalyzer.Models
{
    public class ChessGameModel
    {
        public string GameInfo { get; set; } = "";
        public SimpleChessBoard InitialPosition { get; set; }
        public List<SimpleMove> GameMoves { get; set; } = new List<SimpleMove>();
        public AnalysisTreeNode AnalysisTree { get; set; }
        public string SourceFile { get; set; } = "";
        public DateTime CreatedDate { get; set; } = DateTime.Now;

        public ChessGameModel()
        {
            InitialPosition = new SimpleChessBoard();
        }



        public static ChessGameModel LoadFromPGN(string filePath)
        {
            var game = new ChessGameModel
            {
                SourceFile = filePath
            };

            // Read PGN file
            var pgnContent = File.ReadAllText(filePath);
            
            // Parse PGN headers for game info
            game.GameInfo = ExtractGameInfo(pgnContent);
            
            // Parse moves and determine current position
            var board = new SimpleChessBoard();
            game.InitialPosition = new SimpleChessBoard(board.FEN);
            
            // Parse PGN moves (simplified - in real app would use proper PGN parser)
            game.GameMoves = ParsePGNMoves(pgnContent);
            
            // If there's a FEN tag, use that as initial position
            var fenMatch = System.Text.RegularExpressions.Regex.Match(pgnContent, @"\[FEN ""([^""]+)""\]");
            if (fenMatch.Success)
            {
                game.InitialPosition = new SimpleChessBoard(fenMatch.Groups[1].Value);
            }
            
            return game;
        }

        public static ChessGameModel LoadFromFEN(string fenString)
        {
            var game = new ChessGameModel
            {
                InitialPosition = new SimpleChessBoard(fenString),
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

        public SimpleChessBoard GetCurrentPosition()
        {
            var board = new SimpleChessBoard(InitialPosition.FEN);
            
            // Apply all game moves
            foreach (var move in GameMoves)
            {
                board = board.MakeMove(move.SAN);
            }
            
            return board;
        }

        public void SaveAnalysisAsPGN(string filePath)
        {
            if (AnalysisTree == null)
                throw new InvalidOperationException("No analysis to save");

            var pgn = GeneratePGNFromAnalysis();
            File.WriteAllText(filePath, pgn);
        }

        public void SaveAnalysisAsJSON(string filePath)
        {
            if (AnalysisTree == null)
                throw new InvalidOperationException("No analysis to save");

            var json = JsonConvert.SerializeObject(AnalysisTree, Formatting.Indented);
            File.WriteAllText(filePath, json);
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

        private static List<SimpleMove> ParsePGNMoves(string pgnContent)
        {
            var moves = new List<SimpleMove>();
            
            // Extract move text (everything after headers)
            var lines = pgnContent.Split('\n');
            bool inMoveText = false;
            var moveText = "";
            
            foreach (var line in lines)
            {
                if (string.IsNullOrWhiteSpace(line) && !inMoveText)
                {
                    inMoveText = true;
                    continue;
                }
                
                if (inMoveText && !line.StartsWith("["))
                {
                    moveText += line + " ";
                }
            }
            
            // Simple move parsing - extract SAN notation
            // This is simplified - real implementation would use proper PGN parser
            var moveMatches = System.Text.RegularExpressions.Regex.Matches(moveText, 
                @"\d+\.(?:\.\.)?\s*([NBRQK]?[a-h]?[1-8]?x?[a-h][1-8](?:=[NBRQ])?[+#]?)");
            
            foreach (System.Text.RegularExpressions.Match match in moveMatches)
            {
                if (match.Groups[1].Success)
                {
                    var san = match.Groups[1].Value.Trim();
                    moves.Add(new SimpleMove(san, san));
                }
            }
            
            return moves;
        }
    }
}