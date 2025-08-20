using System.Windows;

namespace ChessTreeAnalyzer
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            
            // Initialize application-level services
            InitializeServices();
        }

        private void InitializeServices()
        {
            // Register dependency injection services here if needed
        }
    }
}