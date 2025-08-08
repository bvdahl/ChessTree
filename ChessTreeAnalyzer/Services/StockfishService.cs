using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using ChessTreeAnalyzer.Models;

namespace ChessTreeAnalyzer.Services
{
    public class StockfishService : IDisposable
    {
        private Process _stockfishProcess;
        private StreamWriter _stockfishInput;
        private StreamReader _stockfishOutput;
        private bool _isInitialized = false;
        private readonly object _lock = new object();

        public bool IsInitialized => _isInitialized;

        public async Task<bool> InitializeAsync(string stockfishPath, AnalysisSettings settings)
        {
            try
            {
                if (_isInitialized)
                    Dispose();

                if (!File.Exists(stockfishPath))
                    throw new FileNotFoundException($"Stockfish executable not found: {stockfishPath}");

                _stockfishProcess = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = stockfishPath,
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

                // Wait for UCI ready
                await SendCommandAsync("uci");
                await WaitForResponseAsync("uciok");

                // Configure engine settings
                await SendCommandAsync($"setoption name Hash value {settings.HashSizeMB}");
                await SendCommandAsync($"setoption name Threads value {settings.ThreadCount}");
                await SendCommandAsync("isready");
                await WaitForResponseAsync("readyok");

                _isInitialized = true;
                return true;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to initialize Stockfish: {ex.Message}", ex);
            }
        }

        public async Task<List<AnalyzedMove>> AnalyzePositionAsync(ProperChessBoard position, 
            int movesToAnalyze, TimeSpan analysisTime, CancellationToken cancellationToken = default)
        {
            if (!_isInitialized)
                throw new InvalidOperationException("Stockfish not initialized");

            lock (_lock)
            {
                try
                {
                    var results = new List<AnalyzedMove>();

                    // Set position with proper UCI protocol
                    var fen = position.FEN;
                    System.Diagnostics.Debug.WriteLine($"[STOCKFISH] Setting position: {fen}");
                    SendCommand($"position fen {fen}");
                    SendCommand("isready");
                    WaitForResponse("readyok", 1000);
                    
                    // Configure multipv for analyzing multiple moves
                    SendCommand($"setoption name MultiPV value {movesToAnalyze}");
                    
                    // Start analysis with proper time control
                    var timeMs = (int)analysisTime.TotalMilliseconds;
                    System.Diagnostics.Debug.WriteLine($"[STOCKFISH] Starting analysis for {timeMs}ms with MultiPV={movesToAnalyze}");
                    SendCommand($"go movetime {timeMs}");

                    // Read analysis output until bestmove
                    string line;
                    var multiPvResults = new Dictionary<int, AnalyzedMove>();
                    var timeout = DateTime.Now.AddMilliseconds(timeMs + 2000); // Add buffer for engine overhead

                    while ((line = _stockfishOutput.ReadLine()) != null && DateTime.Now < timeout)
                    {
                        cancellationToken.ThrowIfCancellationRequested();
                        
                        System.Diagnostics.Debug.WriteLine($"[STOCKFISH OUTPUT] {line}");

                        if (line.StartsWith("bestmove"))
                        {
                            System.Diagnostics.Debug.WriteLine($"[STOCKFISH] Analysis complete, found {multiPvResults.Count} moves");
                            break;
                        }

                        if (line.StartsWith("info") && line.Contains("multipv"))
                        {
                            var analyzedMove = ParseInfoLine(line, position);
                            if (analyzedMove != null)
                            {
                                multiPvResults[analyzedMove.MultiPvIndex] = analyzedMove;
                                System.Diagnostics.Debug.WriteLine($"[STOCKFISH] Parsed move {analyzedMove.MultiPvIndex}: {analyzedMove.Move?.UCI} eval={analyzedMove.Evaluation}");
                            }
                        }
                    }

                    // Convert to sorted list
                    for (int i = 1; i <= Math.Min(movesToAnalyze, multiPvResults.Count); i++)
                    {
                        if (multiPvResults.ContainsKey(i))
                        {
                            results.Add(multiPvResults[i]);
                        }
                    }

                    return results;
                }
                catch (Exception ex)
                {
                    throw new InvalidOperationException($"Analysis failed: {ex.Message}", ex);
                }
            }
        }

