// Evaluation normalization and move filtering.
// Stockfish reports scores relative to the side to move. We keep both a
// "side-to-move" value (for filtering/sorting) and a "White's perspective"
// value (for display and PGN comments).

const MATE_BASE = 100000;

// Convert a raw parsed engine result into a normalized eval for a position
// where `whiteToMove` indicates the side on move.
export function normalizeEval(parsed, whiteToMove) {
  if (parsed.scoreType === "mate") {
    const sideMate = parsed.scoreValue; // + = side to move delivers mate
    const whiteMate = whiteToMove ? sideMate : -sideMate;
    return {
      uci: parsed.uci,
      pv: parsed.pv,
      depth: parsed.depth,
      isMate: true,
      sideMate,
      whiteMate,
      whiteCp: null,
    };
  }
  const sideCp = parsed.scoreValue;
  const whiteCp = whiteToMove ? sideCp : -sideCp;
  return {
    uci: parsed.uci,
    pv: parsed.pv,
    depth: parsed.depth,
    isMate: false,
    sideCp,
    whiteCp,
    whiteMate: null,
  };
}

// A single comparable number from the side-to-move's perspective.
// Higher is better for the side to move.
function sideScoreValue(n) {
  if (n.isMate) {
    return n.sideMate > 0
      ? MATE_BASE - n.sideMate * 100
      : -MATE_BASE - n.sideMate * 100;
  }
  return n.sideCp;
}

// Filter a list of normalized moves (already best-first from MultiPV) down to
// the ones we keep, applying the centipawn threshold and max move count.
export function filterMoves(normalized, threshold, maxMoves) {
  if (!normalized.length) return [];

  const best = normalized[0];

  // If the best move is a forced mate for the side to move, end the line here.
  if (best.isMate && best.sideMate > 0) {
    return [best];
  }

  const kept = [best];
  const bestVal = sideScoreValue(best);

  for (let i = 1; i < Math.min(maxMoves, normalized.length); i++) {
    const m = normalized[i];

    // Never include a move that walks into a forced mate against us.
    if (m.isMate && m.sideMate < 0) continue;

    // Favorable mates are always worth keeping.
    if (m.isMate || best.isMate) {
      kept.push(m);
      continue;
    }

    const diff = bestVal - sideScoreValue(m);
    if (diff <= threshold) {
      kept.push(m);
    }
  }

  return kept;
}

// Human-readable label from White's perspective, e.g. "+1.35" or "#5" / "-#3".
export function formatEvalDisplay(node) {
  if (node.isMate) {
    const m = node.whiteMate;
    if (m > 0) return `#${m}`;
    return `-#${Math.abs(m)}`;
  }
  const pawns = (node.whiteCp ?? 0) / 100;
  return `${pawns >= 0 ? "+" : ""}${pawns.toFixed(2)}`;
}

// PGN comment value from White's perspective: centipawns "{+150}" or mate "{#5}".
export function formatEvalComment(node) {
  if (node.isMate) {
    const m = node.whiteMate;
    return m > 0 ? `#${m}` : `-#${Math.abs(m)}`;
  }
  const cp = node.whiteCp ?? 0;
  return `${cp >= 0 ? "+" : ""}${cp}`;
}
