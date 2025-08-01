using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ChessTreeAnalyzer.Models;

namespace ChessTreeAnalyzer.Services
{
    public class ChessAnalysisService
    {
        private readonly StockfishService _stockfishService;
        private CancellationTokenSource _cancellationTokenSource;
        private bool _isAnalyzing = false;

        public event EventHandler<AnalysisProgressEventArgs> AnalysisProgressChanged;
        public event EventHandler<AnalysisCompletedEventArgs> AnalysisCompleted;
        public event EventHandler<string> AnalysisOutputReceived;

        public bool IsAnalyzing => _isAnalyzing;

        public ChessAnalysisService(StockfishService stockfishService)
        {
            _stockfishService = stockfishService ?? throw new ArgumentNullException(nameof(stockfishService));
        }

        public async Task StartAnalysisAsync(ChessGameModel game, AnalysisSettings settings)
        {
            if (_isAnalyzing)
                throw new InvalidOperationException("Analysis already in progress");

            _isAnalyzing = true;
            _cancellationTokenSource = new CancellationTokenSource();

            try
            {
                // Initialize Stockfish if not already done
                if (!_stockfishService.IsInitialized)
                {
                    OnAnalysisOutputReceived("Initializing Stockfish engine...");
                    await _stockfishService.InitializeAsync(settings.StockfishPath, settings);
                    OnAnalysisOutputReceived("Stockfish initialized successfully.");
                }

                // Validate settings
                settings.Validate();

                OnAnalysisOutputReceived($"Starting analysis with depth {settings.MaxDepth}, time {settings.TimePerPosition.TotalSeconds}s per position");
                OnAnalysisOutputReceived($"White: {settings.WhiteMovesToAnalyze} moves, threshold {settings.WhiteThreshold}cp");
                OnAnalysisOutputReceived($"Black: {settings.BlackMovesToAnalyze} moves, threshold {settings.BlackThreshold}cp");

                // Start analysis
                var result = await PerformAnalysisAsync(game, settings, _cancellationTokenSource.Token);

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
                OnAnalysisOutputReceived("Analysis cancelled by user.");
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
                OnAnalysisOutputReceived($"Analysis error: {ex.Message}");
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

        public void StopAnalysis()
        {
            if (_isAnalyzing && _cancellationTokenSource != null)
            {
                _cancellationTokenSource.Cancel();
            }
        }

        private async Task<AnalysisTreeNode> PerformAnalysisAsync(ChessGameModel game, 
            AnalysisSettings settings, CancellationToken cancellationToken)
        {
            var startTime = DateTime.Now;
            var totalPositions = CalculateEstimatedPositions(settings.MaxDepth, 
                Math.Max(settings.WhiteMovesToAnalyze, settings.BlackMovesToAnalyze));
            var positionsAnalyzed = 0;

            // Create root node from current game position
            var rootPosition = game.GetCurrentPosition();
            var root = new AnalysisTreeNode
            {
                Position = rootPosition,
                Move = null,
                Depth = 0,
                Evaluation = 0
            };

            // Build tree using breadth-first search
            var queue = new Queue<AnalysisTreeNode>();
            queue.Enqueue(root);

            while (queue.Count > 0 && !cancellationToken.IsCancellationRequested)
            {
                var currentNode = queue.Dequeue();

                // Stop if we've reached maximum depth
                if (currentNode.Depth >= settings.MaxDepth)
                    continue;

                // Skip if game is over
                if (currentNode.Position.IsGameOver)
                    continue;

                try
                {
                    positionsAnalyzed++;
                    var progressPercentage = Math.Min(100, (positionsAnalyzed * 100) / totalPositions);

                    // Generate move sequence for display
                    var moveSequence = GenerateMoveSequence(currentNode, game);
                    OnAnalysisProgressChanged(new AnalysisProgressEventArgs
                    {
                        ProgressPercentage = progressPercentage,
                        PositionsAnalyzed = positionsAnalyzed,
                        TotalPositions = totalPositions,
                        CurrentMove = moveSequence
                    });

                    OnAnalysisOutputReceived($"Analyzing depth {currentNode.Depth}, position {positionsAnalyzed}... {moveSequence}");

                    // Determine moves to analyze based on whose turn it is
                    var movesToAnalyze = currentNode.Position.WhiteToMove ? 
                        settings.WhiteMovesToAnalyze : settings.BlackMovesToAnalyze;

                    // Analyze position
                    var analyzedMoves = await _stockfishService.AnalyzePositionAsync(
                        currentNode.Position, movesToAnalyze, settings.TimePerPosition, cancellationToken);

                    if (analyzedMoves.Count == 0)
                    {
                        OnAnalysisOutputReceived($"No moves found for position at depth {currentNode.Depth}");
                        continue;
                    }

                    // Filter moves based on threshold
                    var filteredMoves = FilterMoves(analyzedMoves, currentNode.Position.WhiteToMove,
                        settings.WhiteThreshold, settings.BlackThreshold);

                    OnAnalysisOutputReceived($"Found {analyzedMoves.Count} moves, using {filteredMoves.Count} after filtering");

                    // Show top move
                    if (filteredMoves.Count > 0)
                    {
                        var topMove = filteredMoves[0];
                        var moveNumber = currentNode.Position.MoveNumber;
                        var side = currentNode.Position.WhiteToMove ? "" : "...";
                        OnAnalysisOutputReceived($"Top move: {moveNumber}.{side} {topMove.MoveNotation} {topMove.EvaluationText}");
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
                            Evaluation = analyzedMove.Evaluation,
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
                    OnAnalysisOutputReceived($"Error analyzing position at depth {currentNode.Depth}: {ex.Message}");
                    continue;
                }
            }

            var duration = DateTime.Now - startTime;
            OnAnalysisOutputReceived($"Analysis completed in {duration.TotalSeconds:F1} seconds");
            OnAnalysisOutputReceived($"Positions analyzed: {positionsAnalyzed}");

            // Update game with analysis result
            game.AnalysisTree = root;

            return root;
        }

        private string GenerateMoveSequence(AnalysisTreeNode node, ChessGameModel game)
        {
            var moves = new List<string>();
            var path = node.GetPathFromRoot();

            // Add game moves context for root position
            if (path.Count == 1 && game.GameMoves.Count > 0)
            {
                // Show last few moves for context
                var contextMoves = game.GameMoves.TakeLast(2).ToList();
                var tempBoard = new SimpleChessBoard(game.InitialPosition.FEN);
                
                // Apply moves before context
                for (int i = 0; i < game.GameMoves.Count - contextMoves.Count; i++)
                {
                    tempBoard = tempBoard.MakeMove(game.GameMoves[i].SAN);
                }

                // Add context moves
                foreach (var move in contextMoves)
                {
                    var moveNumber = tempBoard.MoveNumber;
                    var san = move.SAN; // Get SAN notation from SimpleMove
                    if (tempBoard.WhiteToMove)
                        moves.Add($"{moveNumber}.{san}");
                    else
                        moves.Add(san);
                    tempBoard = tempBoard.MakeMove(san);
                }
            }

            // Add analysis path moves (skip root)
            var board = game.GetCurrentPosition();
            foreach (var pathNode in path.Skip(1))
            {
                if (pathNode.Move != null)
                {
                    var moveNumber = board.MoveNumber;
                    var san = pathNode.Move.SAN;
                    if (board.WhiteToMove)
                        moves.Add($"{moveNumber}.{san}");
                    else
                        moves.Add(san);
                    board = board.MakeMove(pathNode.Move.SAN);
                }
            }

            return string.Join(" ", moves);
        }

        private List<AnalyzedMove> FilterMoves(List<AnalyzedMove> moves, bool isWhiteToMove, 
            int whiteThreshold, int blackThreshold)
        {
            if (moves.Count == 0) return moves;

            var threshold = isWhiteToMove ? whiteThreshold : blackThreshold;
            var bestMove = moves.First();

            // If best move is mate, only return that move
            if (bestMove.IsMate)
                return new List<AnalyzedMove> { bestMove };

            // Filter moves based on threshold
            var filtered = new List<AnalyzedMove>();
            foreach (var move in moves)
            {
                if (move.IsMate)
                {
                    // Include mate moves only if they're good for the current player
                    if ((isWhiteToMove && move.MateInMoves > 0) || 
                        (!isWhiteToMove && move.MateInMoves < 0))
                    {
                        filtered.Add(move);
                    }
                }
                else
                {
                    // Filter by centipawn threshold
                    var evalDiff = isWhiteToMove ? 
                        bestMove.Evaluation - move.Evaluation : 
                        move.Evaluation - bestMove.Evaluation;
                    
                    if (evalDiff <= threshold)
                    {
                        filtered.Add(move);
                    }
                }
            }

            return filtered.Count > 0 ? filtered : new List<AnalyzedMove> { bestMove };
        }

        private int CalculateEstimatedPositions(int maxDepth, int avgMovesPerPosition)
        {
            int total = 0;
            int positions = 1;
            
            for (int depth = 0; depth < maxDepth; depth++)
            {
                total += positions;
                positions *= avgMovesPerPosition;
            }
            
            return total;
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

    public class AnalysisProgressEventArgs : EventArgs
    {
        public int ProgressPercentage { get; set; }
        public int PositionsAnalyzed { get; set; }
        public int TotalPositions { get; set; }
        public string CurrentMove { get; set; } = "";
    }

    public class AnalysisCompletedEventArgs : EventArgs
    {
        public bool Success { get; set; }
        public AnalysisTreeNode AnalysisResult { get; set; }
        public int PositionsAnalyzed { get; set; }
        public string ErrorMessage { get; set; }
    }
}