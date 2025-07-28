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
    
    def __init__(self, stockfish_path: str, analysis_time: float = 1.0):
        """
        Initialize Stockfish analyzer with optimal system configuration.
        
        Args:
            stockfish_path: Path to Stockfish executable
            analysis_time: Time limit for analysis in seconds
            
        Raises:
            RuntimeError: If Stockfish engine cannot be initialized
        """
        self.stockfish_path = stockfish_path
        self.analysis_time = analysis_time
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
            
            # Auto-detect and configure memory (use half of available RAM)
            total_memory_mb = psutil.virtual_memory().total // (1024 * 1024)
            hash_size_mb = max(16, min(1024, total_memory_mb // 2))  # Between 16MB and 1GB
            print(f"Detected {total_memory_mb}MB total RAM, allocating {hash_size_mb}MB for hash table")
            
            # Set hash table size
            self.engine.configure({"Hash": hash_size_mb})
            
            # Additional optimizations
            self.engine.configure({
                "Ponder": False,  # Disable pondering for consistent timing
                "MultiPV": 3,     # Analyze top 3 moves
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
                multipv=3  # Get top 3 moves
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
    
    def _extract_evaluation(self, info: Any, white_to_move: bool) -> float:
        """
        Extract evaluation from engine analysis info.
        
        Args:
            info: Analysis info from engine
            white_to_move: True if it's White's turn
            
        Returns:
            Evaluation in centipawns from the perspective of the side to move
        """
        # Handle mate scores
        if 'score' in info and info['score'].is_mate():
            mate_in = info['score'].mate()
            if mate_in is not None:
                # Convert mate distance to large evaluation
                # Positive if favorable, negative if unfavorable
                if mate_in > 0:
                    return 10000 - mate_in  # Mate in N moves
                else:
                    return -10000 - mate_in  # Getting mated in N moves
        
        # Handle centipawn scores
        if 'score' in info and hasattr(info['score'], 'cp') and info['score'].cp is not None:
            cp_score = info['score'].cp
            
            # Return score from perspective of side to move
            if white_to_move:
                return float(cp_score)
            else:
                return float(-cp_score)
        
        # Default to 0 if no score available
        return 0.0
    
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
