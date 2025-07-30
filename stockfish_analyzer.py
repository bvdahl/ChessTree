"""
Stockfish Analyzer for chess position analysis.
"""

import os
import psutil
from typing import List, Dict, Any, Optional
import chess
import chess.engine


class StockfishAnalyzer:
    """
    Wrapper class for Stockfish engine analysis with optimized configuration.
    """
    
    def __init__(self, stockfish_path: str, analysis_time: float = 60.0, num_moves: int = 3, hash_memory_mb: int = 8192):
        """
        Initialize Stockfish analyzer with optimal system configuration.
        
        Args:
            stockfish_path: Path to Stockfish executable
            analysis_time: Time limit for analysis in seconds (default: 60.0)
            num_moves: Number of top moves to analyze (default: 3)
            hash_memory_mb: Memory allocation for hash table in MB (default: 8192)
            
        Raises:
            RuntimeError: If Stockfish engine cannot be initialized
        """
        self.stockfish_path = stockfish_path
        self.analysis_time = analysis_time
        self.num_moves = num_moves
        self.hash_memory_mb = hash_memory_mb
        self.engine = None
        
        # Initialize engine with optimal configuration
        self._initialize_engine()
    
    def _initialize_engine(self):
        """
        Initialize Stockfish engine with optimal system resource configuration.
        
        Raises:
            RuntimeError: If engine initialization fails
        """
        try:
            # Check if Stockfish executable exists
            if not os.path.isfile(self.stockfish_path):
                raise RuntimeError(f"Stockfish executable not found: {self.stockfish_path}")
            
            # Initialize engine
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            
            # Configure engine with optimal settings
            self._configure_engine()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Stockfish engine: {e}")
    
    def _configure_engine(self):
        """
        Configure Stockfish engine with optimal system resources.
        """
        if not self.engine:
            return
            
        try:
            # Auto-detect number of CPU threads
            num_threads = os.cpu_count() or 1
            print(f"Detected {num_threads} CPU threads")
            
            # Set threads (use all available threads)
            self.engine.configure({"Threads": num_threads})
            
            # Configure memory allocation for hash table
            total_memory_mb = psutil.virtual_memory().total // (1024 * 1024)
            # Use exactly the requested hash memory amount without any limits
            hash_size_mb = self.hash_memory_mb
            print(f"Detected {total_memory_mb}MB total RAM, allocating {hash_size_mb}MB for hash table")
            
            # Set hash table size
            self.engine.configure({"Hash": hash_size_mb})
            
            # Additional optimizations
            self.engine.configure({
                "Ponder": False,  # Disable pondering for consistent timing
                "MultiPV": self.num_moves,     # Analyze requested number of top moves
            })
            
        except Exception as e:
            print(f"Warning: Could not configure all engine options: {e}")
            # Continue with default settings if configuration fails
    
    def analyze_position(self, board: chess.Board) -> List[Dict[str, Any]]:
        """
        Analyze a chess position and return the top moves with evaluations.
        
        Args:
            board: Chess board position to analyze
            
        Returns:
            List of dictionaries containing move analysis results.
            Each dictionary has keys: 'move', 'evaluation', 'pv' (principal variation)
            
        Raises:
            RuntimeError: If analysis fails
        """
        if not self.engine:
            raise RuntimeError("Engine not initialized")
        
        if board.is_game_over():
            return []
        
        try:
            # Analyze position with time limit
            analysis = self.engine.analyse(
                board,
                chess.engine.Limit(time=self.analysis_time),
                multipv=self.num_moves  # Get requested number of top moves
            )
            
            results = []
            
            # Process analysis results
            for info in analysis:
                if 'pv' in info and info['pv']:
                    move = info['pv'][0]
                    
                    # Extract evaluation
                    evaluation = self._extract_evaluation(info, board.turn)
                    
                    # Extract principal variation
                    pv = [str(m) for m in info['pv'][:5]]  # First 5 moves of PV
                    
                    results.append({
                        'move': move,
                        'evaluation': evaluation,
                        'pv': pv,
                        'depth': info.get('depth', 0)
                    })
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Analysis failed: {e}")
    
    def _extract_evaluation(self, info: Any, white_to_move: bool):
        """
        Extract evaluation from engine analysis info.
        
        Args:
            info: Analysis info from engine
            white_to_move: True if it's White's turn
            
        Returns:
            Evaluation - either float (centipawns) or string (mate notation like '#5' or '-#3')
        """
        # Extract score from analysis info
        
        # Handle mate scores - return actual mate notation
        if 'score' in info:
            score_obj = info['score']
            
            # Try different methods to check for mate
            try:
                if hasattr(score_obj, 'is_mate') and score_obj.is_mate():
                    # Try various ways to get mate value
                    mate_in = None
                    
                    # Method 1: Direct mate() method
                    if hasattr(score_obj, 'mate'):
                        mate_in = score_obj.mate()
                    
                    # Method 2: Try white().mate() method  
                    elif hasattr(score_obj, 'white'):
                        white_score = score_obj.white()
                        if hasattr(white_score, 'mate'):
                            mate_in = white_score.mate()
                    
                    # Method 3: Try relative.mate() method
                    elif hasattr(score_obj, 'relative'):
                        relative_score = score_obj.relative
                        if hasattr(relative_score, 'mate'):
                            mate_in = relative_score.mate()
                    
                    if mate_in is not None:
                        # Return mate notation: #5 means mate in 5, -#3 means getting mated in 3
                        if mate_in > 0:
                            return f"#{mate_in}"  # Mate in N moves
                        else:
                            return f"-#{abs(mate_in)}"  # Getting mated in N moves
                            
            except Exception as e:
                # If mate detection fails, continue to centipawn handling
                print(f"Warning: Could not extract mate score: {e}")
                pass
        
        # Handle centipawn scores - try multiple methods
        if 'score' in info:
            score_obj = info['score']
            
            # Method 1: Direct cp access
            if hasattr(score_obj, 'cp') and score_obj.cp is not None:
                return float(score_obj.cp)
            
            # Method 2: Try white() method
            try:
                white_score = score_obj.white()
                if hasattr(white_score, 'cp') and white_score.cp is not None:
                    return float(white_score.cp)
            except:
                pass
            
            # Method 3: Try relative() method
            try:
                relative_score = score_obj.relative
                if hasattr(relative_score, 'cp') and relative_score.cp is not None:
                    return float(relative_score.cp)
            except:
                pass
        
        # Default to 0 if no score available
        return 0.0
        
    def is_mate_evaluation(self, evaluation) -> bool:
        """Check if evaluation represents a mate score."""
        return isinstance(evaluation, str) and ('#' in evaluation)
        
    def is_favorable_mate(self, evaluation) -> bool:
        """Check if mate evaluation is favorable (not getting mated)."""
        if not self.is_mate_evaluation(evaluation):
            return False
        return not evaluation.startswith('-')
        
    def is_unfavorable_mate(self, evaluation) -> bool:
        """Check if mate evaluation is unfavorable (getting mated)."""
        if not self.is_mate_evaluation(evaluation):
            return False
        return evaluation.startswith('-')
    
    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Get the best move for the current position.
        
        Args:
            board: Chess board position
            
        Returns:
            Best move or None if analysis fails
        """
        if not self.engine:
            return None
            
        try:
            result = self.engine.play(
                board,
                chess.engine.Limit(time=self.analysis_time)
            )
            return result.move
        except Exception:
            return None
    
    def close(self):
        """
        Close the Stockfish engine and free resources.
        """
        if self.engine:
            try:
                self.engine.quit()
            except Exception:
                pass  # Ignore errors during cleanup
            finally:
                self.engine = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
