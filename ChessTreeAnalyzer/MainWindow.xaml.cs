using System;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;
using ChessTreeAnalyzer.Models;
using ChessTreeAnalyzer.Services;

namespace ChessTreeAnalyzer
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            StatusText.Text = "Chess Tree Analyzer Ready";
            
            // Initialize with a starting position
            var startingBoard = new SimpleChessBoard();
            ChessBoard.SetPosition(startingBoard);
            
            OutputTextBlock.Text = "Welcome to Chess Tree Analyzer!\n\nFeatures:\n" +
                                  "• Load PGN files for analysis\n" +
                                  "• Set up positions from FEN notation\n" +
                                  "• Generate analysis trees with Stockfish\n" +
                                  "• Professional Windows interface\n\n" +
                                  "Click 'Load FEN' or 'Open PGN' to get started.";
        }

        private void OpenPGN_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new OpenFileDialog
            {
                Filter = "PGN Files (*.pgn)|*.pgn|All Files (*.*)|*.*",
                Title = "Open PGN File"
            };

            if (dialog.ShowDialog() == true)
            {
                try
                {
                    var game = ChessGameModel.LoadFromPGN(dialog.FileName);
                    ChessBoard.SetPosition(game.InitialPosition);
                    StatusText.Text = $"Loaded PGN: {System.IO.Path.GetFileName(dialog.FileName)}";
                    OutputTextBlock.Text = $"PGN file loaded successfully:\n{game.GameInfo}\n\nReady for analysis.";
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error loading PGN file: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void LoadFEN_Click(object sender, RoutedEventArgs e)
        {
            string fen = Microsoft.VisualBasic.Interaction.InputBox(
                "Enter FEN notation:", 
                "Load FEN Position", 
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
            
            if (!string.IsNullOrWhiteSpace(fen))
            {
                try
                {
                    var game = ChessGameModel.LoadFromFEN(fen);
                    ChessBoard.SetPosition(game.InitialPosition);
                    StatusText.Text = "FEN position loaded";
                    OutputTextBlock.Text = $"FEN position loaded:\n{fen}\n\nPosition ready for analysis.";
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error loading FEN: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void SaveAnalysis_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Save analysis functionality will be implemented here.", "Save Analysis", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void SaveAsAnalysis_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Save as analysis functionality will be implemented here.", "Save As", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void Exit_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }

        private void StartAnalysis_Click(object sender, RoutedEventArgs e)
        {
            StatusText.Text = "Analysis functionality will be integrated with Stockfish engine";
            OutputTextBlock.Text = "Analysis engine integration:\n\n" +
                                  "This professional Windows interface is ready for Stockfish integration.\n" +
                                  "The analysis service framework is implemented and can be connected\n" +
                                  "to your proven Python chess analysis engine.\n\n" +
                                  "Features ready for integration:\n" +
                                  "• Real-time analysis progress updates\n" +
                                  "• Interactive analysis tree display\n" +
                                  "• Professional result formatting\n" +
                                  "• Export capabilities";
        }

        private void StopAnalysis_Click(object sender, RoutedEventArgs e)
        {
            StatusText.Text = "Analysis stopped";
        }

        private void AnalysisSettings_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Analysis settings dialog will be implemented here.", "Settings", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void EngineSettings_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Engine settings dialog will be implemented here.", "Engine Settings", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void ToggleBoard_Click(object sender, RoutedEventArgs e)
        {
            // Toggle board visibility
        }

        private void ToggleAnalysisTree_Click(object sender, RoutedEventArgs e)
        {
            // Toggle analysis tree visibility
        }

        private void ToggleOutput_Click(object sender, RoutedEventArgs e)
        {
            // Toggle output panel visibility  
        }

        private void ResetLayout_Click(object sender, RoutedEventArgs e)
        {
            StatusText.Text = "Layout reset";
        }

        private void About_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Chess Tree Analyzer v1.0\n\nProfessional chess analysis application\nBuilt with .NET 8 WPF\n\n© 2025 Chess Analysis Tools", 
                          "About Chess Tree Analyzer", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void UserGuide_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("User guide functionality will be implemented here.", "User Guide", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }


}