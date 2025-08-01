using System;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;
using ChessTreeAnalyzer.Services;
using ChessTreeAnalyzer.Models;

namespace ChessTreeAnalyzer
{
    public partial class MainWindow : Window
    {
        private readonly ChessAnalysisService _analysisService;
        private readonly StockfishService _stockfishService;
        private ChessGameModel _currentGame;

        public MainWindow()
        {
            InitializeComponent();
            
            // Initialize services
            _stockfishService = new StockfishService();
            _analysisService = new ChessAnalysisService(_stockfishService);
            
            // Subscribe to events
            _analysisService.AnalysisProgressChanged += OnAnalysisProgressChanged;
            _analysisService.AnalysisCompleted += OnAnalysisCompleted;
            _analysisService.AnalysisOutputReceived += OnAnalysisOutputReceived;
            
            // Set initial state
            UpdateUI();
        }

        #region Menu Event Handlers

        private void OpenPGN_Click(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog
            {
                Title = "Open PGN File",
                Filter = "PGN files (*.pgn)|*.pgn|All files (*.*)|*.*",
                FilterIndex = 1,
                RestoreDirectory = true
            };

            if (openFileDialog.ShowDialog() == true)
            {
                try
                {
                    _currentGame = ChessGameModel.LoadFromPGN(openFileDialog.FileName);
                    ChessBoard.LoadGame(_currentGame);
                    StatusText.Text = $"Loaded: {openFileDialog.FileName}";
                    UpdateUI();
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error loading PGN file: {ex.Message}", "Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void LoadFEN_Click(object sender, RoutedEventArgs e)
        {
            var fenDialog = new FENInputDialog();
            if (fenDialog.ShowDialog() == true)
            {
                try
                {
                    _currentGame = ChessGameModel.LoadFromFEN(fenDialog.FENString);
                    ChessBoard.LoadGame(_currentGame);
                    StatusText.Text = "Loaded FEN position";
                    UpdateUI();
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error loading FEN: {ex.Message}", "Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void SaveAnalysis_Click(object sender, RoutedEventArgs e)
        {
            if (_currentGame?.AnalysisTree == null)
            {
                MessageBox.Show("No analysis to save.", "Information", 
                              MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            var saveFileDialog = new SaveFileDialog
            {
                Title = "Save Analysis",
                Filter = "PGN files (*.pgn)|*.pgn|JSON files (*.json)|*.json|All files (*.*)|*.*",
                FilterIndex = 1,
                RestoreDirectory = true,
                FileName = $"analysis_{DateTime.Now:yyyyMMdd_HHmm}"
            };

            if (saveFileDialog.ShowDialog() == true)
            {
                try
                {
                    // Save analysis based on file extension
                    var extension = System.IO.Path.GetExtension(saveFileDialog.FileName).ToLower();
                    if (extension == ".json")
                    {
                        _currentGame.SaveAnalysisAsJSON(saveFileDialog.FileName);
                    }
                    else
                    {
                        _currentGame.SaveAnalysisAsPGN(saveFileDialog.FileName);
                    }
                    
                    StatusText.Text = $"Analysis saved: {saveFileDialog.FileName}";
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error saving analysis: {ex.Message}", "Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void SaveAsAnalysis_Click(object sender, RoutedEventArgs e)
        {
            // Same as SaveAnalysis_Click for now
            SaveAnalysis_Click(sender, e);
        }

        private void Exit_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }

        #endregion

        #region Analysis Event Handlers

        private async void StartAnalysis_Click(object sender, RoutedEventArgs e)
        {
            if (_currentGame == null)
            {
                MessageBox.Show("Please load a PGN file or FEN position first.", "No Game Loaded", 
                              MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            try
            {
                // Parse analysis parameters
                if (!int.TryParse(DepthTextBox.Text, out int depth) || depth < 1)
                {
                    MessageBox.Show("Please enter a valid depth (1 or greater).", "Invalid Depth", 
                                  MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                if (!double.TryParse(TimeTextBox.Text, out double timePerMove) || timePerMove <= 0)
                {
                    MessageBox.Show("Please enter a valid analysis time (greater than 0).", "Invalid Time", 
                                  MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                // Start analysis
                var analysisSettings = new AnalysisSettings
                {
                    MaxDepth = depth,
                    TimePerPosition = TimeSpan.FromSeconds(timePerMove),
                    WhiteMovesToAnalyze = 3,
                    BlackMovesToAnalyze = 3,
                    WhiteThreshold = 30,
                    BlackThreshold = 30
                };

                StartAnalysisButton.IsEnabled = false;
                StopAnalysisButton.IsEnabled = true;
                AnalysisProgressBar.Visibility = Visibility.Visible;
                StatusText.Text = "Starting analysis...";

                await _analysisService.StartAnalysisAsync(_currentGame, analysisSettings);
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
            _analysisService.StopAnalysis();
            ResetAnalysisUI();
            StatusText.Text = "Analysis stopped by user";
        }

        #endregion

        #region Analysis Event Handlers

        private void OnAnalysisProgressChanged(object sender, AnalysisProgressEventArgs e)
        {
            Dispatcher.Invoke(() =>
            {
                AnalysisProgressBar.Value = e.ProgressPercentage;
                ProgressText.Text = $"{e.PositionsAnalyzed}/{e.TotalPositions}";
                StatusText.Text = e.CurrentMove;
            });
        }

        private void OnAnalysisCompleted(object sender, AnalysisCompletedEventArgs e)
        {
            Dispatcher.Invoke(() =>
            {
                ResetAnalysisUI();
                
                if (e.Success)
                {
                    // Update the analysis tree view
                    PopulateAnalysisTree(e.AnalysisResult);
                    StatusText.Text = $"Analysis completed. {e.PositionsAnalyzed} positions analyzed.";
                }
                else
                {
                    StatusText.Text = $"Analysis failed: {e.ErrorMessage}";
                    MessageBox.Show($"Analysis failed: {e.ErrorMessage}", "Analysis Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            });
        }

        private void OnAnalysisOutputReceived(object sender, string output)
        {
            Dispatcher.Invoke(() =>
            {
                OutputTextBlock.Text += output + Environment.NewLine;
                
                // Auto-scroll to bottom
                if (OutputTextBlock.Parent is ScrollViewer scrollViewer)
                {
                    scrollViewer.ScrollToBottom();
                }
            });
        }

        #endregion

        #region UI Helper Methods

        private void UpdateUI()
        {
            bool hasGame = _currentGame != null;
            StartAnalysisButton.IsEnabled = hasGame;
            
            // Update window title
            if (hasGame)
            {
                Title = $"Chess Tree Analyzer - {_currentGame.GameInfo}";
            }
            else
            {
                Title = "Chess Tree Analyzer";
            }
        }

        private void ResetAnalysisUI()
        {
            StartAnalysisButton.IsEnabled = _currentGame != null;
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
                var treeViewItem = CreateTreeViewItem(rootNode);
                AnalysisTreeView.Items.Add(treeViewItem);
                treeViewItem.IsExpanded = true;
            }
        }

        private TreeViewItem CreateTreeViewItem(AnalysisTreeNode node)
        {
            var item = new TreeViewItem
            {
                Header = node.DisplayText,
                Tag = node
            };

            foreach (var child in node.Children)
            {
                item.Items.Add(CreateTreeViewItem(child));
            }

            return item;
        }

        #endregion

        #region Other Event Handlers

        private void AnalysisSettings_Click(object sender, RoutedEventArgs e)
        {
            // TODO: Open analysis settings dialog
            MessageBox.Show("Analysis settings dialog will be implemented.", "Coming Soon", 
                          MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void EngineSettings_Click(object sender, RoutedEventArgs e)
        {
            // TODO: Open engine settings dialog
            MessageBox.Show("Engine settings dialog will be implemented.", "Coming Soon", 
                          MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void ToggleBoard_Click(object sender, RoutedEventArgs e)
        {
            // TODO: Toggle board visibility
        }

        private void ToggleAnalysisTree_Click(object sender, RoutedEventArgs e)
        {
            // TODO: Toggle analysis tree visibility
        }

        private void ToggleOutput_Click(object sender, RoutedEventArgs e)
        {
            // TODO: Toggle output visibility
        }

        private void ResetLayout_Click(object sender, RoutedEventArgs e)
        {
            // TODO: Reset window layout to default
        }

        private void About_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Chess Tree Analyzer v1.0\n\nA professional chess analysis application.", 
                          "About", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void UserGuide_Click(object sender, RoutedEventArgs e)
        {
            // TODO: Open user guide
            MessageBox.Show("User guide will be implemented.", "Coming Soon", 
                          MessageBoxButton.OK, MessageBoxImage.Information);
        }

        #endregion

        protected override void OnClosed(EventArgs e)
        {
            // Clean up resources
            _stockfishService?.Dispose();
            base.OnClosed(e);
        }
    }
}