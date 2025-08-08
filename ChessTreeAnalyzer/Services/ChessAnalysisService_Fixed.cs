using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ChessTreeAnalyzer.Models;

namespace ChessTreeAnalyzer.Services
{
    public class ChessAnalysisService_Fixed
    {
        private readonly StockfishService _stockfishService;
        private bool _isAnalyzing = false;
        private CancellationTokenSource _cancellationTokenSource;
        private List<string> _allDiagnostics = new List<string>();

        public event EventHandler<AnalysisProgressEventArgs> AnalysisProgressChanged;
        public event EventHandler<AnalysisCompletedEventArgs> AnalysisCompleted;
        public event EventHandler<string> AnalysisOutputReceived;

        public bool IsAnalyzing => _isAnalyzing;

        public ChessAnalysisService_Fixed(StockfishService stockfishService)
        {
            _stockfishService = stockfishService ?? throw new ArgumentNullException(nameof(stockfishService));
        }

        public async Task StartAnalysisAsync(ChessGameModel game, AnalysisSettings settings)
        {
            if (_isAnalyzing)
                throw new InvalidOperationException("Analysis already in progress");

            _isAnalyzing = true;
            _cancellationTokenSource = new CancellationTokenSource();
            _allDiagnostics.Clear();

            try
            {
                var result = await PerformCompleteAnalysisAsync(game, settings, _cancellationTokenSource.Token);
                
                OnAnalysisCompleted(new AnalysisCompletedEventArgs
                {
                    Success = true,
                    AnalysisResult = result,
                    PositionsAnalyzed = result.GetTotalNodeCount(),
                    ErrorMessage = null
                });
            }
            catch (OperationCanceledException)
            {
                LogAndOutput("Analysis cancelled by user.");
                OnAnalysisCompleted(new AnalysisCompletedEventArgs
                {
                    Success = false,
                    AnalysisResult = null,
                    PositionsAnalyzed = 0,
                    ErrorMessage = "Analysis cancelled by user"
                });
            }
            catch (Exception ex)
            {
                LogAndOutput($"Analysis error: {ex.Message}");
                OnAnalysisCompleted(new AnalysisCompletedEventArgs
                {
                    Success = false,
                    AnalysisResult = null,
                    PositionsAnalyzed = 0,
                    ErrorMessage = ex.Message
                });
            }
            finally
            {
                _isAnalyzing = false;
                _cancellationTokenSource?.Dispose();
                _cancellationTokenSource = null;
            }
        }

