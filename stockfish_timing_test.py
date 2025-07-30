#!/usr/bin/env python3
"""
Test script to investigate Stockfish's actual analysis timing and depth behavior.
"""

import chess
import chess.engine
import time
import sys

def test_stockfish_timing():
    """Test actual Stockfish analysis timing vs requested time limits."""
    
    # Complex middle game position that should require significant analysis
    test_positions = [
        "rnbqkb1r/ppp2ppp/8/4P3/8/2pP1N2/P1P3PP/R1BQKB1R w KQkq - 0 8",  # Complex tactical
        "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",  # Very complex
        "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"  # Endgame study
    ]
    
    time_limits = [5.0, 10.0, 30.0]  # Test different time limits
    
    try:
        print("Testing Stockfish timing behavior...")
        engine = chess.engine.SimpleEngine.popen_uci('./stockfish_engine')
        
        # Configure engine with large hash and threads
        engine.configure({
            'Hash': 4096,  # 4GB hash
            'Threads': 8
        })
        
        for i, fen in enumerate(test_positions):
            print(f"\n=== Position {i+1}: {fen[:30]}... ===")
            board = chess.Board(fen)
            
            for time_limit in time_limits:
                print(f"\nTesting {time_limit}s time limit:")
                
                # Measure actual analysis time
                start_time = time.time()
                
                # Single-PV analysis first
                result = engine.analyse(
                    board,
                    chess.engine.Limit(time=time_limit),
                    multipv=1
                )
                
                end_time = time.time()
                actual_time = end_time - start_time
                
                print(f"  Requested: {time_limit:.1f}s")
                print(f"  Actual: {actual_time:.2f}s ({actual_time/time_limit*100:.1f}% of limit)")
                print(f"  Depth reached: {result[0].get('depth', 'unknown') if result else 'unknown'}")
                print(f"  Nodes searched: {result[0].get('nodes', 'unknown') if result else 'unknown'}")
                
                # Test MultiPV=3
                start_time = time.time()
                
                multipv_result = engine.analyse(
                    board,
                    chess.engine.Limit(time=time_limit),
                    multipv=3
                )
                
                end_time = time.time()
                multipv_actual_time = end_time - start_time
                
                print(f"  MultiPV=3 actual: {multipv_actual_time:.2f}s ({multipv_actual_time/time_limit*100:.1f}% of limit)")
                print(f"  MultiPV results: {len(multipv_result)} moves")
                
                if len(multipv_result) > 0:
                    print(f"  MultiPV depth: {multipv_result[0].get('depth', 'unknown')}")
        
        engine.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

def test_depth_limits():
    """Test if Stockfish has internal depth limits that override time limits."""
    
    print("\n" + "="*60)
    print("TESTING DEPTH BEHAVIOR")
    print("="*60)
    
    try:
        engine = chess.engine.SimpleEngine.popen_uci('./stockfish_engine')
        
        # Simple position for depth testing
        board = chess.Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
        
        # Test different limit types
        limit_types = [
            ("Time: 30s", chess.engine.Limit(time=30.0)),
            ("Depth: 15", chess.engine.Limit(depth=15)),
            ("Nodes: 1M", chess.engine.Limit(nodes=1000000)),
            ("Time: 60s", chess.engine.Limit(time=60.0)),
        ]
        
        for label, limit in limit_types:
            print(f"\n--- {label} ---")
            
            start_time = time.time()
            result = engine.analyse(board, limit, multipv=1)
            end_time = time.time()
            
            actual_time = end_time - start_time
            
            print(f"Actual time: {actual_time:.2f}s")
            print(f"Depth reached: {result.get('depth', 'unknown')}")
            print(f"Nodes searched: {result.get('nodes', 'unknown'):,}")
            print(f"Evaluation: {result.get('score', 'unknown')}")
        
        engine.quit()
        
    except Exception as e:
        print(f"Error in depth testing: {e}")

if __name__ == "__main__":
    print("Stockfish Timing and Depth Analysis")
    print("=" * 50)
    
    if test_stockfish_timing():
        test_depth_limits()
    else:
        print("Failed to run timing tests")