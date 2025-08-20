using System;
using ChessTreeAnalyzer.Models;

namespace ChessTreeAnalyzer
{
    // Simple test to verify position changes are working
    public class TestPositionChanges
    {
        public static void RunTest()
        {
            Console.WriteLine("=== Testing Position Changes ===\n");
            
            // Test 1: Starting position
            var startPos = new ProperChessBoard();
            Console.WriteLine($"Starting FEN: {startPos.FEN}");
            Console.WriteLine($"White to move: {startPos.WhiteToMove}");
            Console.WriteLine($"Move number: {startPos.MoveNumber}");
            Console.WriteLine();
            
            // Test 2: Make e2e4
            Console.WriteLine("Making move: e2e4");
            var pos2 = startPos.MakeMove("e2e4");
            Console.WriteLine($"New FEN: {pos2.FEN}");
            Console.WriteLine($"White to move: {pos2.WhiteToMove}");
            Console.WriteLine($"Move number: {pos2.MoveNumber}");
            Console.WriteLine($"FEN changed: {pos2.FEN != startPos.FEN}");
            Console.WriteLine();
            
            // Test 3: Make e7e5
            Console.WriteLine("Making move: e7e5");
            var pos3 = pos2.MakeMove("e7e5");
            Console.WriteLine($"New FEN: {pos3.FEN}");
            Console.WriteLine($"White to move: {pos3.WhiteToMove}");
            Console.WriteLine($"Move number: {pos3.MoveNumber}");
            Console.WriteLine($"FEN changed: {pos3.FEN != pos2.FEN}");
            Console.WriteLine();
            
            // Test 4: Make invalid move (should return same position)
            Console.WriteLine("Making invalid move: a9a9");
            var pos4 = pos3.MakeMove("a9a9");
            Console.WriteLine($"New FEN: {pos4.FEN}");
            Console.WriteLine($"FEN unchanged (as expected): {pos4.FEN == pos3.FEN}");
            Console.WriteLine();
            
            // Test 5: Your specific position
            var yourPos = new ProperChessBoard("r1bqkb1r/ppp2ppp/8/4P3/8/2pP1N2/P1P3PP/R1BQKB1R w KQkq - 0 8");
            Console.WriteLine($"Your position FEN: {yourPos.FEN}");
            Console.WriteLine($"White to move: {yourPos.WhiteToMove}");
            Console.WriteLine($"Move number: {yourPos.MoveNumber}");
            
            // Try some moves from this position
            Console.WriteLine("\nTrying move Ng5:");
            var testMove1 = yourPos.MakeMove("f3g5");
            Console.WriteLine($"New FEN: {testMove1.FEN}");
            Console.WriteLine($"FEN changed: {testMove1.FEN != yourPos.FEN}");
            
            Console.WriteLine("\nTrying move Bd2:");
            var testMove2 = yourPos.MakeMove("c1d2");
            Console.WriteLine($"New FEN: {testMove2.FEN}");
            Console.WriteLine($"FEN changed: {testMove2.FEN != yourPos.FEN}");
        }
    }
}