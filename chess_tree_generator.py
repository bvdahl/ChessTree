#!/usr/bin/env python3
"""
Chess Game Tree Generator

A Python command-line tool that generates chess game trees using Stockfish engine analysis
with configurable depth and move filtering.
"""

import argparse
import json
import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Any
import chess
import chess.engine
import chess.pgn
import io
from contextlib import redirect_stdout
from stockfish_analyzer import StockfishAnalyzer
from tree_node import TreeNode


class ChessTreeGenerator:
    """Main class for generating chess game trees."""
    
    def __init__(self, stockfish_path: str, max_depth: int = 3, 
                 analysis_time: float = 60.0, 
                 white_threshold: int = 30, black_threshold: int = 30,
                 white_moves: int = 3, black_moves: int = 3,
                 hash_memory_mb: int = 8192):
        """
        Initialize the chess tree generator.
        
        Args:
            stockfish_path: Path to Stockfish engine executable
            max_depth: Maximum depth in half-moves (default: 3)
            analysis_time: Time to analyze each position in seconds (default: 1.0)
            white_threshold: Centipawn threshold for White move filtering (default: 30)
            black_threshold: Centipawn threshold for Black move filtering (default: 30)
            white_moves: Number of top moves to analyze for White positions (default: 3)
            black_moves: Number of top moves to analyze for Black positions (default: 3)
            hash_memory_mb: Memory allocation for hash table in MB (default: 8192)
        """
        self.stockfish_path = stockfish_path
        self.max_depth = max_depth
        self.analysis_time = analysis_time
        self.white_threshold = white_threshold
        self.black_threshold = black_threshold
        self.white_moves = white_moves
        self.black_moves = black_moves
        self.hash_memory_mb = hash_memory_mb
        
        # Use the maximum of white/black moves for analyzer initialization
        max_moves = max(white_moves, black_moves)
        self.analyzer = StockfishAnalyzer(stockfish_path, analysis_time, max_moves, hash_memory_mb)
        
        # Statistics tracking
        self.total_positions_analyzed = 0
        self.total_moves_after_filtering = 0
        self.start_time = None
        self.end_time = None
        
    def generate_tree_from_pgn(self, pgn_file: str) -> tuple[TreeNode, chess.pgn.Game]:
        """
        Generate a game tree from the last position in a PGN file.
        
        Args:
            pgn_file: Path to PGN file
            
        Returns:
            Tuple of (TreeNode root, chess.pgn.Game object)
        """
        with open(pgn_file, 'r') as f:
            game = chess.pgn.read_game(f)
        
        if game is None:
            raise ValueError(f"No valid game found in PGN file: {pgn_file}")
        
        # Play through the game to get the final position
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
        
        # Create root node from final position
        root = TreeNode(
            board=board.copy(),
            move=None,
            evaluation=None,
            depth=0
        )
        
        # Build tree from this position
        self.start_time = time.time()
        self._build_tree_breadth_first(root)
        self.end_time = time.time()
        
        return root, game

    def generate_tree(self, fen: str) -> TreeNode:
        """
        Generate a complete game tree from the given FEN position.
        
        Args:
            fen: FEN string representing the starting position
            
        Returns:
            TreeNode: Root node of the generated game tree
            
        Raises:
            ValueError: If FEN string is invalid
            RuntimeError: If Stockfish engine fails to initialize
        """
        try:
            board = chess.Board(fen)
        except ValueError as e:
            raise ValueError(f"Invalid FEN string: {fen}. Error: {e}")
        
        # Create root node
        root = TreeNode(
            board=board.copy(),
            move=None,
            evaluation=None,
            depth=0
        )
        
        # Build tree using breadth-first approach to ensure complete coverage
        self.start_time = time.time()
        self._build_tree_breadth_first(root)
        self.end_time = time.time()
        
        return root
    
    def _build_tree_breadth_first(self, root: TreeNode):
        """
        Build the game tree using breadth-first traversal to ensure completeness.
        
        Args:
            root: Root node of the tree
        """
        # Queue for breadth-first traversal: (node, current_depth)
        queue: List[tuple[TreeNode, int]] = [(root, 0)]
        
        while queue:
            current_node, current_depth = queue.pop(0)
            
            # Stop if we've reached maximum depth
            if current_depth >= self.max_depth:
                continue
            
            # Skip if game is over
            if current_node.board.is_game_over():
                continue
            
            try:
                # Show progress to console (bypasses diagnostics capture)
                original_stdout = sys.__stdout__
                original_stdout.write(f"\r📊 Analyzing depth {current_depth}, position {self.total_positions_analyzed + 1}...")
                original_stdout.flush()
                
                print(f"Analyzing position at depth {current_depth} (move {current_node.board.fullmove_number})")
                
                # Analyze current position
                analysis_results = self.analyzer.analyze_position(current_node.board)
                
                if not analysis_results:
                    print(f"No analysis results for depth {current_depth}")
                    continue
                
                print(f"Got {len(analysis_results)} moves from analysis")
                for i, move_data in enumerate(analysis_results):
                    print(f"  Move {i+1}: {move_data['move']} eval: {move_data['evaluation']}")
                
                # Filter moves based on centipawn threshold
                filtered_moves = self._filter_moves(analysis_results, current_node.board.turn)
                print(f"After filtering: {len(filtered_moves)} moves")
                
                # Track statistics (after filtering)
                self.total_positions_analyzed += 1
                self.total_moves_after_filtering += len(filtered_moves)
                
                # Create child nodes for filtered moves
                for move_data in filtered_moves:
                    move = move_data['move']
                    evaluation = move_data['evaluation']
                    
                    # Make the move on a copy of the board
                    child_board = current_node.board.copy()
                    child_board.push(move)
                    
                    # Create child node
                    child_node = TreeNode(
                        board=child_board,
                        move=move,
                        evaluation=evaluation,
                        depth=current_depth + 1
                    )
                    
                    current_node.children.append(child_node)
                    
                    # Add child to queue for further expansion
                    queue.append((child_node, current_depth + 1))
                    
            except Exception as e:
                print(f"Error analyzing position at depth {current_depth}: {e}", file=sys.stderr)
                continue
    
    def _filter_moves(self, analysis_results: List[Dict[str, Any]], is_white_to_move: bool) -> List[Dict[str, Any]]:
        """
        Filter moves based on evaluation with special mate handling and side-specific parameters.
        
        Args:
            analysis_results: List of move analysis results from Stockfish
            is_white_to_move: True if White to move, False if Black to move
            
        Returns:
            List of filtered moves (maximum num_moves for current side, within centipawn threshold)
        """
        if not analysis_results:
            return []
        
        # Get side-specific parameters
        current_threshold = self.white_threshold if is_white_to_move else self.black_threshold
        current_max_moves = self.white_moves if is_white_to_move else self.black_moves
        
        # Sort moves by evaluation with mate-aware comparison
        sorted_moves = sorted(analysis_results, key=lambda x: self._get_sort_value(x['evaluation'], is_white_to_move), reverse=True)
        
        best_move = sorted_moves[0]
        best_eval = best_move['evaluation']
        
        # Special case: If best move is a forced mate for current player, only return that move
        if self._is_mate_evaluation(best_eval) and self._is_mate_for_current_player(best_eval, is_white_to_move):
            print(f"  Found forced mate: {best_move['move']} {best_eval} - ending variation here")
            return [best_move]
        
        # Take best move
        filtered_moves = [best_move]
        
        # Add additional moves up to current_max_moves if within threshold
        filtered_out = []
        for move_data in sorted_moves[1:current_max_moves]:
            move_eval = move_data['evaluation']
            
            # Filter out moves that lead to opponent mate (regardless of threshold)
            if self._is_mate_evaluation(move_eval) and self._is_mate_for_opponent(move_eval, is_white_to_move):
                print(f"  Filtered mate-losing move: {move_data['move']} {move_eval}")
                filtered_out.append(move_data)
                continue
            
            # For non-mate moves, apply centipawn threshold
            if not self._is_mate_evaluation(best_eval) and not self._is_mate_evaluation(move_eval):
                if is_white_to_move:
                    eval_diff = best_eval - move_eval  # Positive difference for White
                else:
                    eval_diff = move_eval - best_eval  # Positive difference for Black
                    
                if eval_diff <= current_threshold:
                    filtered_moves.append(move_data)
                else:
                    filtered_out.append(move_data)
            else:
                # Include other favorable moves when dealing with mates
                filtered_moves.append(move_data)
        
        # Add remaining moves as filtered out
        for move_data in sorted_moves[current_max_moves:]:
            filtered_out.append(move_data)
        
        # Print filtered out moves
        if filtered_out:
            player = "White" if is_white_to_move else "Black"
            print(f"  Filtered out {len(filtered_out)} moves for {player} (threshold: {current_threshold}cp, max_moves: {current_max_moves}):")
            for move in filtered_out:
                print(f"    {move['move']} eval: {move['evaluation']}")
        
        return filtered_moves
    
    def _is_mate_evaluation(self, evaluation) -> bool:
        """Check if evaluation represents a mate score."""
        return isinstance(evaluation, str) and ('#' in evaluation)
        
    def _is_mate_for_current_player(self, evaluation, is_white_to_move: bool) -> bool:
        """Check if mate evaluation represents current player delivering mate."""
        if not self._is_mate_evaluation(evaluation):
            return False
        
        # #N means White delivers mate, -#N means Black delivers mate
        white_has_mate = not evaluation.startswith('-')
        return white_has_mate == is_white_to_move
        
    def _is_mate_for_opponent(self, evaluation, is_white_to_move: bool) -> bool:
        """Check if mate evaluation represents opponent delivering mate."""
        if not self._is_mate_evaluation(evaluation):
            return False
        
        # #N means White delivers mate, -#N means Black delivers mate
        white_has_mate = not evaluation.startswith('-')
        return white_has_mate != is_white_to_move
    
    def _get_sort_value(self, evaluation, is_white_to_move: bool) -> float:
        """Convert evaluation to sortable numeric value."""
        if self._is_mate_evaluation(evaluation):
            # Parse mate notation: #5 means White mates in 5, -#3 means Black mates in 3
            if evaluation.startswith('-#'):
                mate_moves = int(evaluation[2:])
                # Black has mate
                if is_white_to_move:
                    return -20000 + mate_moves  # Bad for White
                else:
                    return 20000 - mate_moves   # Good for Black
            else:  # #N
                mate_moves = int(evaluation[1:])
                # White has mate
                if is_white_to_move:
                    return 20000 - mate_moves   # Good for White
                else:
                    return -20000 + mate_moves  # Bad for Black
        else:
            # Regular centipawn evaluation
            eval_cp = float(evaluation)
            return eval_cp if is_white_to_move else -eval_cp
    
    def _format_evaluation(self, evaluation) -> str:
        """Format evaluation for PGN output."""
        if self._is_mate_evaluation(evaluation):
            return str(evaluation)  # Return mate notation as-is: #5 or -#3
        else:
            return f"{evaluation:+.0f}"  # Format centipawn with sign: +150, -75
    
    def tree_to_pgn(self, node: TreeNode, game_info: Dict[str, str] = None, existing_game: chess.pgn.Game = None) -> str:
        """
        Convert tree to PGN format with variations, optionally appending to existing game.
        
        Args:
            node: Root node of the tree
            game_info: Optional game information for PGN headers
            existing_game: Optional existing game to append analysis to
            
        Returns:
            PGN string with main line and variations
        """
        pgn_lines = []
        
        if existing_game:
            # Use existing game headers and moves
            headers = existing_game.headers
            for key, value in headers.items():
                pgn_lines.append(f'[{key} "{value}"]')
            
            # Add analysis comment
            pgn_lines.append('[Annotator "Chess Tree Generator"]')
            pgn_lines.append("")  # Empty line after headers
            
            # Get the main line moves from existing game
            board = existing_game.board()
            moves_list = []
            move_number = 1
            white_move = True
            
            for move in existing_game.mainline_moves():
                move_san = board.san(move)
                if white_move:
                    moves_list.append(f"{move_number}. {move_san}")
                else:
                    moves_list.append(move_san)
                    move_number += 1
                white_move = not white_move
                board.push(move)
            
            # Add original game moves
            game_moves = " ".join(moves_list)
            
            # Add analysis starting point
            starting_move_num = board.fullmove_number
            analysis_moves = self._node_to_pgn_moves(node, board.turn, starting_move_num)
            
            if analysis_moves:
                pgn_lines.append(f"{game_moves} {analysis_moves} *")
            else:
                pgn_lines.append(f"{game_moves} *")
                
        else:
            # Create new PGN from scratch
            if game_info is None:
                game_info = {
                    "Event": "Chess Tree Analysis",
                    "Site": "Local Analysis", 
                    "Date": "????.??.??",
                    "Round": "?",
                    "White": "?",
                    "Black": "?",
                    "Result": "*",
                    "FEN": node.board.fen()
                }
            
            # Create PGN headers
            for key, value in game_info.items():
                pgn_lines.append(f'[{key} "{value}"]')
            pgn_lines.append("")  # Empty line after headers
            
            # Convert tree to moves with variations
            starting_move_num = node.board.fullmove_number
            moves_text = self._node_to_pgn_moves(node, node.board.turn, starting_move_num)
            pgn_lines.append(f"{moves_text} *" if moves_text else "*")
        
        return "\n".join(pgn_lines)
    
    def _node_to_pgn_moves(self, node: TreeNode, starting_turn: bool, move_number: int = 1) -> str:
        """
        Convert tree to proper PGN format with full recursive depth.
        Generates variations to match the analysis depth configured by the user.
        """
        if not node.children:
            return ""
        
        # Build the complete tree structure to full requested depth
        tree_text = self._build_complete_tree(node, starting_turn, move_number)
        return tree_text
    
    def _build_tree_stack_based(self, root: TreeNode, starting_turn: bool, move_number: int) -> str:
        """Build complete tree with proper variations using controlled depth."""
        if not root.children:
            return ""
        
        def build_simple_line(node: TreeNode, turn: bool, move_num: int, max_levels: int) -> str:
            """Build just the main line with variations at each level."""
            if not node.children or max_levels <= 0:
                return ""
            
            parts = []
            
            # Main move
            main_child = node.children[0]
            main_san = node.board.san(main_child.move)
            main_eval = f" {{{self._format_evaluation(main_child.evaluation)}}}" if main_child.evaluation is not None else ""
            
            if turn:
                main_move = f"{move_num}. {main_san}{main_eval}"
                next_turn = False
                next_move_num = move_num
            else:
                main_move = f"{move_num}... {main_san}{main_eval}"
                next_turn = True
                next_move_num = move_num + 1
            
            parts.append(main_move)
            
            # Add variations WITH their full continuations
            for alt_child in node.children[1:]:
                alt_san = node.board.san(alt_child.move)
                alt_eval = f" {{{self._format_evaluation(alt_child.evaluation)}}}" if alt_child.evaluation is not None else ""
                
                if turn:
                    var_start = f"({move_num}. {alt_san}{alt_eval}"
                    var_next_turn = False
                    var_next_move_num = move_num
                else:
                    var_start = f"({move_num}... {alt_san}{alt_eval}"
                    var_next_turn = True
                    var_next_move_num = move_num + 1
                
                # Build the FULL continuation for this variation
                if alt_child.children and max_levels > 1:
                    var_continuation = build_simple_line(alt_child, var_next_turn, var_next_move_num, max_levels - 1)
                    if var_continuation:
                        parts.append(var_start + " " + var_continuation + ")")
                    else:
                        parts.append(var_start + ")")
                else:
                    parts.append(var_start + ")")
            
            # Continue main line
            if main_child.children and max_levels > 1:
                continuation = build_simple_line(main_child, next_turn, next_move_num, max_levels - 1)
                if continuation:
                    parts.append(continuation)
            
            return " ".join(parts)
        
        return build_simple_line(root, starting_turn, move_number, 8)
    
    def _build_full_variation(self, parent_node: TreeNode, child_node: TreeNode, starting_turn: bool, move_number: int, depth_limit: int) -> str:
        """Build a complete variation including all its sub-variations."""
        if depth_limit <= 0:
            return ""
            
        move_san = parent_node.board.san(child_node.move)
        move_eval = f" {{{child_node.evaluation:+.0f}}}" if child_node.evaluation is not None else ""
        
        if starting_turn:
            var_start = f"({move_number}. {move_san}{move_eval}"
            next_turn = False
            next_move_num = move_number
        else:
            var_start = f"({move_number}... {move_san}{move_eval}"
            next_turn = True
            next_move_num = move_number + 1
        
        # If this variation has children, build the complete sub-tree
        if child_node.children and depth_limit > 1:
            continuation = self._build_tree_simple_recursive(child_node, next_turn, next_move_num, depth_limit - 1)
            if continuation:
                return var_start + " " + continuation + ")"
        
        return var_start + ")"
    
    def _build_tree_simple_recursive(self, node: TreeNode, starting_turn: bool, move_number: int, depth_limit: int) -> str:
        """Simple recursive tree builder with strict depth limit."""
        if not node.children or depth_limit <= 0:
            return ""
        
        parts = []
        
        # Main move
        main_child = node.children[0]
        main_san = node.board.san(main_child.move)
        main_eval = f" {{{main_child.evaluation:+.0f}}}" if main_child.evaluation is not None else ""
        
        if starting_turn:
            main_move = f"{move_number}. {main_san}{main_eval}"
            next_turn = False
            next_move_num = move_number
        else:
            main_move = f"{move_number}... {main_san}{main_eval}"
            next_turn = True
            next_move_num = move_number + 1
        
        parts.append(main_move)
        
        # Alternative moves as variations
        for alt_child in node.children[1:]:
            alt_san = node.board.san(alt_child.move)
            alt_eval = f" {{{alt_child.evaluation:+.0f}}}" if alt_child.evaluation is not None else ""
            
            if starting_turn:
                alt_var = f"({move_number}. {alt_san}{alt_eval})"
            else:
                alt_var = f"({move_number}... {alt_san}{alt_eval})"
            
            parts.append(alt_var)
        
        # Continue with main line only (simplified approach)
        if main_child.children and depth_limit > 1:
            continuation = self._build_tree_simple_recursive(main_child, next_turn, next_move_num, depth_limit - 1)
            if continuation:
                parts.append(continuation)
        
        return " ".join(parts)
    
    def _build_complete_tree(self, node: TreeNode, starting_turn: bool, move_number: int) -> str:
        """Build complete tree using stack-based approach."""
        return self._build_tree_stack_based(node, starting_turn, move_number)
    
    def _build_complete_tree_internal(self, node: TreeNode, starting_turn: bool, move_number: int, max_depth: int) -> str:
        """
        Build complete PGN tree recursively following all branches to full depth.
        
        Args:
            node: Current node in tree
            starting_turn: True if White to move, False if Black
            move_number: Current move number
            max_depth: Maximum recursion depth to prevent infinite loops
            
        Returns:
            Complete PGN string with all variations
        """
        if not node.children or max_depth <= 0:
            return ""
        
        parts = []
        
        # Step 1: Main move (best move at current position)
        main_child = node.children[0]
        main_san = node.board.san(main_child.move)
        main_eval = f" {{{main_child.evaluation:+.0f}}}" if main_child.evaluation is not None else ""
        
        if starting_turn:
            main_move = f"{move_number}. {main_san}{main_eval}"
            response_turn = False
            response_move_num = move_number
        else:
            main_move = f"{move_number}... {main_san}{main_eval}"
            response_turn = True
            response_move_num = move_number + 1
        
        parts.append(main_move)
        
        # Step 2: Build variations for alternative first moves  
        for alt_child in node.children[1:]:
            alt_variation = self._build_variation_simple(node, alt_child, starting_turn, move_number, max_depth)
            if alt_variation:
                parts.append(alt_variation)
        
        # Step 3: Main response (best response to main move)
        if main_child.children:
            main_response = main_child.children[0]
            response_san = main_child.board.san(main_response.move)
            response_eval = f" {{{main_response.evaluation:+.0f}}}" if main_response.evaluation is not None else ""
            
            if response_turn:
                response_move = f"{response_move_num}. {response_san}{response_eval}"
                final_turn = False
                final_move_num = response_move_num
            else:
                response_move = f"{response_move_num}... {response_san}{response_eval}"
                final_turn = True
                final_move_num = response_move_num + 1
            
            parts.append(response_move)
            
            # Step 4: Build variations for alternative responses
            for alt_response in main_child.children[1:]:
                alt_resp_var = self._build_variation_simple(main_child, alt_response, response_turn, response_move_num, max_depth)
                if alt_resp_var:
                    parts.append(alt_resp_var)
            
            # Step 5: Continue with children of main response (with depth limit)
            if main_response.children and max_depth > 1:
                continuation = self._build_complete_tree_internal(main_response, final_turn, final_move_num, max_depth - 1)
                if continuation:
                    parts.append(continuation)
        
        return " ".join(parts)
    
    def _build_manual_style_variation(self, parent_node: TreeNode, child_node: TreeNode, 
                                     starting_turn: bool, move_number: int) -> str:
        """Build variation exactly like the manual example with all responses and continuations."""
        try:
            # Start the variation
            move_san = parent_node.board.san(child_node.move)
            move_eval = f" {{{child_node.evaluation:+.0f}}}" if child_node.evaluation is not None else ""
            
            if starting_turn:
                var_parts = [f"({move_number}. {move_san}{move_eval}"]
                next_turn = False
                next_move_num = move_number
            else:
                var_parts = [f"({move_number}... {move_san}{move_eval}"]
                next_turn = True
                next_move_num = move_number + 1
            
            if child_node.children:
                # Main response
                main_resp = child_node.children[0]
                resp_san = child_node.board.san(main_resp.move)
                resp_eval = f" {{{main_resp.evaluation:+.0f}}}" if main_resp.evaluation is not None else ""
                
                if next_turn:
                    resp_text = f"{next_move_num}. {resp_san}{resp_eval}"
                    final_turn = False
                    final_move_num = next_move_num
                else:
                    resp_text = f"{next_move_num}... {resp_san}{resp_eval}"
                    final_turn = True
                    final_move_num = next_move_num + 1
                
                var_parts.append(resp_text)
                
                # ALL alternative responses as sub-variations (this was missing!)
                for alt_resp in child_node.children[1:]:
                    alt_resp_san = child_node.board.san(alt_resp.move)
                    alt_resp_eval = f" {{{alt_resp.evaluation:+.0f}}}" if alt_resp.evaluation is not None else ""
                    
                    if next_turn:
                        sub_var_start = f"({next_move_num}. {alt_resp_san}{alt_resp_eval}"
                    else:
                        sub_var_start = f"({next_move_num}... {alt_resp_san}{alt_resp_eval}"
                    
                    # Add continuation for this alternative response
                    if alt_resp.children:
                        cont_child = alt_resp.children[0]
                        cont_san = alt_resp.board.san(cont_child.move)
                        cont_eval = f" {{{cont_child.evaluation:+.0f}}}" if cont_child.evaluation is not None else ""
                        
                        if final_turn:
                            cont_text = f"{final_move_num}. {cont_san}{cont_eval}"
                        else:
                            cont_text = f"{final_move_num}... {cont_san}{cont_eval}"
                        
                        # Add alternatives to this continuation
                        cont_parts = [cont_text]
                        for alt_cont in alt_resp.children[1:]:
                            alt_cont_var = self._build_variation_simple(alt_resp, alt_cont, final_turn, final_move_num)
                            if alt_cont_var:
                                cont_parts.append(alt_cont_var)
                        
                        sub_var = sub_var_start + " " + " ".join(cont_parts) + ")"
                    else:
                        sub_var = sub_var_start + ")"
                    
                    var_parts.append(sub_var)
                
                # Main continuation - recursive call for full depth  
                if main_resp.children:
                    continuation = self._build_complete_tree(main_resp, final_turn, final_move_num)
                    if continuation:
                        var_parts.append(continuation)
            
            return " ".join(var_parts) + ")"
            
        except Exception as e:
            print(f"Error building manual style variation: {e}", file=sys.stderr)
            return ""
    
    def _build_full_variation(self, parent_node: TreeNode, child_node: TreeNode, 
                             starting_turn: bool, move_number: int, depth_remaining: int) -> str:
        """Build a complete variation to full depth like the manual example."""
        if depth_remaining <= 0:
            return ""
        
        try:
            # Start the variation 
            move_san = parent_node.board.san(child_node.move)
            move_eval = f" {{{child_node.evaluation:+.0f}}}" if child_node.evaluation is not None else ""
            
            if starting_turn:
                var_parts = [f"({move_number}. {move_san}{move_eval}"]
                next_turn = False
                next_move_num = move_number
            else:
                var_parts = [f"({move_number}... {move_san}{move_eval}"]
                next_turn = True
                next_move_num = move_number + 1
            
            # Add all responses and their continuations
            if child_node.children:
                # Main response (best move)
                main_resp = child_node.children[0]
                resp_san = child_node.board.san(main_resp.move)
                resp_eval = f" {{{main_resp.evaluation:+.0f}}}" if main_resp.evaluation is not None else ""
                
                if next_turn:
                    resp_text = f"{next_move_num}. {resp_san}{resp_eval}"
                    final_turn = False
                    final_move_num = next_move_num
                else:
                    resp_text = f"{next_move_num}... {resp_san}{resp_eval}"
                    final_turn = True
                    final_move_num = next_move_num + 1
                
                var_parts.append(resp_text)
                
                # Add alternative responses FIRST (before main continuation)
                for alt_resp in child_node.children[1:]:
                    alt_resp_var = self._build_response_variation(child_node, alt_resp, next_turn, next_move_num, depth_remaining - 1)
                    if alt_resp_var:
                        var_parts.append(alt_resp_var)
                
                # Add recursive continuation for main response
                if main_resp.children:
                    continuation = self._build_complete_tree(main_resp, final_turn, final_move_num)
                    if continuation:
                        var_parts.append(continuation)
            
            return " ".join(var_parts) + ")"
            
        except Exception as e:
            print(f"Error building full variation: {e}", file=sys.stderr)
            return ""
    
    def _build_response_variation(self, parent_node: TreeNode, child_node: TreeNode,
                                 starting_turn: bool, move_number: int, depth_remaining: int) -> str:
        """Build a response variation with continuation."""
        if depth_remaining <= 0:
            return ""
        
        try:
            move_san = parent_node.board.san(child_node.move)
            move_eval = f" {{{child_node.evaluation:+.0f}}}" if child_node.evaluation is not None else ""
            
            if starting_turn:
                var_start = f"({move_number}. {move_san}{move_eval}"
                next_turn = False
                next_move_num = move_number
            else:
                var_start = f"({move_number}... {move_san}{move_eval}"
                next_turn = True
                next_move_num = move_number + 1
            
            # Add continuation if available
            if child_node.children and depth_remaining > 1:
                main_cont = child_node.children[0]
                cont_san = child_node.board.san(main_cont.move)
                cont_eval = f" {{{main_cont.evaluation:+.0f}}}" if main_cont.evaluation is not None else ""
                
                if next_turn:
                    cont_text = f"{next_move_num}. {cont_san}{cont_eval}"
                    final_turn = False
                    final_move_num = next_move_num
                else:
                    cont_text = f"{next_move_num}... {cont_san}{cont_eval}"
                    final_turn = True
                    final_move_num = next_move_num + 1
                
                # Add alternatives to continuation
                alt_parts = [cont_text]
                for alt_cont in main_cont.children[1:]:
                    alt_var = self._build_variation_simple(main_cont, alt_cont, final_turn, final_move_num)
                    if alt_var:
                        alt_parts.append(alt_var)
                
                return var_start + " " + " ".join(alt_parts) + ")"
            else:
                return var_start + ")"
                
        except Exception as e:
            print(f"Error building response variation: {e}", file=sys.stderr)
            return ""

    def _build_variation_branch(self, parent_node: TreeNode, child_node: TreeNode, 
                               starting_turn: bool, move_number: int, depth_remaining: int) -> str:
        """Build a complete variation branch like the manual example."""
        if depth_remaining <= 0:
            return ""
        
        try:
            # Start the variation
            move_san = parent_node.board.san(child_node.move)
            move_eval = f" {{{child_node.evaluation:+.0f}}}" if child_node.evaluation is not None else ""
            
            if starting_turn:
                var_start = f"({move_number}. {move_san}{move_eval}"
                next_turn = False
                next_move_num = move_number
            else:
                var_start = f"({move_number}... {move_san}{move_eval}"
                next_turn = True
                next_move_num = move_number + 1
            
            # Continue the variation if there are more moves
            continuation_parts = []
            
            if child_node.children and depth_remaining > 1:
                # Add main response
                main_resp = child_node.children[0]
                resp_san = child_node.board.san(main_resp.move)
                resp_eval = f" {{{main_resp.evaluation:+.0f}}}" if main_resp.evaluation is not None else ""
                
                if next_turn:
                    resp_text = f"{next_move_num}. {resp_san}{resp_eval}"
                    final_turn = False
                    final_move_num = next_move_num
                else:
                    resp_text = f"{next_move_num}... {resp_san}{resp_eval}"
                    final_turn = True
                    final_move_num = next_move_num + 1
                
                continuation_parts.append(resp_text)
                
                # Add recursive continuation 
                if main_resp.children:
                    continuation = self._build_complete_tree(main_resp, final_turn, final_move_num)
                    if continuation:
                        continuation_parts.append(continuation)
            
            # Combine all parts
            if continuation_parts:
                return var_start + " " + " ".join(continuation_parts) + ")"
            else:
                return var_start + ")"
                
        except Exception as e:
            print(f"Error building variation branch: {e}", file=sys.stderr)
            return ""
    
    def _build_variation_simple(self, parent_node: TreeNode, child_node: TreeNode, 
                               starting_turn: bool, move_number: int, max_depth: int = 20) -> str:
        """Build a variation with controlled recursion depth to avoid infinite loops."""
        try:
            if max_depth <= 0:
                return ""
                
            move_san = parent_node.board.san(child_node.move)
            move_eval = f" {{{child_node.evaluation:+.0f}}}" if child_node.evaluation is not None else ""
            
            if starting_turn:
                var_start = f"({move_number}. {move_san}{move_eval}"
                next_turn = False
                next_move_num = move_number
            else:
                var_start = f"({move_number}... {move_san}{move_eval}"
                next_turn = True
                next_move_num = move_number + 1
            
            # Add continuation if children exist (with depth limit)
            if child_node.children and max_depth > 1:
                # Get the main continuation (first child)
                main_child = child_node.children[0]
                continuation = self._build_complete_tree_safe(child_node, next_turn, next_move_num, max_depth - 1)
                if continuation:
                    return var_start + " " + continuation + ")"
            
            return var_start + ")"
                
        except Exception as e:
            print(f"Error building variation: {e}", file=sys.stderr)
            return ""

    def tree_to_dict(self, node: TreeNode) -> Dict[str, Any]:
        """
        Convert tree to dictionary format for JSON output.
        
        Args:
            node: Root node of the tree
            
        Returns:
            Dictionary representation of the tree
        """
        result = {
            'fen': node.board.fen(),
            'move': str(node.move) if node.move else None,
            'evaluation': node.evaluation,
            'depth': node.depth,
            'is_checkmate': node.board.is_checkmate(),
            'is_stalemate': node.board.is_stalemate(),
            'is_game_over': node.board.is_game_over(),
            'children': []
        }
        
        for child in node.children:
            result['children'].append(self.tree_to_dict(child))
        
        return result
    
    def print_tree(self, node: TreeNode, indent: int = 0):
        """
        Print tree in a readable format.
        
        Args:
            node: Node to print
            indent: Current indentation level
        """
        prefix = "  " * indent
        
        if node.move:
            move_str = str(node.move)
            eval_str = f" (eval: {node.evaluation})" if node.evaluation is not None else ""
            print(f"{prefix}{move_str}{eval_str}")
        else:
            print(f"{prefix}Starting position (FEN: {node.board.fen()})")
        
        # Print game status
        if node.board.is_checkmate():
            print(f"{prefix}  --> CHECKMATE")
        elif node.board.is_stalemate():
            print(f"{prefix}  --> STALEMATE")
        elif node.board.is_insufficient_material():
            print(f"{prefix}  --> INSUFFICIENT MATERIAL")
        
        # Print children
        for child in node.children:
            self.print_tree(child, indent + 1)
    
    def print_summary(self):
        """Print analysis summary statistics."""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            start_datetime = datetime.fromtimestamp(self.start_time)
            end_datetime = datetime.fromtimestamp(self.end_time)
            
            print("\n" + "=" * 60)
            print("ANALYSIS SUMMARY")
            print("=" * 60)
            print(f"Start time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"End time: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            print(f"Positions analyzed: {self.total_positions_analyzed}")
            print(f"Total moves used: {self.total_moves_after_filtering} (after filtering)")
            if self.total_positions_analyzed > 0:
                avg_moves = self.total_moves_after_filtering / self.total_positions_analyzed
                print(f"Average moves per position: {avg_moves:.1f}")
                print(f"Average time per position: {duration/self.total_positions_analyzed:.2f} seconds")
            print("=" * 60)
    
    def close(self):
        """Close the Stockfish analyzer."""
        self.analyzer.close()


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate chess game trees using Stockfish engine analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chess_tree_generator.py --fen "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" --stockfish-path ./stockfish
  python chess_tree_generator.py --fen "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4" --depth 5 --time 2.0
        """
    )
    
    # Input group - either FEN or PGN file (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--fen',
        help='FEN string representing the starting position'
    )
    input_group.add_argument(
        '--pgn-file',
        help='PGN file to analyze from the last position'
    )
    
    parser.add_argument(
        '--stockfish-path',
        required=True,
        help='Path to Stockfish engine executable'
    )
    
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='Maximum depth in half-moves (default: 3)'
    )
    
    parser.add_argument(
        '--time',
        type=float,
        default=60.0,
        help='Analysis time per position in seconds (default: 60.0)'
    )
    
    parser.add_argument(
        '--threshold',
        type=int,
        default=30,
        help='Centipawn threshold for move filtering (applies to both sides if --white-threshold/--black-threshold not specified)'
    )
    
    parser.add_argument(
        '--white-threshold',
        type=int,
        help='Centipawn threshold for White move filtering (overrides --threshold for White)'
    )
    
    parser.add_argument(
        '--black-threshold', 
        type=int,
        help='Centipawn threshold for Black move filtering (overrides --threshold for Black)'
    )
    
    parser.add_argument(
        '--num-moves',
        type=int,
        default=3,
        help='Number of top moves to analyze per position (applies to both sides if --white-moves/--black-moves not specified)'
    )
    
    parser.add_argument(
        '--white-moves',
        type=int,
        help='Number of top moves to analyze for White positions (overrides --num-moves for White)'
    )
    
    parser.add_argument(
        '--black-moves',
        type=int, 
        help='Number of top moves to analyze for Black positions (overrides --num-moves for Black)'
    )
    
    parser.add_argument(
        '--hash-memory',
        type=int,
        default=8192,
        help='Memory allocation for Stockfish hash table in MB (default: 8192)'
    )
    
    parser.add_argument(
        '--output',
        choices=['tree', 'json', 'pgn'],
        default='tree',
        help='Output format: tree (human-readable), json, or pgn (default: tree)'
    )
    
    parser.add_argument(
        '--output-file',
        help='Output file path (if not specified, prints to stdout)'
    )
    
    args = parser.parse_args()
    
    # Validate Stockfish path
    if not os.path.isfile(args.stockfish_path):
        print(f"Error: Stockfish executable not found at: {args.stockfish_path}", file=sys.stderr)
        sys.exit(1)
    
    # Validate PGN file if provided
    if args.pgn_file and not os.path.isfile(args.pgn_file):
        print(f"Error: PGN file not found at: {args.pgn_file}", file=sys.stderr)
        sys.exit(1)
    
    generator = None
    diagnostics_buffer = io.StringIO()
    
    try:
        # Determine White/Black specific parameters
        white_threshold = args.white_threshold if args.white_threshold is not None else args.threshold
        black_threshold = args.black_threshold if args.black_threshold is not None else args.threshold
        white_moves = args.white_moves if args.white_moves is not None else args.num_moves
        black_moves = args.black_moves if args.black_moves is not None else args.num_moves
        
        # Initialize generator
        generator = ChessTreeGenerator(
            stockfish_path=args.stockfish_path,
            max_depth=args.depth,
            analysis_time=args.time,
            white_threshold=white_threshold,
            black_threshold=black_threshold,
            white_moves=white_moves,
            black_moves=black_moves,
            hash_memory_mb=args.hash_memory
        )
        
        # Show initial progress to console
        if args.pgn_file:
            print(f"🔍 Starting analysis of PGN file: {args.pgn_file}")
            if white_threshold == black_threshold and white_moves == black_moves:
                print(f"⚙️  Configuration: depth={args.depth}, time={args.time}s, threshold={white_threshold}cp, moves={white_moves}")
            else:
                print(f"⚙️  Configuration: depth={args.depth}, time={args.time}s")
                print(f"   White: threshold={white_threshold}cp, moves={white_moves}")
                print(f"   Black: threshold={black_threshold}cp, moves={black_moves}")
        else:
            print(f"🔍 Starting analysis from FEN position")
            print(f"⚙️  Configuration: depth={args.depth}, time={args.time}s, threshold={args.threshold}cp, moves={args.num_moves}")
        
        # Start capturing console output for diagnostics
        with redirect_stdout(diagnostics_buffer):
            # Generate tree from either FEN or PGN
            existing_game = None
            if args.pgn_file:
                print(f"Analyzing PGN file: {args.pgn_file}")
                print(f"Max depth: {args.depth} half-moves")
                print(f"Analysis time: {args.time} seconds per position")
                print(f"Centipawn threshold: {args.threshold}")
                print(f"Number of moves per position: {args.num_moves}")
                print("=" * 50)
                root, existing_game = generator.generate_tree_from_pgn(args.pgn_file)
            else:
                print(f"Generating game tree from FEN: {args.fen}")
                print(f"Max depth: {args.depth} half-moves")
                print(f"Analysis time: {args.time} seconds per position")
                print(f"Centipawn threshold: {args.threshold}")
                print(f"Number of moves per position: {args.num_moves}")
                print("=" * 50)
                root = generator.generate_tree(args.fen)
            
            # Print summary statistics to diagnostics
            generator.print_summary()
        
        # Output results
        if args.output == 'json':
            tree_dict = generator.tree_to_dict(root)
            json_output = json.dumps(tree_dict, indent=2)
            
            if args.output_file:
                # Add timestamp to filename
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                base_name, ext = os.path.splitext(args.output_file)
                timestamped_filename = f"{base_name}_{timestamp}{ext}"
                
                with open(timestamped_filename, 'w') as f:
                    f.write(json_output)
                print(f"Tree saved to: {timestamped_filename}")
            else:
                print(json_output)
        elif args.output == 'pgn':
            pgn_output = generator.tree_to_pgn(root, existing_game=existing_game)
            
            if args.output_file:
                # Add timestamp to filename
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                base_name, ext = os.path.splitext(args.output_file)
                timestamped_filename = f"{base_name}_{timestamp}{ext}"
                
                with open(timestamped_filename, 'w') as f:
                    f.write(pgn_output)
                print(f"PGN saved to: {timestamped_filename}")
            else:
                print(pgn_output)
        else:  # tree format
            if args.output_file:
                # Add timestamp to filename
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                base_name, ext = os.path.splitext(args.output_file)
                timestamped_filename = f"{base_name}_{timestamp}{ext}"
                
                with open(timestamped_filename, 'w') as f:
                    # Redirect stdout to file
                    original_stdout = sys.stdout
                    sys.stdout = f
                    generator.print_tree(root)
                    sys.stdout = original_stdout
                print(f"Tree saved to: {timestamped_filename}")
            else:
                generator.print_tree(root)
        
        # Clear the progress line and show completion
        print(f"\r✅ Analysis complete! Processed {generator.total_positions_analyzed} positions")
        
        # Write diagnostics to file including summary
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        diagnostics_filename = f"diagnostics_{timestamp}.txt"
        
        # Write diagnostics and summary to file
        with open(diagnostics_filename, 'w') as f:
            # Write captured diagnostics
            f.write(diagnostics_buffer.getvalue())
            
            # Write summary directly to file
            if generator.start_time and generator.end_time:
                duration = generator.end_time - generator.start_time
                start_datetime = datetime.fromtimestamp(generator.start_time)
                end_datetime = datetime.fromtimestamp(generator.end_time)
                
                f.write("\n" + "="*60 + "\n")
                f.write("FINAL SUMMARY\n")
                f.write("="*60 + "\n")
                f.write(f"Start time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"End time: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)\n")
                f.write(f"Positions analyzed: {generator.total_positions_analyzed}\n")
                f.write(f"Total moves used: {generator.total_moves_after_filtering} (after filtering)\n")
                if generator.total_positions_analyzed > 0:
                    avg_moves = generator.total_moves_after_filtering / generator.total_positions_analyzed
                    f.write(f"Average moves per position: {avg_moves:.1f}\n")
                    f.write(f"Average time per position: {duration/generator.total_positions_analyzed:.2f} seconds\n")
                f.write("="*60 + "\n")
            else:
                f.write("\n" + "="*60 + "\n")
                f.write("FINAL SUMMARY\n")
                f.write("="*60 + "\n")
                f.write("Analysis timing information not available\n")
                f.write("="*60 + "\n")
        
        print(f"Diagnostics saved to: {diagnostics_filename}")
        
        # Also print summary to console for immediate feedback
        generator.print_summary()
        
    except ValueError as e:
        print(f"Input Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Engine Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Always close the Stockfish engine to free resources
        if generator:
            generator.close()
            print("Stockfish engine closed.")


if __name__ == "__main__":
    main()