        private AnalyzedMove ParseInfoLine(string infoLine, ProperChessBoard position)
        {
            try
            {
                var parts = infoLine.Split(' ');
                var analyzedMove = new AnalyzedMove();

                for (int i = 0; i < parts.Length; i++)
                {
                    switch (parts[i])
                    {
                        case "multipv":
                            if (i + 1 < parts.Length && int.TryParse(parts[i + 1], out int pvIndex))
                                analyzedMove.MultiPvIndex = pvIndex;
                            break;

                        case "cp":
                            if (i + 1 < parts.Length && int.TryParse(parts[i + 1], out int cp))
                            {
                                // Stockfish gives evaluation from perspective of side to move
                                // Keep it as-is for now
                                analyzedMove.Evaluation = cp;
                                analyzedMove.IsMate = false;
                            }
                            break;

                        case "mate":
                            if (i + 1 < parts.Length && int.TryParse(parts[i + 1], out int mateIn))
                            {
                                analyzedMove.MateInMoves = mateIn;
                                analyzedMove.IsMate = true;
                            }
                            break;

                        case "pv":
                            if (i + 1 < parts.Length)
                            {
                                var uciMove = parts[i + 1];
                                // Convert UCI to SAN notation
                                var sanMove = ConvertUciToSan(uciMove, position);
                                analyzedMove.Move = new SimpleMove(uciMove, sanMove, 0); // Fixed: UCI first, then SAN
                                analyzedMove.MoveNotation = sanMove; // Use SAN for display
                            }
                            break;

                        case "depth":
                            if (i + 1 < parts.Length && int.TryParse(parts[i + 1], out int depth))
                                analyzedMove.Depth = depth;
                            break;
                    }
                }

                return analyzedMove.Move != null ? analyzedMove : null;
            }
            catch
            {
                return null;
            }
        }

        private async Task SendCommandAsync(string command)
        {
            await _stockfishInput.WriteLineAsync(command);
            await _stockfishInput.FlushAsync();
        }

        private void SendCommand(string command)
        {
            _stockfishInput.WriteLine(command);
            _stockfishInput.Flush();
        }

        private async Task<bool> WaitForResponseAsync(string expectedResponse, int timeoutMs = 5000)
        {
            var timeout = DateTime.Now.AddMilliseconds(timeoutMs);
            
            while (DateTime.Now < timeout)
            {
                var line = await _stockfishOutput.ReadLineAsync();
                if (line != null && line.Trim() == expectedResponse)
                    return true;
            }
            
            return false;
        }
        
        private bool WaitForResponse(string expectedResponse, int timeoutMs = 5000)
        {
            var timeout = DateTime.Now.AddMilliseconds(timeoutMs);
            
            while (DateTime.Now < timeout)
            {
                var line = _stockfishOutput.ReadLine();
                if (line != null && line.Trim() == expectedResponse)
                    return true;
            }
            
            return false;
        }

        private string ConvertUciToSan(string uciMove, ProperChessBoard position)
        {
            try
            {
                // Simple UCI to SAN conversion for common cases
                if (uciMove.Length < 4) return uciMove;
                
                var from = uciMove.Substring(0, 2);
                var to = uciMove.Substring(2, 2);
                var piece = position.GetPieceAt(GetSquareIndex(from));
                
                // Basic conversion - this would need full chess logic for accurate SAN
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
                // Fallback to UCI if conversion fails
                return uciMove;
            }
        }
        
        private int GetSquareIndex(string square)
        {
            if (square.Length != 2) return -1;
            var file = square[0] - 'a';
            var rank = square[1] - '1';
            return rank * 8 + file;
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

    public class AnalyzedMove
    {
        public SimpleMove Move { get; set; }
        public string MoveNotation { get; set; } = "";
        public int Evaluation { get; set; }
        public bool IsMate { get; set; }
        public int MateInMoves { get; set; }
        public int Depth { get; set; }
        public int MultiPvIndex { get; set; }

        public string EvaluationText
        {
            get
            {
                if (IsMate)
                    return $"Mate in {Math.Abs(MateInMoves)}";
                else
                    return $"{Evaluation:+0;-#}";
            }
        }
    }
}