        private async Task<AnalysisTreeNode> PerformCompleteAnalysisAsync(ChessGameModel game, AnalysisSettings settings, CancellationToken cancellationToken)
        {
            var startTime = DateTime.Now;
            
            LogAndOutput("Starting chess analysis...");
            
            // Initialize Stockfish
            if (!_stockfishService.IsInitialized)
            {
                LogAndOutput("Initializing Stockfish engine...");
                await _stockfishService.InitializeAsync(settings.StockfishPath, settings);
                LogAndOutput("Stockfish initialized successfully.");
            }

            // Get the ACTUAL current position from loaded game
            var currentPosition = game.GetCurrentPosition();
            LogAndOutput($"Starting position FEN: {currentPosition.FEN}");
            LogAndOutput($"Analysis depth: {settings.MaxDepth}, time: {settings.TimePerPosition.TotalSeconds}s per position");
            LogAndOutput($"White: {settings.WhiteMovesToAnalyze} moves, threshold {settings.WhiteThreshold}cp");
            LogAndOutput($"Black: {settings.BlackMovesToAnalyze} moves, threshold {settings.BlackThreshold}cp");

            // Create root node from CURRENT position (not initial)
            var root = new AnalysisTreeNode
            {
                Position = currentPosition,
                Depth = 0,
                Move = null,
                Evaluation = 0
            };

            // BFS tree generation
            var queue = new Queue<AnalysisTreeNode>();
            queue.Enqueue(root);
            int positionsAnalyzed = 0;

            while (queue.Count > 0 && !cancellationToken.IsCancellationRequested)
            {
                var currentNode = queue.Dequeue();

                // Stop if reached max depth
                if (currentNode.Depth >= settings.MaxDepth)
                    continue;

                // Skip if game over
                if (currentNode.Position.IsGameOver)
                    continue;

                try
                {
                    positionsAnalyzed++;
                    
                    // Generate proper move sequence with correct move numbers
                    var moveSequence = GenerateProperMoveSequence(currentNode);
                    
                    OnAnalysisProgressChanged(new AnalysisProgressEventArgs
                    {
                        ProgressPercentage = Math.Min(100, (positionsAnalyzed * 10)),
                        PositionsAnalyzed = positionsAnalyzed,
                        TotalPositions = 100,
                        CurrentMove = moveSequence
                    });

                    LogAndOutput($"Analyzing position at depth {currentNode.Depth}: {moveSequence}");
                    LogAndOutput($"  FEN: {currentNode.Position.FEN}");

                    // Determine moves to analyze
                    var movesToAnalyze = currentNode.Position.WhiteToMove ? 
                        settings.WhiteMovesToAnalyze : settings.BlackMovesToAnalyze;

                    // Analyze position
                    var analyzedMoves = await _stockfishService.AnalyzePositionAsync(
                        currentNode.Position, movesToAnalyze, settings.TimePerPosition, cancellationToken);

                    if (analyzedMoves.Count == 0)
                    {
                        LogAndOutput($"No legal moves found at depth {currentNode.Depth}");
                        continue;
                    }

                    // Filter moves based on thresholds
                    var filteredMoves = FilterMoves(analyzedMoves, currentNode.Position.WhiteToMove,
                        settings.WhiteThreshold, settings.BlackThreshold);

                    LogAndOutput($"Found {analyzedMoves.Count} moves, using {filteredMoves.Count} after filtering");
                    
                    // Show top moves with proper notation
                    for (int i = 0; i < Math.Min(3, filteredMoves.Count); i++)
                    {
                        var move = filteredMoves[i];
                        var moveNum = currentNode.Position.MoveNumber;
                        var side = currentNode.Position.WhiteToMove ? $"{moveNum}." : $"{moveNum}...";
                        LogAndOutput($"  {side}{move.MoveNotation} {move.EvaluationText}");
                    }

                    // Create child nodes
                    foreach (var analyzedMove in filteredMoves)
                    {
                        if (analyzedMove.Move == null) continue;

                        var childPosition = currentNode.Position.MakeMove(analyzedMove.Move);

                        var childNode = new AnalysisTreeNode
                        {
                            Position = childPosition,
                            Move = analyzedMove.Move,
                            Evaluation = (int)analyzedMove.Evaluation,
                            IsMateScore = analyzedMove.IsMate,
                            MateInMoves = analyzedMove.MateInMoves,
                            Depth = currentNode.Depth + 1
                        };

                        currentNode.AddChild(childNode);
                        queue.Enqueue(childNode);
                    }
                }
                catch (Exception ex)
                {
                    LogAndOutput($"Error analyzing position at depth {currentNode.Depth}: {ex.Message}");
                    continue;
                }
            }

            var duration = DateTime.Now - startTime;
            LogAndOutput($"Analysis completed in {duration.TotalSeconds:F1} seconds");
            LogAndOutput($"Total positions analyzed: {positionsAnalyzed}");

            // Save results with proper file management
            await SaveAnalysisResults(game, root, settings, startTime);

            return root;
        }

        private string GenerateProperMoveSequence(AnalysisTreeNode node)
        {
            if (node.Depth == 0) return "Starting position";
            
            var path = node.GetPathFromRoot();
            var moves = new List<string>();
            
            for (int i = 1; i < path.Count; i++)
            {
                var moveNode = path[i];
                var moveNum = moveNode.Position.MoveNumber - 1; // Previous move number
                var isWhiteMove = !moveNode.Position.WhiteToMove; // Previous move was opposite color
                
                if (isWhiteMove)
                {
                    moves.Add($"{moveNum}.{moveNode.Move.SAN}");
                }
                else
                {
                    if (moves.Count == 0 || !moves.Last().Contains("..."))
                    {
                        moves.Add($"{moveNum}...{moveNode.Move.SAN}");
                    }
                    else
                    {
                        moves.Add(moveNode.Move.SAN);
                    }
                }
            }
            
            return string.Join(" ", moves);
        }

        private List<AnalyzedMove> FilterMoves(List<AnalyzedMove> moves, bool isWhiteToMove, int whiteThreshold, int blackThreshold)
        {
            if (moves.Count <= 1) return moves;

            var bestMove = moves[0];
            var threshold = isWhiteToMove ? whiteThreshold : blackThreshold;
            
            // For mate scores, only show the mate
            if (bestMove.IsMate && 
                ((isWhiteToMove && bestMove.MateInMoves > 0) || (!isWhiteToMove && bestMove.MateInMoves < 0)))
            {
                return new List<AnalyzedMove> { bestMove };
            }

            var result = new List<AnalyzedMove>();
            foreach (var move in moves)
            {
                // Don't filter mate moves for the opponent
                if (move.IsMate) 
                {
                    result.Add(move);
                    continue;
                }

                var evalDiff = Math.Abs(move.Evaluation - bestMove.Evaluation);
                if (evalDiff <= threshold)
                {
                    result.Add(move);
                }
            }

            return result.Count > 0 ? result : new List<AnalyzedMove> { bestMove };
        }

