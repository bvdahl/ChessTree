import React from "react";
import { formatEvalDisplay } from "../analysis/evaluation.js";

function evalChipClass(ev) {
  if (!ev) return "eval-white";
  if (ev.isMate) return "eval-mate";
  if ((ev.whiteCp ?? 0) > 20) return "eval-pos";
  if ((ev.whiteCp ?? 0) < -20) return "eval-neg";
  return "eval-white";
}

function moveNumberLabel(node) {
  if (!node.fenBefore) return "";
  const parts = node.fenBefore.split(" ");
  const whiteToMove = parts[1] === "w";
  const num = parseInt(parts[5], 10) || 1;
  return whiteToMove ? `${num}.` : `${num}...`;
}

function TreeNode({ node, selectedId, onSelect }) {
  return (
    <div>
      <div
        className={
          "node-row" + (node.id === selectedId ? " selected" : "")
        }
        onClick={() => onSelect(node)}
        title={
          (node.isGameMove
            ? "Game move — click to view this position on the board"
            : "Suggested move — click to view this position on the board") +
          (node.eval ? " · Evaluation shown from White's point of view" : "")
        }
      >
        <span className="node-num">{moveNumberLabel(node)}</span>
        <span
          className={"node-move" + (node.isGameMove ? " game" : "")}
        >
          {node.move.san}
        </span>
        {node.eval && (
          <span className={"eval-chip " + evalChipClass(node.eval)}>
            {formatEvalDisplay(node.eval)}
          </span>
        )}
      </div>
      {node.children.length > 0 && (
        <div className="tree-children">
          {node.children.map((c) => (
            <TreeNode
              key={c.id}
              node={c}
              selectedId={selectedId}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function VariationTree({ root, selectedId, onSelect }) {
  const hasContent = root && root.children.length > 0;

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
          <>
            <div
              className={
                "node-row" + (root.id === selectedId ? " selected" : "")
              }
              onClick={() => onSelect(root)}
              title="The starting position — click to view it on the board"
            >
              <span className="node-move" style={{ color: "var(--text-dim)" }}>
                Start
              </span>
            </div>
            <div className="tree-children">
              {root.children.map((c) => (
                <TreeNode
                  key={c.id}
                  node={c}
                  selectedId={selectedId}
                  onSelect={onSelect}
                />
              ))}
            </div>
          </>
        )}
      </div>
      <div className="footer-note">
        Blue = game moves · Click any move to view it on the board
      </div>
    </div>
  );
}
