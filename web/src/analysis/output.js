// PGN and JSON output generation from a variation tree.
// Produces ChessBase-compatible nested variations with eval comments.

import { formatEvalComment } from "./evaluation.js";

function fenInfo(fen) {
  const parts = fen.split(" ");
  return {
    whiteToMove: parts[1] === "w",
    moveNumber: parseInt(parts[5], 10) || 1,
  };
}

function formatMove(node, forceNumber) {
  const { whiteToMove, moveNumber } = fenInfo(node.fenBefore);
  let prefix = "";
  if (whiteToMove) prefix = `${moveNumber}. `;
  else if (forceNumber) prefix = `${moveNumber}... `;

  let text = prefix + node.move.san;

  // Add eval comments only for analyzed moves (game moves carry no eval).
  if (node.eval) {
    text += ` {${formatEvalComment(node.eval)}}`;
  }
  return text;
}

// Walk the line beginning at `node` (a position node) and emit its main line
// with nested variations. Returns a token string.
function buildLine(node) {
  const tokens = [];
  let cur = node;
  let forceNumber = true;

  while (cur.children.length) {
    const main = cur.children[0];
    const variations = cur.children.slice(1);

    tokens.push(formatMove(main, forceNumber));

    for (const v of variations) {
      const inner = buildLine(v);
      const head = formatMove(v, true);
      tokens.push(inner ? `(${head} ${inner})` : `(${head})`);
    }

    // After a branch, the next black move needs its number again.
    forceNumber = variations.length > 0;
    cur = main;
  }

  return tokens.join(" ");
}

export function treeToPgn(root, meta = {}) {
  const headers = [];
  const event = meta.event || "Chess Tree Analysis";
  headers.push(`[Event "${event}"]`);
  headers.push(`[Site "Chess Tree Analyzer"]`);
  headers.push(`[Date "${meta.date || new Date().toISOString().slice(0, 10)}"]`);
  headers.push(`[Round "-"]`);
  headers.push(`[White "${meta.white || "Analysis"}"]`);
  headers.push(`[Black "${meta.black || "Analysis"}"]`);
  headers.push(`[Result "*"]`);
  const STANDARD_START =
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
  if (root.fen && root.fen !== STANDARD_START) {
    headers.push(`[SetUp "1"]`);
    headers.push(`[FEN "${root.fen}"]`);
  }

  const moves = buildLine(root);
  const body = moves ? `${moves} *` : "*";

  return `${headers.join("\n")}\n\n${body}\n`;
}

export function treeToJson(root) {
  function serialize(node) {
    const out = {
      move: node.move ? node.move.san : null,
      uci: node.move ? node.move.uci : null,
      fen: node.fen,
      depth: node.depth,
      isGameMove: node.isGameMove,
    };
    if (node.eval) {
      out.eval = node.eval.isMate
        ? { mate: node.eval.whiteMate }
        : { cp: node.eval.whiteCp };
    }
    if (node.children.length) {
      out.children = node.children.map(serialize);
    }
    return out;
  }
  return JSON.stringify(serialize(root), null, 2);
}

// Count total analyzed nodes (excludes game moves and root).
export function countAnalyzedNodes(root) {
  let count = 0;
  const stack = [root];
  while (stack.length) {
    const n = stack.pop();
    if (n.eval) count += 1;
    for (const c of n.children) stack.push(c);
  }
  return count;
}