        private async Task SaveAnalysisResults(ChessGameModel game, AnalysisTreeNode root, AnalysisSettings settings, DateTime startTime)
        {
            try
            {
                var timestamp = startTime.ToString("yyyyMMdd_HHmmss");
                var outputDir = !string.IsNullOrEmpty(settings.OutputDirectory) ? 
                    settings.OutputDirectory : Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
                
                // Ensure output directory exists
                Directory.CreateDirectory(outputDir);
                
                var baseFileName = Path.Combine(outputDir, $"{settings.BaseFilename}_{timestamp}");

                // Save diagnostics file
                if (settings.AutoSaveDiagnostics)
                {
                    var diagnosticsFileName = baseFileName + "_diagnostics.txt";
                    await File.WriteAllLinesAsync(diagnosticsFileName, _allDiagnostics);
                    LogAndOutput($"Diagnostics saved to: {Path.GetFileName(diagnosticsFileName)}");
                }

                // Save PGN with actual analysis tree
                if (settings.SavePGN)
                {
                    var pgnFileName = baseFileName + ".pgn";
                    var pgnContent = GenerateProperPGN(game, root);
                    await File.WriteAllTextAsync(pgnFileName, pgnContent);
                    LogAndOutput($"Analysis saved to PGN: {Path.GetFileName(pgnFileName)}");
                }

                // Save JSON
                if (settings.SaveJSON)
                {
                    var jsonFileName = baseFileName + ".json";
                    var jsonContent = Newtonsoft.Json.JsonConvert.SerializeObject(root, Newtonsoft.Json.Formatting.Indented);
                    await File.WriteAllTextAsync(jsonFileName, jsonContent);
                    LogAndOutput($"Analysis saved to JSON: {Path.GetFileName(jsonFileName)}");
                }
            }
            catch (Exception ex)
            {
                LogAndOutput($"Error saving results: {ex.Message}");
            }
        }

        private string GenerateProperPGN(ChessGameModel game, AnalysisTreeNode root)
        {
            var pgn = new System.Text.StringBuilder();
            
            // PGN headers
            pgn.AppendLine("[Event \"Chess Tree Analysis\"]");
            pgn.AppendLine($"[Date \"{DateTime.Now:yyyy.MM.dd}\"]");
            pgn.AppendLine("[White \"Analysis\"]");
            pgn.AppendLine("[Black \"Analysis\"]");
            pgn.AppendLine("[Result \"*\"]");
            pgn.AppendLine($"[FEN \"{root.Position.FEN}\"]");
            pgn.AppendLine();
            
            // Generate move tree
            pgn.AppendLine(GeneratePGNFromTree(root, 0));
            
            return pgn.ToString();
        }

        private string GeneratePGNFromTree(AnalysisTreeNode node, int depth)
        {
            if (node.Children.Count == 0) return "";
            
            var result = new System.Text.StringBuilder();
            var moveNum = node.Position.MoveNumber;
            
            for (int i = 0; i < node.Children.Count; i++)
            {
                var child = node.Children[i];
                var isMainLine = i == 0;
                
                if (!isMainLine) result.Append("( ");
                
                // Add move number if needed
                if (node.Position.WhiteToMove)
                {
                    result.Append($"{moveNum}.");
                }
                else if (isMainLine && result.Length == 0)
                {
                    result.Append($"{moveNum}...");
                }
                
                result.Append($"{child.Move.SAN} ");
                
                // Add evaluation comment
                var evalComment = child.IsMateScore ? 
                    $"{{M{child.MateInMoves}}}" : 
                    $"{{{child.Evaluation:+0;-#}}}";
                result.Append($"{evalComment} ");
                
                // Recursively add child moves
                result.Append(GeneratePGNFromTree(child, depth + 1));
                
                if (!isMainLine) result.Append(") ");
            }
            
            return result.ToString();
        }

        private void LogAndOutput(string message)
        {
            var timestampedMessage = $"[{DateTime.Now:HH:mm:ss}] {message}";
            _allDiagnostics.Add(timestampedMessage);
            OnAnalysisOutputReceived(message);
        }

        public void StopAnalysis()
        {
            if (_isAnalyzing && _cancellationTokenSource != null)
            {
                _cancellationTokenSource.Cancel();
            }
        }

        protected virtual void OnAnalysisProgressChanged(AnalysisProgressEventArgs e)
        {
            AnalysisProgressChanged?.Invoke(this, e);
        }

        protected virtual void OnAnalysisCompleted(AnalysisCompletedEventArgs e)
        {
            AnalysisCompleted?.Invoke(this, e);
        }

        protected virtual void OnAnalysisOutputReceived(string output)
        {
            AnalysisOutputReceived?.Invoke(this, output);
        }
    }
}