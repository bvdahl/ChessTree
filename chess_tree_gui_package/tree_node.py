"""
Tree Node class for representing chess game tree nodes.
"""

from typing import List, Optional
import chess


class TreeNode:
    """
    Represents a node in the chess game tree.
    
    Each node contains:
    - Chess board position
    - Move that led to this position (None for root)
    - Evaluation score from engine
    - Depth level in the tree
    - List of child nodes
    """
    
    def __init__(self, board: chess.Board, move: Optional[chess.Move] = None,
                 evaluation: Optional[float] = None, depth: int = 0):
        """
        Initialize a tree node.
        
        Args:
            board: Chess board position
            move: Move that led to this position (None for root)
            evaluation: Engine evaluation score in centipawns
            depth: Depth level in the tree (0 for root)
        """
        self.board = board
        self.move = move
        self.evaluation = evaluation
        self.depth = depth
        self.children: List['TreeNode'] = []
    
    def add_child(self, child: 'TreeNode'):
        """
        Add a child node to this node.
        
        Args:
            child: Child node to add
        """
        self.children.append(child)
    
    def is_leaf(self) -> bool:
        """
        Check if this node is a leaf (has no children).
        
        Returns:
            True if node has no children, False otherwise
        """
        return len(self.children) == 0
    
    def get_moves_to_position(self) -> List[chess.Move]:
        """
        Get the sequence of moves from root to this position.
        Note: This would require parent references to implement fully.
        For now, this is a placeholder for potential future functionality.
        
        Returns:
            List of moves from root to this position
        """
        # This would need parent references to implement properly
        # For now, return empty list as placeholder
        return []
    
    def count_nodes(self) -> int:
        """
        Count total number of nodes in subtree rooted at this node.
        
        Returns:
            Total number of nodes including this node
        """
        count = 1  # Count this node
        for child in self.children:
            count += child.count_nodes()
        return count
    
    def get_leaf_nodes(self) -> List['TreeNode']:
        """
        Get all leaf nodes in the subtree rooted at this node.
        
        Returns:
            List of all leaf nodes
        """
        if self.is_leaf():
            return [self]
        
        leaves = []
        for child in self.children:
            leaves.extend(child.get_leaf_nodes())
        return leaves
    
    def __str__(self) -> str:
        """
        String representation of the node.
        
        Returns:
            String describing the node
        """
        if self.move:
            eval_str = f" (eval: {self.evaluation})" if self.evaluation is not None else ""
            return f"Move: {self.move}{eval_str} at depth {self.depth}"
        else:
            return f"Root position at depth {self.depth}"
    
    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.
        
        Returns:
            Detailed string representation
        """
        return (f"TreeNode(move={self.move}, evaluation={self.evaluation}, "
                f"depth={self.depth}, children={len(self.children)})")
