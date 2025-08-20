using System;
using System.IO;
using ChessTreeAnalyzer.Models;
using Newtonsoft.Json;

namespace ChessTreeAnalyzer.Services
{
    public class SettingsService
    {
        private static readonly string SettingsFolder = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), 
            "ChessTreeAnalyzer");
        private static readonly string SettingsFile = Path.Combine(SettingsFolder, "settings.json");

        public static void SaveSettings(AnalysisSettings settings)
        {
            try
            {
                Directory.CreateDirectory(SettingsFolder);
                var json = JsonConvert.SerializeObject(settings, Formatting.Indented);
                File.WriteAllText(SettingsFile, json);
            }
            catch (Exception ex)
            {
                // Log error but don't throw - settings persistence shouldn't crash the app
                System.Diagnostics.Debug.WriteLine($"Failed to save settings: {ex.Message}");
            }
        }

        public static AnalysisSettings LoadSettings()
        {
            try
            {
                if (File.Exists(SettingsFile))
                {
                    var json = File.ReadAllText(SettingsFile);
                    return JsonConvert.DeserializeObject<AnalysisSettings>(json) ?? new AnalysisSettings();
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to load settings: {ex.Message}");
            }

            return new AnalysisSettings();
        }
    }
}