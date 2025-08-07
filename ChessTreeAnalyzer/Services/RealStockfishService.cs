using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using ChessTreeAnalyzer.Models;

namespace ChessTreeAnalyzer.Services
{
    /// <summary>
    /// REAL Stockfish Service - Replicated from Python working version
    /// Uses actual UCI protocol communication like the Python chess.engine library
    /// </summary>
    public class RealStockfishService : IDisposable
    {
        private readonly string _stockfishPath;
        private Process? _stockfishProcess;
        private StreamWriter? _stockfishInput;
        private StreamReader? _stockfishOutput;
        private bool _isInitialized = false;

        public RealStockfishService(string stockfishPath)
        {
            _stockfishPath = stockfishPath ?? throw new ArgumentNullException(nameof(stockfishPath));
        }

        public async Task<bool> InitializeAsync()
        {
            try
            {
                if (!File.Exists(_stockfishPath))
                {
                    throw new FileNotFoundException($"Stockfish executable not found: {_stockfishPath}");
                }

                // Start Stockfish process exactly like Python version
                _stockfishProcess = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = _stockfishPath,
                        UseShellExecute = false,
                        RedirectStandardInput = true,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    }
                };

                _stockfishProcess.Start();
                _stockfishInput = _stockfishProcess.StandardInput;
                _stockfishOutput = _stockfishProcess.StandardOutput;

                // Initialize UCI like Python's chess.engine.SimpleEngine.popen_uci()
                await SendCommandAsync("uci");
                
                // Wait for uciok response
                string? line;
                bool uciOk = false;
                while ((line = await _stockfishOutput.ReadLineAsync()) != null)
                {
                    if (line.Trim() == "uciok")
                    {
                        uciOk = true;
                        break;
                    }
                }

                if (!uciOk)
                {
                    throw new InvalidOperationException("Failed to initialize UCI protocol");
                }

                // Configure engine like Python version
                await ConfigureEngineAsync();
                
