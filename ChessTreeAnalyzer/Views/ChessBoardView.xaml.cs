using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Shapes;
using Chess;
using ChessTreeAnalyzer.Models;

namespace ChessTreeAnalyzer.Views
{
    public partial class ChessBoardView : UserControl
    {
        private readonly Dictionary<string, string> _pieceSymbols = new Dictionary<string, string>
        {
            { "wK", "♔" }, { "wQ", "♕" }, { "wR", "♖" }, { "wB", "♗" }, { "wN", "♘" }, { "wP", "♙" },
            { "bK", "♚" }, { "bQ", "♛" }, { "bR", "♜" }, { "bB", "♝" }, { "bN", "♞" }, { "bP", "♟" }
        };

        private ChessGameModel _currentGame;
        private ChessBoard _currentPosition;
        private bool _flipped = false;
        private readonly Border[,] _squares = new Border[8, 8];
        private readonly TextBlock[,] _pieces = new TextBlock[8, 8];

        public ChessBoardView()
        {
            InitializeComponent();
            InitializeBoard();
        }

        private void InitializeBoard()
        {
            // Create board squares
            for (int rank = 0; rank < 8; rank++)
            {
                for (int file = 0; file < 8; file++)
                {
                    var square = new Border
                    {
                        Background = GetSquareColor(rank, file),
                        BorderBrush = Brushes.Transparent,
                        BorderThickness = new Thickness(0)
                    };

                    var piece = new TextBlock
                    {
                        FontSize = 36,
                        FontFamily = new FontFamily("Segoe UI Symbol"),
                        HorizontalAlignment = HorizontalAlignment.Center,
                        VerticalAlignment = VerticalAlignment.Center,
                        Foreground = Brushes.Black
                    };

                    square.Child = piece;
                    
                    Grid.SetRow(square, rank);
                    Grid.SetColumn(square, file);
                    
                    BoardGrid.Children.Add(square);
                    
                    _squares[rank, file] = square;
                    _pieces[rank, file] = piece;
                }
            }

            // Set starting position
            SetPosition(new ChessBoard());
        }

        private Brush GetSquareColor(int rank, int file)
        {
            bool isLightSquare = (rank + file) % 2 == 0;
            return isLightSquare ? new SolidColorBrush(Color.FromRgb(240, 217, 181)) : 
                                   new SolidColorBrush(Color.FromRgb(181, 136, 99));
        }

        public void LoadGame(ChessGameModel game)
        {
            _currentGame = game;
            SetPosition(game.GetCurrentPosition());
        }

        public void SetPosition(ChessBoard position)
        {
            _currentPosition = position;
            UpdatePieces();
        }

        private void UpdatePieces()
        {
            // Clear all pieces
            for (int rank = 0; rank < 8; rank++)
            {
                for (int file = 0; file < 8; file++)
                {
                    _pieces[rank, file].Text = "";
                }
            }

            if (_currentPosition == null) return;

            // Place pieces on board
            for (int squareIndex = 0; squareIndex < 64; squareIndex++)
            {
                var piece = _currentPosition.GetPiece(squareIndex);
                if (piece != null)
                {
                    var (rank, file) = IndexToCoordinates(squareIndex);
                    var pieceKey = GetPieceKey(piece);
                    
                    if (_pieceSymbols.ContainsKey(pieceKey))
                    {
                        _pieces[rank, file].Text = _pieceSymbols[pieceKey];
                    }
                }
            }
        }

        private (int rank, int file) IndexToCoordinates(int squareIndex)
        {
            int rank = 7 - (squareIndex / 8); // Flip rank for display
            int file = squareIndex % 8;
            
            if (_flipped)
            {
                rank = 7 - rank;
                file = 7 - file;
            }
            
            return (rank, file);
        }

        private string GetPieceKey(Piece piece)
        {
            string color = piece.Color == PieceColor.White ? "w" : "b";
            string type = piece.Type switch
            {
                PieceType.King => "K",
                PieceType.Queen => "Q",
                PieceType.Rook => "R",
                PieceType.Bishop => "B",
                PieceType.Knight => "N",
                PieceType.Pawn => "P",
                _ => ""
            };
            return color + type;
        }

        public void FlipBoard()
        {
            _flipped = !_flipped;
            UpdatePieces();
        }

        public void HighlightSquares(IEnumerable<int> squareIndices, Brush highlightBrush)
        {
            // Reset all square borders
            for (int rank = 0; rank < 8; rank++)
            {
                for (int file = 0; file < 8; file++)
                {
                    _squares[rank, file].BorderBrush = Brushes.Transparent;
                    _squares[rank, file].BorderThickness = new Thickness(0);
                }
            }

            // Highlight specified squares
            foreach (var squareIndex in squareIndices)
            {
                var (rank, file) = IndexToCoordinates(squareIndex);
                _squares[rank, file].BorderBrush = highlightBrush;
                _squares[rank, file].BorderThickness = new Thickness(3);
            }
        }

        public void ClearHighlights()
        {
            for (int rank = 0; rank < 8; rank++)
            {
                for (int file = 0; file < 8; file++)
                {
                    _squares[rank, file].BorderBrush = Brushes.Transparent;
                    _squares[rank, file].BorderThickness = new Thickness(0);
                }
            }
        }
    }
}