using System;
using System.IO;
using Newtonsoft.Json;

namespace ChessTreeAnalyzer.Models
{
    public class AnalysisSettings
    {
        public int MaxDepth { get; set; } = 3;
        public TimeSpan TimePerPosition { get; set; } = TimeSpan.FromSeconds(60);
        public int WhiteMovesToAnalyze { get; set; } = 3;
        public int BlackMovesToAnalyze { get; set; } = 3;
        public int WhiteThreshold { get; set; } = 30; // Centipawns
        public int BlackThreshold { get; set; } = 30; // Centipawns
        public int HashSizeMB { get; set; } = 8192;
        public int ThreadCount { get; set; } = Environment.ProcessorCount;
        public string StockfishPath { get; set; } = "stockfish.exe";
        public bool EnableMateFiltering { get; set; } = true;
        public bool ShowFilteredMoves { get; set; } = true;
        
        // Output settings
        public string OutputDirectory { get; set; } = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
        public string BaseFilename { get; set; } = "chess_analysis";
        public bool SavePGN { get; set; } = true;
        public bool SaveJSON { get; set; } = false;
        public bool AutoSaveDiagnostics { get; set; } = true;

        public AnalysisSettings Clone()
        {
            return new AnalysisSettings
            {
                MaxDepth = MaxDepth,
                TimePerPosition = TimePerPosition,
                WhiteMovesToAnalyze = WhiteMovesToAnalyze,
                BlackMovesToAnalyze = BlackMovesToAnalyze,
                WhiteThreshold = WhiteThreshold,
                BlackThreshold = BlackThreshold,
                HashSizeMB = HashSizeMB,
                ThreadCount = ThreadCount,
                StockfishPath = StockfishPath,
                EnableMateFiltering = EnableMateFiltering,
                ShowFilteredMoves = ShowFilteredMoves,
                OutputDirectory = OutputDirectory,
                BaseFilename = BaseFilename,
                SavePGN = SavePGN,
                SaveJSON = SaveJSON,
                AutoSaveDiagnostics = AutoSaveDiagnostics
            };
        }

        public void Validate()
        {
            if (MaxDepth < 1)
                throw new ArgumentException("Max depth must be at least 1");
            
            if (TimePerPosition.TotalSeconds <= 0)
                throw new ArgumentException("Time per position must be greater than 0");
            
            if (WhiteMovesToAnalyze < 1)
                throw new ArgumentException("White moves to analyze must be at least 1");
            
            if (BlackMovesToAnalyze < 1)
                throw new ArgumentException("Black moves to analyze must be at least 1");
            
            if (HashSizeMB < 1)
                throw new ArgumentException("Hash size must be at least 1 MB");
            
            if (ThreadCount < 1)
                throw new ArgumentException("Thread count must be at least 1");
            
            if (string.IsNullOrWhiteSpace(StockfishPath))
                throw new ArgumentException("Stockfish path cannot be empty");
        }

        public void SaveToFile(string filePath)
        {
            var json = JsonConvert.SerializeObject(this, Formatting.Indented);
            File.WriteAllText(filePath, json);
        }

        public static AnalysisSettings LoadFromFile(string filePath)
        {
            var json = File.ReadAllText(filePath);
            return JsonConvert.DeserializeObject<AnalysisSettings>(json);
        }
    }
}