                _isInitialized = true;
                return true;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to initialize Stockfish: {ex.Message}", ex);
            }
        }

        private async Task ConfigureEngineAsync()
        {
            try
            {
                // Configure threads (auto-detect like Python)
                var threads = Environment.ProcessorCount;
                await SendCommandAsync($"setoption name Threads value {threads}");

                // Configure hash size (like Python version - use 1GB)
                await SendCommandAsync("setoption name Hash value 1024");

                // Disable pondering for consistent timing (like Python)
                await SendCommandAsync("setoption name Ponder value false");

                // Send isready to confirm settings
                await SendCommandAsync("isready");
                
                string? line;
                while ((line = await _stockfishOutput.ReadLineAsync()) != null)
                {
                    if (line.Trim() == "readyok")
                        break;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Could not configure all engine options: {ex.Message}");
            }
        }

        /// <summary>
        /// Analyze position exactly like Python's analyzer.analyze_position()
        /// </summary>
        public async Task<List<AnalyzedMove>> AnalyzePositionAsync(SimpleChessBoard position, 
            int numMoves, double timeSeconds, CancellationToken cancellationToken)
        {
            if (!_isInitialized || position.IsGameOver)
                return new List<AnalyzedMove>();

            try
            {
                // Set position using FEN (like Python: engine.analyse(board, ...))
                await SendCommandAsync($"position fen {position.ToFen()}");
                
                // Configure MultiPV (like Python's multipv parameter)
                await SendCommandAsync($"setoption name MultiPV value {numMoves}");
                
                // Start analysis with time limit (like Python's Limit(time=...))
                var timeMs = (int)(timeSeconds * 1000);
                await SendCommandAsync($"go movetime {timeMs}");
                
                // Parse results exactly like Python's _extract_evaluation()
                var results = new Dictionary<int, AnalyzedMove>();
                bool bestmoveReceived = false;
                
                while (!bestmoveReceived && !cancellationToken.IsCancellationRequested)
                {
                    var line = await _stockfishOutput.ReadLineAsync();
                    if (line == null) break;
                    
                    if (line.StartsWith("info") && line.Contains("pv"))
                    {
                        var move = ParseEngineOutput(line, position);
                        if (move != null)
                        {
                            results[move.MultiPvIndex] = move;
                        }
                    }
                    else if (line.StartsWith("bestmove"))
                    {
                        bestmoveReceived = true;
                    }
                }
                
                // Return sorted by best moves first (like Python)
                return results.Values.OrderBy(m => m.MultiPvIndex).Take(numMoves).ToList();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Analysis failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Parse Stockfish output exactly like Python's _extract_evaluation()
        /// </summary>
        private AnalyzedMove? ParseEngineOutput(string line, SimpleChessBoard position)
        {
            try
            {
                // Parse: info depth 18 seldepth 24 multipv 1 score cp 458 nodes 1543829 nps 1932341 tbhits 0 time 799 pv d3d4
                var parts = line.Split(' ');
                
                int multiPvIndex = 1;
                int evaluation = 0;
                bool isMate = false;
                int mateInMoves = 0;
                string? uciMove = null;
                
                for (int i = 0; i < parts.Length - 1; i++)
                {
                    switch (parts[i])
                    {
                        case "multipv":
                            if (int.TryParse(parts[i + 1], out var pv))
                                multiPvIndex = pv;
                            break;
                            
                        case "score":
                            if (i + 2 < parts.Length)
                            {
                                if (parts[i + 1] == "cp" && int.TryParse(parts[i + 2], out var cp))
                                {
                                    // Centipawn score (like Python's score_obj.cp)
                                    evaluation = cp;
                                }
                                else if (parts[i + 1] == "mate" && int.TryParse(parts[i + 2], out var mate))
                                {
                                    // Mate score (like Python's score_obj.mate())
                                    isMate = true;
                                    mateInMoves = mate;
                                }
                            }
                            break;
                            
                        case "pv":
                            if (i + 1 < parts.Length)
                            {
                                uciMove = parts[i + 1];
                            }
                            break;
                    }
                }
                
                if (string.IsNullOrEmpty(uciMove))
                    return null;

                // Convert UCI to SAN (like Python's board.san(move))
                var sanMove = ConvertUciToSan(uciMove, position);
                
                return new AnalyzedMove
                {
                    Move = new SimpleMove { UCI = uciMove, SAN = sanMove },
                    MoveNotation = sanMove,
                    Evaluation = evaluation,
                    IsMate = isMate,
                    MateInMoves = mateInMoves,
                    MultiPvIndex = multiPvIndex,
                    Depth = 0
                };
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Convert UCI to SAN notation (like Python's board.san(move))
        /// </summary>
        private string ConvertUciToSan(string uciMove, SimpleChessBoard position)
        {
            try
            {
                if (uciMove.Length < 4) return uciMove;
                
                var from = uciMove.Substring(0, 2);
                var to = uciMove.Substring(2, 2);
                
                // Get piece at source square
                var piece = position.GetPieceAt(GetSquareIndex(from));
                
                if (string.IsNullOrEmpty(piece))
                {
                    // Pawn move
                    if (from[0] != to[0]) // Capture
                        return $"{from[0]}x{to}";
                    else
                        return to;
                }
                else
                {
                    var pieceSymbol = piece.ToUpper();
                    if (pieceSymbol == "P") pieceSymbol = ""; // Pawns don't show symbol
                    
                    // Check for capture
                    var targetPiece = position.GetPieceAt(GetSquareIndex(to));
                    var capture = !string.IsNullOrEmpty(targetPiece) ? "x" : "";
                    
                    return $"{pieceSymbol}{capture}{to}";
                }
            }
            catch
            {
                return uciMove; // Fallback
            }
        }
        
        private int GetSquareIndex(string square)
        {
            if (square.Length != 2) return -1;
            var file = square[0] - 'a';
            var rank = square[1] - '1';
            return rank * 8 + file;
        }

        private async Task SendCommandAsync(string command)
        {
            if (_stockfishInput != null)
            {
                await _stockfishInput.WriteLineAsync(command);
                await _stockfishInput.FlushAsync();
            }
        }

        public void Dispose()
        {
            try
            {
                if (_stockfishInput != null)
                {
                    _stockfishInput.WriteLine("quit");
                    _stockfishInput.Flush();
                    _stockfishInput.Close();
                }

                _stockfishOutput?.Close();
                
                if (_stockfishProcess != null && !_stockfishProcess.HasExited)
                {
                    _stockfishProcess.WaitForExit(1000);
                    if (!_stockfishProcess.HasExited)
                        _stockfishProcess.Kill();
                }

                _stockfishProcess?.Dispose();
                _isInitialized = false;
            }
            catch (Exception)
            {
                // Ignore disposal errors
            }
        }
    }
}