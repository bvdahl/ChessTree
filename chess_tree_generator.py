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
                 analysis_time: float = 60.0, centipawn_threshold: int = 30):
        """
        Initialize the chess tree generator.
        
        Args:
            stockfish_path: Path to Stockfish engine executable
            max_depth: Maximum depth in half-moves (default: 3)
            analysis_time: Time to analyze each position in seconds (default: 1.0)
            centipawn_threshold: Centipawn threshold for move filtering (default: 30)
        """
        self.stockfish_path = stockfish_path
        self.max_depth = max_depth
        self.analysis_time = analysis_time
        self.centipawn_threshold = centipawn_threshold
        self.analyzer = StockfishAnalyzer(stockfish_path, analysis_time)
        
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
        
        # Add second and third moves if within threshold
        for move_data in sorted_moves[1:3]:
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
        Convert tree to proper PGN format showing complete analysis with all variations.
        """
        if not node.children:
            return ""
        
        result = []
        
        # Start with the best line (3 half-moves)
        main_line = self._build_main_line(node, starting_turn, move_number, 3)
        result.extend(main_line)
        
        # Add variations at each level
        variations = self._build_all_variations(node, starting_turn, move_number, 3)
        result.extend(variations)
        
        return " ".join(result)
    
    def _build_main_line(self, node: TreeNode, starting_turn: bool, move_number: int, depth: int) -> List[str]:
        """Build the main line (best moves) for the specified depth."""
        line = []
        current_node = node
        current_turn = starting_turn
        current_move_num = move_number
        
        for level in range(depth):
            if not current_node.children:
                break
                
            best_child = current_node.children[0]
            try:
                move_san = current_node.board.san(best_child.move)
                eval_str = f" {{{best_child.evaluation:+.0f}}}" if best_child.evaluation is not None else ""
                
                if current_turn:  # White to move
                    move_text = f"{current_move_num}. {move_san}{eval_str}"
                    current_turn = False
                else:  # Black to move  
                    move_text = f"{current_move_num}... {move_san}{eval_str}"
                    current_turn = True
                    current_move_num += 1
                
                line.append(move_text)
                current_node = best_child
                
            except Exception as e:
                print(f"Error building main line: {e}", file=sys.stderr)
                break
        
        return line
    
    def _build_all_variations(self, node: TreeNode, starting_turn: bool, move_number: int, max_depth: int) -> List[str]:
        """Build all variations at each level."""
        variations = []
        
        # Level 1 variations (alternatives to first move)
        for alt_child in node.children[1:]:  # All alternatives to main move
            try:
                alt_san = node.board.san(alt_child.move)
                alt_eval = f" {{{alt_child.evaluation:+.0f}}}" if alt_child.evaluation is not None else ""
                
                if starting_turn:
                    var_text = f"({move_number}. {alt_san}{alt_eval}"
                else:
                    var_text = f"({move_number}... {alt_san}{alt_eval}"
                
                # Add deeper variations for this alternative if available
                if alt_child.children and max_depth > 1:
                    next_turn = not starting_turn
                    next_move_num = move_number + (0 if starting_turn else 1)
                    
                    deeper_vars = self._build_variation_continuation(alt_child, next_turn, next_move_num, max_depth - 1)
                    if deeper_vars:
                        var_text += " " + " ".join(deeper_vars)
                
                var_text += ")"
                variations.append(var_text)
                
            except Exception as e:
                print(f"Error building variation: {e}", file=sys.stderr)
                continue
        
        # Level 2 variations (if main line exists)
        if node.children and node.children[0].children:
            main_child = node.children[0]
            next_turn = not starting_turn
            next_move_num = move_number + (0 if starting_turn else 1)
            
            for resp_alt in main_child.children[1:]:  # Alternatives to main response
                try:
                    resp_san = main_child.board.san(resp_alt.move)
                    resp_eval = f" {{{resp_alt.evaluation:+.0f}}}" if resp_alt.evaluation is not None else ""
                    
                    if next_turn:
                        var_text = f"({next_move_num}. {resp_san}{resp_eval})"
                    else:
                        var_text = f"({next_move_num}... {resp_san}{resp_eval})"
                    
                    variations.append(var_text)
                    
                except Exception as e:
                    continue
        
        return variations
    
    def _build_variation_continuation(self, node: TreeNode, starting_turn: bool, move_number: int, depth: int) -> List[str]:
        """Build continuation moves for a variation."""
        if depth <= 0 or not node.children:
            return []
        
        continuation = []
        best_child = node.children[0]
        
        try:
            move_san = node.board.san(best_child.move)
            eval_str = f" {{{best_child.evaluation:+.0f}}}" if best_child.evaluation is not None else ""
            
            if starting_turn:
                move_text = f"{move_number}. {move_san}{eval_str}"
            else:
                move_text = f"{move_number}... {move_san}{eval_str}"
            
            continuation.append(move_text)
            
            # Continue recursively if more depth needed
            if depth > 1:
                next_turn = not starting_turn
                next_move_num = move_number + (0 if starting_turn else 1)
                deeper = self._build_variation_continuation(best_child, next_turn, next_move_num, depth - 1)
                continuation.extend(deeper)
                
        except Exception as e:
            print(f"Error in variation continuation: {e}", file=sys.stderr)
        
        return continuation

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
    
    try:
        # Initialize generator
        generator = ChessTreeGenerator(
            stockfish_path=args.stockfish_path,
            max_depth=args.depth,
            analysis_time=args.time,
            centipawn_threshold=args.threshold
        )
        
        # Generate tree from either FEN or PGN
        existing_game = None
        if args.pgn_file:
            print(f"Analyzing PGN file: {args.pgn_file}")
            print(f"Max depth: {args.depth} half-moves")
            print(f"Analysis time: {args.time} seconds per position")
            print(f"Centipawn threshold: {args.threshold}")
            print("=" * 50)
            root, existing_game = generator.generate_tree_from_pgn(args.pgn_file)
        else:
            print(f"Generating game tree from FEN: {args.fen}")
            print(f"Max depth: {args.depth} half-moves")
            print(f"Analysis time: {args.time} seconds per position")
            print(f"Centipawn threshold: {args.threshold}")
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
        
        # Close generator
        generator.close()
        
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


if __name__ == "__main__":
    main()
