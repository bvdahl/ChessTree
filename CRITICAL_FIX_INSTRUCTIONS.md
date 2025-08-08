# Critical Fix for Chess Tree Analyzer

## The Issue
The moves from Stockfish are not being applied because the UCI and SAN parameters are likely reversed in the SimpleMove constructor.

## Quick Manual Fix
If you can't download the fixed version, here's what to change in your local copy:

### File: ChessTreeAnalyzer/Services/StockfishService.cs
Around line 180, find this code:
```csharp
case "pv":
    if (i + 1 < parts.Length)
    {
        var uciMove = parts[i + 1];
        // Convert UCI to SAN notation
        var sanMove = ConvertUciToSan(uciMove, position);
        analyzedMove.Move = new SimpleMove(sanMove, uciMove, 0);  // <-- THIS IS WRONG
        analyzedMove.MoveNotation = sanMove;
    }
    break;
```

Change it to:
```csharp
case "pv":
    if (i + 1 < parts.Length)
    {
        var uciMove = parts[i + 1];
        // Convert UCI to SAN notation
        var sanMove = ConvertUciToSan(uciMove, position);
        analyzedMove.Move = new SimpleMove(uciMove, sanMove, 0);  // <-- FIXED: UCI first, then SAN
        analyzedMove.MoveNotation = sanMove;
    }
    break;
```

## The SimpleMove Constructor
The SimpleMove constructor expects parameters in this order:
```csharp
public SimpleMove(string uci, string san, int eval = 0)
```

But the code was calling it with `(sanMove, uciMove, 0)` which put SAN in the UCI field and vice versa.

## To Verify the Fix
After making this change and rebuilding:
1. Run an analysis
2. Check the diagnostics file
3. You should see moves actually being applied and different positions being analyzed

## Expected Output After Fix
Instead of:
```
ERROR: Position unchanged after move d4!
```

You should see:
```
New FEN after d3d4: [different FEN showing the position after the move]
```

The analysis should then continue to explore multiple positions instead of being stuck on one.