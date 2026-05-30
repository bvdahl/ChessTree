// Breadth-first chess variation tree generator.
// Game moves form the main line (depth 0); analysis begins from the final
// game position (the leaf) and expands outward depth by depth.

import { Chess } from "chess.js";
import { normalizeEval, filterMoves } from "./evaluation.js";

let nodeCounter = 0;
function nextId() {
  return `n${nodeCounter++}`;
}

function uciToMoveObj(uci) {
  return {
    from: uci.slice(0, 2),
    to: uci.slice(2, 4),
    promotion: uci.length > 4 ? uci[4] : undefined,
  };
}

function whiteToMoveFromFen(fen) {
  return fen.split(" ")[1] === "w";
}

// Turn a list of SAN moves into a readable, numbered line for progress display.
function formatLine(startFen, sans) {
  const parts = startFen.split(" ");
  let moveNo = parseInt(parts[5], 10) || 1;
  let whiteToMove = parts[1] === "w";
  const out = [];
  for (const san of sans) {
    if (whiteToMove) out.push(`${moveNo}. ${san}`);
    else {
      out.push(out.length === 0 ? `${moveNo}... ${san}` : san);
      moveNo += 1;
    }
    whiteToMove = !whiteToMove;
  }
  return out.join(" ");
}

// Build the root + game-move chain. Returns { root, leaf, leafLine }.
function buildGameLine(startFen, gameMoves) {
  const root = {
    id: nextId(),
    fenBefore: null,
    fen: startFen,
    move: null,
    depth: 0,
    isGameMove: false,
    isRoot: true,
    eval: null,
    children: [],
  };

  let current = root;
  const chess = new Chess(startFen);
  const leafLine = [];

  for (const gm of gameMoves) {
    let moveResult;
    try {
      moveResult = chess.move(gm.san ?? uciToMoveObj(gm.uci));
    } catch (e) {
      break; // Stop on first illegal move; keep what parsed.
    }
    if (!moveResult) break;

    const node = {
      id: nextId(),
      fenBefore: current.fen,
      fen: chess.fen(),
      move: { san: moveResult.san, uci: moveResult.lan },
      depth: 0,
      isGameMove: true,
      isRoot: false,
      eval: null,
      children: [],
    };
    current.children.push(node);
    current = node;
    leafLine.push(moveResult.san);
  }

  return { root, leaf: current, leafLine };
}

// Analyze a tree from a starting position.
//   params: { startFen, gameMoves, settings }
//   settings: { maxDepth, moveTimeMs, whiteMoves, blackMoves,
//               whiteThreshold, blackThreshold }
//   onProgress({ analyzed, queued, depth, line }) is called as work proceeds.
//   signal: AbortSignal to stop early (partial tree is still returned).
export async function generateTree(engine, params, onProgress, signal) {
  nodeCounter = 0;
  const { startFen, gameMoves, settings } = params;
  const { root, leaf, leafLine } = buildGameLine(startFen, gameMoves);

  // BFS queue of position nodes to expand. Start from the leaf.
  const queue = [{ node: leaf, depth: 0, line: leafLine.slice() }];
  let analyzed = 0;

  while (queue.length) {
    if (signal && signal.aborted) break;

    const { node, depth, line } = queue.shift();
    if (depth >= settings.maxDepth) continue;

    const whiteToMove = whiteToMoveFromFen(node.fen);
    const movesToAnalyze = whiteToMove
      ? settings.whiteMoves
      : settings.blackMoves;
    const threshold = whiteToMove
      ? settings.whiteThreshold
      : settings.blackThreshold;

    // Skip terminal positions (checkmate/stalemate/no legal moves).
    let chess;
    try {
      chess = new Chess(node.fen);
    } catch (e) {
      continue;
    }
    if (chess.isGameOver() || chess.moves().length === 0) continue;

    let parsedMoves;
    try {
      parsedMoves = await engine.analyze(
        node.fen,
        { multiPv: movesToAnalyze, moveTimeMs: settings.moveTimeMs },
        signal
      );
    } catch (e) {
      continue;
    }

    analyzed += 1;

    const normalized = parsedMoves.map((p) => normalizeEval(p, whiteToMove));
    const kept = filterMoves(normalized, threshold, movesToAnalyze);

    for (const ev of kept) {
      if (!ev.uci) continue;
      const childChess = new Chess(node.fen);
      let mv;
      try {
        mv = childChess.move(uciToMoveObj(ev.uci));
      } catch (e) {
        continue;
      }
      if (!mv) continue;

      const childNode = {
        id: nextId(),
        fenBefore: node.fen,
        fen: childChess.fen(),
        move: { san: mv.san, uci: mv.lan },
        depth: depth + 1,
        isGameMove: false,
        isRoot: false,
        eval: ev,
        children: [],
      };
      node.children.push(childNode);
      queue.push({
        node: childNode,
        depth: depth + 1,
        line: [...line, mv.san],
      });
    }

    if (onProgress) {
      onProgress({
        analyzed,
        queued: queue.length,
        depth,
        line: line.length ? formatLine(startFen, line) : "(start position)",
      });
    }
  }

  return root;
}

// Parse a PGN string into a start FEN and a list of game moves.
export function parsePgn(pgnText) {
  const chess = new Chess();
  chess.loadPgn(pgnText);

  // Reconstruct the move list with SAN by replaying from the header FEN.
  const headers = chess.header();
  const startFen = headers.FEN || new Chess().fen();

  const verbose = chess.history({ verbose: true });
  const gameMoves = verbose.map((m) => ({ san: m.san, uci: m.lan }));

  return { startFen, gameMoves };
}
