import React, { useState, useEffect } from "react";
import { formatEvalDisplay } from "../analysis/evaluation.js";

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

  // Walk a chain from `start`, collecting the main line as inline tokens and the
  // alternatives at each step as nested, indented variation blocks. `includeSelf`
  // is true for a side-variation (we render its own first move) and false for the
  // root spine (which has no move of its own).
  function buildChain(start, includeSelf, forceNumberFirst, isMain) {
    const inline = [];
    const subBlocks = [];
    let cur = start;
    let forceNumber = forceNumberFirst;

    if (includeSelf) {
      inline.push(moveToken(start, true, isMain));
      forceNumber = false;
    }

    while (cur.children.length) {
      const main = cur.children[0];
      const alts = cur.children.slice(1);

      if (inline.length) inline.push(" ");
      inline.push(moveToken(main, forceNumber, isMain));

      for (const alt of alts) {
        subBlocks.push(renderVariationBlock(alt));
      }

      // After a branch interrupts the flow, the next black move needs its
      // number repeated.
      forceNumber = alts.length > 0;
      cur = main;
    }

    return { inline, subBlocks };
  }

  // An alternative move plus everything that follows it, rendered on its own
  // indented line. Deeper alternatives nest further via the DOM, foldable with a
  // small +/- toggle.
  function renderVariationBlock(v) {
    const isCollapsed = collapsed.has(v.id);
    const hasMore = v.children.length > 0;

    let inline;
    let subBlocks = [];
    if (isCollapsed) {
      inline = [moveToken(v, true, false)];
    } else {
      const built = buildChain(v, true, false, false);
      inline = built.inline;
      subBlocks = built.subBlocks;
    }

    return (
      <div className="vt-block" key={"var-" + v.id}>
        <div className="vt-line vt-varline">
          {hasMore ? (
            <button
              className="vt-toggle"
              onClick={(e) => {
                e.stopPropagation();
                toggle(v.id);
              }}
              title={isCollapsed ? "Show this line" : "Hide this line"}
              aria-label={isCollapsed ? "Show this line" : "Hide this line"}
            >
              {isCollapsed ? "+" : "\u2212"}
            </button>
          ) : (
            <span className="vt-toggle-spacer" />
          )}
          <span className="vt-branch" aria-hidden="true">
            ↳
          </span>
          {inline}
          {isCollapsed && hasMore ? (
            <span className="vt-ellipsis">…</span>
          ) : null}
        </div>
        {subBlocks.length ? <div className="vt-subs">{subBlocks}</div> : null}
      </div>
    );
  }

  let mainLine = null;
  if (hasContent) {
    const { inline, subBlocks } = buildChain(root, false, true, true);
    mainLine = (
      <div className="vt-tree">
        <div className="vt-line vt-mainline">
          <span
            className={
              "vt-move vt-start" + (root.id === selectedId ? " selected" : "")
            }
            onClick={() => onSelect(root)}
            title="The starting position — click to view it on the board"
          >
            Start
          </span>{" "}
          {inline}
        </div>
        {subBlocks.length ? <div className="vt-subs">{subBlocks}</div> : null}
      </div>
    );
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
          mainLine
        )}
      </div>
      <div className="footer-note">
        Bold = main line · Blue = game moves · Indented ↳ lines = variations ·
        +/− folds a branch · Click a move to view it
      </div>
    </div>
  );
}
