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
from typing import List, Dict, Any
import chess
import chess.engine
import chess.pgn
import io
from stockfish_analyzer import StockfishAnalyzer
from tree_node import TreeNode


class ChessTreeGenerator:
    """Main class for generating chess game trees."""
    
    def __init__(self, stockfish_path: str, max_depth: int = 3, 
                 analysis_time: float = 60.0, centipawn_threshold: int = 30, num_moves: int = 3, hash_memory_mb: int = 8192):
        """
        Initialize the chess tree generator.
        
        Args:
            stockfish_path: Path to Stockfish engine executable
            max_depth: Maximum depth in half-moves (default: 3)
            analysis_time: Time to analyze each position in seconds (default: 1.0)
            centipawn_threshold: Centipawn threshold for move filtering (default: 30)
            num_moves: Number of top moves to analyze per position (default: 3)
            hash_memory_mb: Memory allocation for hash table in MB (default: 8192)
        """
        self.stockfish_path = stockfish_path
        self.max_depth = max_depth
        self.analysis_time = analysis_time
        self.centipawn_threshold = centipawn_threshold
        self.num_moves = num_moves
        self.hash_memory_mb = hash_memory_mb
        self.analyzer = StockfishAnalyzer(stockfish_path, analysis_time, num_moves, hash_memory_mb)
        
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
        self._build_tree_breadth_first(root)
        
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
        self._build_tree_breadth_first(root)
        
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
                filtered_moves = self._filter_moves(analysis_results)
                print(f"After filtering: {len(filtered_moves)} moves")
                
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
    
    def _filter_moves(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter moves based on evaluation difference threshold.
        
        Args:
            analysis_results: List of move analysis results from Stockfish
            
        Returns:
            List of filtered moves (maximum 3, within centipawn threshold)
        """
        if not analysis_results:
            return []
        
        # Sort by evaluation (best first)
        sorted_moves = sorted(analysis_results, key=lambda x: x['evaluation'], reverse=True)
        
        # Take best move
        filtered_moves = [sorted_moves[0]]
        best_eval = sorted_moves[0]['evaluation']
        
        # Add additional moves up to num_moves if within threshold
        for move_data in sorted_moves[1:self.num_moves]:
            eval_diff = best_eval - move_data['evaluation']
            if eval_diff <= self.centipawn_threshold:
                filtered_moves.append(move_data)
            else:
                break  # No need to check further moves
        
        return filtered_moves
    
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
        Convert tree to proper PGN format matching the manual example structure.
        Shows exactly 3 moves at each level, explored 3 levels deep.
        """
        if not node.children:
            return ""
        
        result = []
        
        # Build the complete tree structure
        tree_text = self._build_complete_tree(node, starting_turn, move_number)
        
        return tree_text
    
    def _build_complete_tree(self, node: TreeNode, starting_turn: bool, move_number: int) -> str:
        """Build the complete tree structure exactly like the manual example."""
        if not node.children:
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
        
        # Step 2: Build complete variations for alternative first moves (like manual example)
        for alt_child in node.children[1:]:  # All alternatives to main move
            alt_variation = self._build_manual_style_variation(node, alt_child, starting_turn, move_number)
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
            
            # Step 4: Build variations for alternative responses (like manual example)
            for alt_response in main_child.children[1:]:  # All alternatives to main response
                alt_resp_var = self._build_manual_style_variation(main_child, alt_response, response_turn, response_move_num)
                if alt_resp_var:
                    parts.append(alt_resp_var)
            
            # Step 5: Final moves (best continuation plus alternatives)
            if main_response.children:
                final_main = main_response.children[0]
                final_san = main_response.board.san(final_main.move)
                final_eval = f" {{{final_main.evaluation:+.0f}}}" if final_main.evaluation is not None else ""
                
                if final_turn:
                    final_move = f"{final_move_num}. {final_san}{final_eval}"
                else:
                    final_move = f"{final_move_num}... {final_san}{final_eval}"
                
                parts.append(final_move)
                
                # Add alternative final moves
                for alt_final in main_response.children[1:]:
                    alt_final_var = self._build_simple_variation(main_response, alt_final, final_turn, final_move_num)
                    if alt_final_var:
                        parts.append(alt_final_var)
        
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
                            alt_cont_var = self._build_simple_variation(alt_resp, alt_cont, final_turn, final_move_num)
                            if alt_cont_var:
                                cont_parts.append(alt_cont_var)
                        
                        sub_var = sub_var_start + " " + " ".join(cont_parts) + ")"
                    else:
                        sub_var = sub_var_start + ")"
                    
                    var_parts.append(sub_var)
                
                # Main continuation
                if main_resp.children:
                    final_main = main_resp.children[0]
                    final_san = main_resp.board.san(final_main.move)
                    final_eval = f" {{{final_main.evaluation:+.0f}}}" if final_main.evaluation is not None else ""
                    
                    if final_turn:
                        final_text = f"{final_move_num}. {final_san}{final_eval}"
                    else:
                        final_text = f"{final_move_num}... {final_san}{final_eval}"
                    
                    var_parts.append(final_text)
                    
                    # Add alternative final moves
                    for alt_final in main_resp.children[1:]:
                        alt_final_var = self._build_simple_variation(main_resp, alt_final, final_turn, final_move_num)
                        if alt_final_var:
                            var_parts.append(alt_final_var)
            
            return " ".join(var_parts) + ")"
            
        except Exception as e:
            print(f"Error building manual style variation: {e}", file=sys.stderr)
            return ""
    
    def _build_full_variation(self, parent_node: TreeNode, child_node: TreeNode, 
                             starting_turn: bool, move_number: int, depth_remaining: int) -> str:
        """Build a complete variation with all 3 levels like in the manual example."""
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
            if child_node.children and depth_remaining > 1:
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
                
                # Add final moves for main response (continuation of main line)
                if main_resp.children and depth_remaining > 2:
                    final_main = main_resp.children[0]
                    final_san = main_resp.board.san(final_main.move)
                    final_eval = f" {{{final_main.evaluation:+.0f}}}" if final_main.evaluation is not None else ""
                    
                    if final_turn:
                        final_text = f"{final_move_num}. {final_san}{final_eval}"
                    else:
                        final_text = f"{final_move_num}... {final_san}{final_eval}"
                    
                    var_parts.append(final_text)
                    
                    # Add alternative final moves
                    for alt_final in main_resp.children[1:]:
                        alt_final_var = self._build_simple_variation(main_resp, alt_final, final_turn, final_move_num)
                        if alt_final_var:
                            var_parts.append(alt_final_var)
            
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
                    alt_var = self._build_simple_variation(main_cont, alt_cont, final_turn, final_move_num)
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
                
                # Add final move if available
                if main_resp.children and depth_remaining > 2:
                    final_move = main_resp.children[0]
                    final_san = main_resp.board.san(final_move.move)
                    final_eval = f" {{{final_move.evaluation:+.0f}}}" if final_move.evaluation is not None else ""
                    
                    if final_turn:
                        final_text = f"{final_move_num}. {final_san}{final_eval}"
                    else:
                        final_text = f"{final_move_num}... {final_san}{final_eval}"
                    
                    continuation_parts.append(final_text)
                
                # Add sub-variations (alternatives at deeper levels)
                if depth_remaining > 2 and main_resp.children:
                    for sub_alt in main_resp.children[1:]:  # All available sub-variations
                        sub_var = self._build_simple_variation(main_resp, sub_alt, final_turn, final_move_num)
                        if sub_var:
                            continuation_parts.append(sub_var)
            
            # Combine all parts
            if continuation_parts:
                return var_start + " " + " ".join(continuation_parts) + ")"
            else:
                return var_start + ")"
                
        except Exception as e:
            print(f"Error building variation branch: {e}", file=sys.stderr)
            return ""
    
    def _build_simple_variation(self, parent_node: TreeNode, child_node: TreeNode, 
                               starting_turn: bool, move_number: int) -> str:
        """Build a simple variation without deep nesting."""
        try:
            move_san = parent_node.board.san(child_node.move)
            move_eval = f" {{{child_node.evaluation:+.0f}}}" if child_node.evaluation is not None else ""
            
            if starting_turn:
                return f"({move_number}. {move_san}{move_eval})"
            else:
                return f"({move_number}... {move_san}{move_eval})"
                
        except Exception as e:
            print(f"Error building simple variation: {e}", file=sys.stderr)
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
        help='Centipawn threshold for move filtering (default: 30)'
    )
    
    parser.add_argument(
        '--num-moves',
        type=int,
        default=3,
        help='Number of top moves to analyze per position (default: 3)'
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
    try:
        # Initialize generator
        generator = ChessTreeGenerator(
            stockfish_path=args.stockfish_path,
            max_depth=args.depth,
            analysis_time=args.time,
            centipawn_threshold=args.threshold,
            num_moves=args.num_moves,
            hash_memory_mb=args.hash_memory
        )
        
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
        
        # Output results
        if args.output == 'json':
            tree_dict = generator.tree_to_dict(root)
            json_output = json.dumps(tree_dict, indent=2)
            
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    f.write(json_output)
                print(f"Tree saved to: {args.output_file}")
            else:
                print(json_output)
        elif args.output == 'pgn':
            pgn_output = generator.tree_to_pgn(root, existing_game=existing_game)
            
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    f.write(pgn_output)
                print(f"PGN saved to: {args.output_file}")
            else:
                print(pgn_output)
        else:  # tree format
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    # Redirect stdout to file
                    original_stdout = sys.stdout
                    sys.stdout = f
                    generator.print_tree(root)
                    sys.stdout = original_stdout
                print(f"Tree saved to: {args.output_file}")
            else:
                generator.print_tree(root)
        
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
