using System.Collections.Generic;
using Chess;

namespace ChessTreeAnalyzer.Models
{
    public class AnalysisTreeNode
    {
        public ChessBoard Position { get; set; }
        public Move? Move { get; set; }
        public int Evaluation { get; set; } // In centipawns
        public bool IsMateScore { get; set; }
        public int MateInMoves { get; set; }
        public int Depth { get; set; }
        public string Comment { get; set; } = "";
        public List<AnalysisTreeNode> Children { get; set; } = new List<AnalysisTreeNode>();
        public AnalysisTreeNode Parent { get; set; }

        public string DisplayText
        {
            get
            {
                if (Move == null)
                    return "Starting Position";

                var moveText = Position.ToSan(Move.Value);
                var evalText = IsMateScore ? $"Mate in {MateInMoves}" : $"{Evaluation:+0;-#}";
                
                return $"{moveText} ({evalText})";
            }
        }

        public string MoveNotation
        {
            get
            {
                if (Move == null || Position == null)
                    return "";

                return Position.ToSan(Move.Value);
            }
        }

        public bool IsLeaf => Children.Count == 0;

        public void AddChild(AnalysisTreeNode child)
        {
            child.Parent = this;
            Children.Add(child);
        }

        public void RemoveChild(AnalysisTreeNode child)
        {
            child.Parent = null;
            Children.Remove(child);
        }

        public List<AnalysisTreeNode> GetPathFromRoot()
        {
            var path = new List<AnalysisTreeNode>();
            var current = this;

            while (current != null)
            {
                path.Insert(0, current);
                current = current.Parent;
            }

            return path;
        }

        public int GetTotalNodeCount()
        {
            int count = 1; // Count this node
            foreach (var child in Children)
            {
                count += child.GetTotalNodeCount();
            }
            return count;
        }

        public AnalysisTreeNode FindNodeByMove(Move move, int depth)
        {
            if (Depth == depth && Move?.ToString() == move.ToString())
                return this;

            foreach (var child in Children)
            {
                var found = child.FindNodeByMove(move, depth);
                if (found != null)
                    return found;
            }

            return null;
        }
    }
}