#!/bin/bash

echo "Setting up C# WPF Chess Tree Analyzer development environment..."

# Check if dotnet is available
if ! command -v dotnet &> /dev/null; then
    echo "Error: .NET SDK not found. Please install .NET 8 SDK."
    exit 1
fi

echo "Found .NET SDK version:"
dotnet --version

# Navigate to the C# project directory
cd ChessTreeAnalyzer

echo "Restoring NuGet packages..."
dotnet restore

echo "Building the project..."
dotnet build --configuration Debug

if [ $? -eq 0 ]; then
    echo "✅ C# project built successfully!"
    echo ""
    echo "Project structure created:"
    echo "- Complete WPF application with professional UI"
    echo "- Interactive chess board visualization"
    echo "- Analysis tree display"
    echo "- Stockfish engine integration"
    echo "- Modern MVVM architecture"
    echo ""
    echo "To run the application:"
    echo "  cd ChessTreeAnalyzer"
    echo "  dotnet run"
    echo ""
    echo "Note: This is a development build. For Windows deployment,"
    echo "the application would be compiled to a native executable."
else
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi