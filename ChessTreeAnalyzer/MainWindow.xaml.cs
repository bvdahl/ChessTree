using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;
using ChessTreeAnalyzer.Models;
using ChessTreeAnalyzer.Services;
using ChessTreeAnalyzer.Dialogs;

namespace ChessTreeAnalyzer
{
    public partial class MainWindow : Window
    {
        private ChessAnalysisService _analysisService;
        private StockfishService _stockfishService;
        private ChessGameModel _currentGame;
        private AnalysisSettings _currentSettings;

        public MainWindow()
        {
            InitializeComponent();
            InitializeServices();
            StatusText.Text = "Chess Tree Analyzer Ready";
            
            // Initialize with a starting position
            var startingBoard = new SimpleChessBoard();
            ChessBoard.SetPosition(startingBoard);
            _currentGame = ChessGameModel.LoadFromFEN(startingBoard.FEN);
            
            OutputTextBox.Text = "Welcome to Chess Tree Analyzer!\n\nFeatures:\n" +
                                  "• Load PGN files for analysis\n" +
                                  "• Set up positions from FEN notation\n" +
                                  "• Generate analysis trees with Stockfish\n" +
                                  "• Professional Windows interface\n\n" +
                                  "Ready for analysis! Configure settings and start analysis.";
        }

