import React, { useState, useEffect } from "react";
import { formatEvalDisplay } from "../analysis/evaluation.js";

// Bracket pairs cycle by nesting depth, the way ChessBase shows nested
// variations: ( ) for the first level, [ ] for the next, { } deeper still.
const BRACKETS = [
  ["(", ")"],
  ["[", "]"],
  ["{", "}"],
];

function evalClass(ev) {
  if (!ev) return "vt-eval-neutral";
  if (ev.isMate) return "vt-eval-mate";
  if ((ev.whiteCp ?? 0) > 20) return "vt-eval-pos";
  if ((ev.whiteCp ?? 0) < -20) return "vt-eval-neg";
  return "vt-eval-neutral";
}

// The move number shown before a move. White moves always show "N."; black
// moves only show "N..." when a number is needed (start of a line, or right
// after a variation interrupted the flow).
function numberPrefix(node, forceNumber) {
  if (!node.fenBefore) return "";
  const parts = node.fenBefore.split(" ");
  const whiteToMove = parts[1] === "w";
  const num = parseInt(parts[5], 10) || 1;
  if (whiteToMove) return `${num}.`;
  return forceNumber ? `${num}...` : "";
}

export default function VariationTree({ root, selectedId, onSelect }) {
  // Ids of variations the user has folded away.
  const [collapsed, setCollapsed] = useState(() => new Set());
  const hasContent = root && root.children.length > 0;

  // Node ids are reused (the counter resets) each time a new tree is built, so
  // clear any folded branches whenever a fresh analysis arrives — otherwise old
  // ids could accidentally collapse unrelated branches in the new tree.
  useEffect(() => {
    setCollapsed(new Set());
  }, [root]);

  function toggle(id) {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  // A single clickable move: number + SAN + (for analysed moves) an eval.
  function moveToken(node, forceNumber, isMain) {
    const num = numberPrefix(node, forceNumber);
    const cls =
      "vt-move" +
      (isMain ? " main" : "") +
      (node.isGameMove ? " game" : "") +
      (node.id === selectedId ? " selected" : "");
    return (
      <span
        key={node.id}
        className={cls}
        onClick={() => onSelect(node)}
        title={
          (node.isGameMove
            ? "Game move — click to view this position on the board"
            : "Suggested move — click to view this position on the board") +
          (node.eval ? " · Evaluation from White's point of view" : "")
        }
      >
        {num ? <span className="vt-num">{num}</span> : null}
        <span className="vt-san">{node.move.san}</span>
        {node.eval ? (
          <span className={"vt-eval " + evalClass(node.eval)}>
            {formatEvalDisplay(node.eval)}
          </span>
        ) : null}
      </span>
    );
  }

  // A side-variation: an alternative move `v` plus everything that follows it,
  // wrapped in brackets and foldable with a small +/- toggle.
  function renderVariation(v, depthLevel) {
    const [open, close] = BRACKETS[depthLevel % BRACKETS.length];
    const isCollapsed = collapsed.has(v.id);

    const inner = [moveToken(v, true, false)];
    if (!isCollapsed) {
      // Mirror output.js buildLine(v): the continuation starts with the number
      // forced, so the on-screen notation matches the exported PGN exactly.
      const cont = renderContinuation(v, depthLevel + 1, true, false);
      if (cont.length) {
        inner.push(" ");
        inner.push(...cont);
      }
    }

    return (
      <span
        key={"var-" + v.id}
        className="vt-var"
        data-depth={depthLevel % BRACKETS.length}
      >
        <button
          className="vt-toggle"
          onClick={(e) => {
            e.stopPropagation();
            toggle(v.id);
          }}
          title={isCollapsed ? "Show this variation" : "Hide this variation"}
          aria-label={isCollapsed ? "Show this variation" : "Hide this variation"}
        >
          {isCollapsed ? "+" : "\u2212"}
        </button>
        <span className="vt-bracket">{open}</span>
        {isCollapsed ? <span className="vt-ellipsis">…</span> : inner}
        <span className="vt-bracket">{close}</span>
      </span>
    );
  }

  // Walk a position's line: its main continuation (first child chain) plus the
  // alternative moves at each step, rendered as nested variations.
  function renderContinuation(node, depthLevel, forceNumberFirst, isMain) {
    const out = [];
    let cur = node;
    let forceNumber = forceNumberFirst;

    while (cur.children.length) {
      const main = cur.children[0];
      const variations = cur.children.slice(1);

      if (out.length) out.push(" ");
      out.push(moveToken(main, forceNumber, isMain));

      for (const v of variations) {
        out.push(" ");
        out.push(renderVariation(v, depthLevel));
      }

      // After a branch interrupts the flow, the next black move needs its
      // number repeated.
      forceNumber = variations.length > 0;
      cur = main;
    }

    return out;
  }

  return (
    <div className="column right">
      <div className="tree-header">
        <h2>Variation Tree</h2>
      </div>
      <div className="tree-body">
        {!hasContent ? (
          <div className="tree-empty">
            No analysis yet. Load a position and run the analysis to build a
            variation tree.
          </div>
        ) : (
          <div className="vt-flow">
            <span
              className={
                "vt-move vt-start" + (root.id === selectedId ? " selected" : "")
              }
              onClick={() => onSelect(root)}
              title="The starting position — click to view it on the board"
            >
              Start
            </span>{" "}
            {renderContinuation(root, 0, true, true)}
          </div>
        )}
      </div>
      <div className="footer-note">
        Bold = main line · Blue = game moves · ( ) variations · +/− folds a
        branch · Click a move to view it
      </div>
    </div>
  );
}
