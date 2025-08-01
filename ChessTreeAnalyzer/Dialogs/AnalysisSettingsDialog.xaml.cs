using System;
using System.Windows;
using Microsoft.Win32;
using ChessTreeAnalyzer.Models;

namespace ChessTreeAnalyzer.Dialogs
{
    public partial class AnalysisSettingsDialog : Window
    {
        public AnalysisSettings Settings { get; private set; }

        public AnalysisSettingsDialog()
        {
            InitializeComponent();
            LoadDefaultSettings();
        }

        public AnalysisSettingsDialog(AnalysisSettings currentSettings) : this()
        {
            if (currentSettings != null)
            {
                LoadSettings(currentSettings);
            }
        }

        private void LoadDefaultSettings()
        {
            var settings = new AnalysisSettings();
            LoadSettings(settings);
        }

        private void LoadSettings(AnalysisSettings settings)
        {
            StockfishPathTextBox.Text = settings.StockfishPath;
            HashSizeTextBox.Text = settings.HashSizeMB.ToString();
            ThreadCountTextBox.Text = settings.ThreadCount.ToString();
            AnalysisTimeTextBox.Text = settings.TimePerPosition.TotalSeconds.ToString("F1");
            MaxDepthSlider.Value = settings.MaxDepth;
            WhiteMovesTextBox.Text = settings.WhiteMovesToAnalyze.ToString();
            BlackMovesTextBox.Text = settings.BlackMovesToAnalyze.ToString();
            WhiteThresholdTextBox.Text = settings.WhiteThreshold.ToString();
            BlackThresholdTextBox.Text = settings.BlackThreshold.ToString();
        }

        private void BrowseStockfish_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new OpenFileDialog
            {
                Title = "Select Stockfish Executable",
                Filter = "Executable Files (*.exe)|*.exe|All Files (*.*)|*.*",
                CheckFileExists = true
            };

            if (dialog.ShowDialog() == true)
            {
                StockfishPathTextBox.Text = dialog.FileName;
            }
        }

        private void MaxDepthSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (DepthValueText != null)
            {
                DepthValueText.Text = $"Depth: {(int)MaxDepthSlider.Value}";
            }
        }

        private void LoadPreset_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new OpenFileDialog
            {
                Title = "Load Analysis Preset",
                Filter = "JSON Files (*.json)|*.json|All Files (*.*)|*.*",
                CheckFileExists = true
            };

            if (dialog.ShowDialog() == true)
            {
                try
                {
                    var presetSettings = AnalysisSettings.LoadFromFile(dialog.FileName);
                    LoadSettings(presetSettings);
                    MessageBox.Show($"Preset loaded successfully from {System.IO.Path.GetFileName(dialog.FileName)}", 
                                  "Preset Loaded", MessageBoxButton.OK, MessageBoxImage.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error loading preset: {ex.Message}", "Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void SavePreset_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new SaveFileDialog
            {
                Title = "Save Analysis Preset",
                Filter = "JSON Files (*.json)|*.json|All Files (*.*)|*.*",
                DefaultExt = "json"
            };

            if (dialog.ShowDialog() == true)
            {
                try
                {
                    var settings = CreateSettingsFromUI();
                    settings.SaveToFile(dialog.FileName);
                    MessageBox.Show($"Preset saved successfully to {System.IO.Path.GetFileName(dialog.FileName)}", 
                                  "Preset Saved", MessageBoxButton.OK, MessageBoxImage.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error saving preset: {ex.Message}", "Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void Ok_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Settings = CreateSettingsFromUI();
                Settings.Validate();
                DialogResult = true;
                Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Invalid settings: {ex.Message}", "Settings Error", 
                              MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }

        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }

        private AnalysisSettings CreateSettingsFromUI()
        {
            return new AnalysisSettings
            {
                StockfishPath = StockfishPathTextBox.Text.Trim(),
                HashSizeMB = int.Parse(HashSizeTextBox.Text),
                ThreadCount = int.Parse(ThreadCountTextBox.Text),
                TimePerPosition = TimeSpan.FromSeconds(double.Parse(AnalysisTimeTextBox.Text)),
                MaxDepth = (int)MaxDepthSlider.Value,
                WhiteMovesToAnalyze = int.Parse(WhiteMovesTextBox.Text),
                BlackMovesToAnalyze = int.Parse(BlackMovesTextBox.Text),
                WhiteThreshold = int.Parse(WhiteThresholdTextBox.Text),
                BlackThreshold = int.Parse(BlackThresholdTextBox.Text)
            };
        }
    }
}