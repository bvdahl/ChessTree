using System.Windows;

namespace ChessTreeAnalyzer
{
    public partial class FENInputDialog : Window
    {
        public string FENString { get; private set; }

        public FENInputDialog()
        {
            InitializeComponent();
            FENTextBox.Focus();
            FENTextBox.SelectAll();
        }

        private void OK_Click(object sender, RoutedEventArgs e)
        {
            FENString = FENTextBox.Text.Trim();
            
            if (string.IsNullOrEmpty(FENString))
            {
                MessageBox.Show("Please enter a valid FEN string.", "Invalid FEN", 
                              MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            // Basic FEN validation
            var parts = FENString.Split(' ');
            if (parts.Length < 4)
            {
                MessageBox.Show("FEN string must have at least 4 parts separated by spaces.", "Invalid FEN", 
                              MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            DialogResult = true;
            Close();
        }

        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }
}