        private void InitializeServices()
        {
            _stockfishService = new StockfishService();
            _analysisService = new ChessAnalysisService(_stockfishService);
            _currentSettings = SettingsService.LoadSettings(); // Load persistent settings
            
            // Subscribe to analysis events
            _analysisService.AnalysisProgressChanged += OnAnalysisProgressChanged;
            _analysisService.AnalysisCompleted += OnAnalysisCompleted;
            _analysisService.AnalysisOutputReceived += OnAnalysisOutputReceived;
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
                    _currentGame = ChessGameModel.LoadFromPGN(dialog.FileName);
                    ChessBoard.SetPosition(_currentGame.GetCurrentPosition()); // Use current position after moves
                    StatusText.Text = $"Loaded PGN: {System.IO.Path.GetFileName(dialog.FileName)}";
                    OutputTextBox.Text = $"PGN file loaded successfully:\n{_currentGame.GameInfo}\n\nCurrent position loaded. Ready for analysis.";
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
                    _currentGame = ChessGameModel.LoadFromFEN(fen);
                    ChessBoard.SetPosition(_currentGame.InitialPosition);
                    StatusText.Text = "FEN position loaded";
                    OutputTextBox.Text = $"FEN position loaded:\n{fen}\n\nPosition ready for analysis.";
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error loading FEN: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void SaveAnalysis_Click(object sender, RoutedEventArgs e)
        {
            if (_currentGame?.AnalysisTree == null)
            {
                MessageBox.Show("No analysis to save. Please run an analysis first.", "No Analysis", 
                              MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            var dialog = new SaveFileDialog
            {
                Title = "Save Analysis",
                Filter = "PGN Files (*.pgn)|*.pgn|JSON Files (*.json)|*.json|All Files (*.*)|*.*",
                DefaultExt = "pgn"
            };

            if (dialog.ShowDialog() == true)
            {
                try
                {
                    var extension = System.IO.Path.GetExtension(dialog.FileName).ToLower();
                    if (extension == ".json")
                        _currentGame.SaveAnalysisAsJSON(dialog.FileName);
                    else
                        _currentGame.SaveAnalysisAsPGN(dialog.FileName);

                    StatusText.Text = $"Analysis saved: {System.IO.Path.GetFileName(dialog.FileName)}";
                    MessageBox.Show("Analysis saved successfully!", "Save Complete", 
                                  MessageBoxButton.OK, MessageBoxImage.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error saving analysis: {ex.Message}", "Save Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void SaveAsAnalysis_Click(object sender, RoutedEventArgs e)
        {
            SaveAnalysis_Click(sender, e); // Same as Save Analysis
        }

        private void Exit_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }

        private async void StartAnalysis_Click(object sender, RoutedEventArgs e)
        {
            if (_analysisService.IsAnalyzing)
            {
                MessageBox.Show("Analysis is already in progress.", "Analysis Running", 
                              MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            if (_currentGame == null)
            {
                MessageBox.Show("Please load a position or PGN file first.", "No Position", 
                              MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            try
            {
                // Update UI for analysis start
                StartAnalysisButton.IsEnabled = false;
                StopAnalysisButton.IsEnabled = true;
                AnalysisProgressBar.Visibility = Visibility.Visible;
                AnalysisProgressBar.Value = 0;
                
                // Get analysis parameters from UI
                if (int.TryParse(DepthTextBox.Text, out int depth))
                    _currentSettings.MaxDepth = depth;
                if (double.TryParse(TimeTextBox.Text, out double timeSeconds))
                    _currentSettings.TimePerPosition = TimeSpan.FromSeconds(timeSeconds);

                StatusText.Text = "Starting analysis...";
                OutputTextBox.Text = "Starting chess analysis...\n";

                // Start analysis
                await _analysisService.StartAnalysisAsync(_currentGame, _currentSettings);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error starting analysis: {ex.Message}", "Analysis Error", 
                              MessageBoxButton.OK, MessageBoxImage.Error);
                ResetAnalysisUI();
            }
        }

        private void StopAnalysis_Click(object sender, RoutedEventArgs e)
        {
            if (_analysisService.IsAnalyzing)
            {
                _analysisService.StopAnalysis();
                StatusText.Text = "Stopping analysis...";
            }
        }

        private void AnalysisSettings_Click(object sender, RoutedEventArgs e)
        {
            var settingsDialog = new AnalysisSettingsDialog(_currentSettings);
            if (settingsDialog.ShowDialog() == true)
            {
                _currentSettings = settingsDialog.Settings;
                SettingsService.SaveSettings(_currentSettings); // Persist settings
                StatusText.Text = "Analysis settings updated and saved";
                
                // Update UI controls to reflect new settings
                DepthTextBox.Text = _currentSettings.MaxDepth.ToString();
                TimeTextBox.Text = _currentSettings.TimePerPosition.TotalSeconds.ToString("F1");
            }
        }

        private void EngineSettings_Click(object sender, RoutedEventArgs e)
        {
            AnalysisSettings_Click(sender, e); // Same as Analysis Settings
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
            var userGuide = "Chess Tree Analyzer - User Guide\n\n" +
                           "1. Load Position:\n" +
                           "   • File → Open PGN to load a chess game\n" +
                           "   • File → Load FEN to set up a specific position\n\n" +
                           "2. Configure Analysis:\n" +
                           "   • Analysis → Settings to configure engine parameters\n" +
                           "   • Set analysis depth and time per position\n" +
                           "   • Configure move filtering thresholds\n\n" +
                           "3. Run Analysis:\n" +
                           "   • Click 'Start Analysis' or press F5\n" +
                           "   • Monitor progress in the output panel\n" +
                           "   • View results in the analysis tree\n\n" +
                           "4. Save Results:\n" +
                           "   • File → Save Analysis to export as PGN or JSON\n" +
                           "   • Analysis includes all variations and evaluations\n\n" +
                           "Requirements:\n" +
                           "• Stockfish chess engine executable\n" +
                           "• Configure engine path in settings";

            MessageBox.Show(userGuide, "User Guide", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        // Analysis event handlers
        private void OnAnalysisProgressChanged(object sender, AnalysisProgressEventArgs e)
        {
            Dispatcher.Invoke(() =>
            {
                AnalysisProgressBar.Value = e.ProgressPercentage;
                ProgressText.Text = $"{e.PositionsAnalyzed}/{e.TotalPositions} positions";
                StatusText.Text = $"Analyzing... {e.ProgressPercentage}%";
            });
        }

        private void OnAnalysisCompleted(object sender, AnalysisCompletedEventArgs e)
        {
            Dispatcher.Invoke(() =>
            {
                ResetAnalysisUI();
                
                if (e.Success)
                {
                    StatusText.Text = $"Analysis completed! {e.PositionsAnalyzed} positions analyzed";
                    PopulateAnalysisTree(e.AnalysisResult);
                }
                else
                {
                    StatusText.Text = "Analysis failed";
                    MessageBox.Show($"Analysis failed: {e.ErrorMessage}", "Analysis Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            });
        }

        private void OnAnalysisOutputReceived(object sender, string output)
        {
            Dispatcher.Invoke(() =>
            {
                OutputTextBox.Text += output + "\n";
                
                // Auto-scroll to bottom
                OutputTextBox.ScrollToEnd();
            });
        }

        private void ResetAnalysisUI()
        {
            StartAnalysisButton.IsEnabled = true;
            StopAnalysisButton.IsEnabled = false;
            AnalysisProgressBar.Visibility = Visibility.Collapsed;
            AnalysisProgressBar.Value = 0;
            ProgressText.Text = "";
        }

        private void PopulateAnalysisTree(AnalysisTreeNode rootNode)
        {
            AnalysisTreeView.Items.Clear();
            
            if (rootNode != null)
            {
                var rootItem = CreateTreeViewItem(rootNode, "Analysis Root");
                AnalysisTreeView.Items.Add(rootItem);
                rootItem.IsExpanded = true;
            }
        }

        private TreeViewItem CreateTreeViewItem(AnalysisTreeNode node, string displayText)
        {
            var item = new TreeViewItem
            {
                Header = displayText,
                Tag = node
            };

            foreach (var child in node.Children)
            {
                var moveText = child.Move?.SAN ?? "Unknown";
                var evalText = child.IsMateScore ? $"Mate {child.MateInMoves}" : $"{child.Evaluation:+0;-#}";
                var childDisplayText = $"{moveText} ({evalText})";
                
                var childItem = CreateTreeViewItem(child, childDisplayText);
                item.Items.Add(childItem);
            }

            return item;
        }

        // New methods to address the 6 issues
        private void CopyOutput_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Clipboard.SetText(OutputTextBox.Text);
                StatusText.Text = "Output copied to clipboard";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error copying to clipboard: {ex.Message}", "Copy Error", 
                              MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void SaveOutput_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new SaveFileDialog
            {
                Title = "Save Analysis Output",
                Filter = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*",
                DefaultExt = "txt",
                FileName = $"chess_analysis_output_{DateTime.Now:yyyyMMdd_HHmmss}.txt"
            };

            if (dialog.ShowDialog() == true)
            {
                try
                {
                    File.WriteAllText(dialog.FileName, OutputTextBox.Text);
                    StatusText.Text = $"Output saved: {Path.GetFileName(dialog.FileName)}";
                    MessageBox.Show("Analysis output saved successfully!", "Save Complete", 
                                  MessageBoxButton.OK, MessageBoxImage.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error saving output: {ex.Message}", "Save Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        protected override void OnClosed(EventArgs e)
        {
            // Save settings on exit  
            SettingsService.SaveSettings(_currentSettings);
            _stockfishService?.Dispose();
            base.OnClosed(e);
        }
    }
}