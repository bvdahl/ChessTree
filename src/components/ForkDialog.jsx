import React, { useEffect } from "react";
import { formatEvalDisplay } from "../analysis/evaluation.js";

function evalClass(ev) {
  if (!ev) return "vt-eval-neutral";
  if (ev.isMate) return "vt-eval-mate";
  if ((ev.whiteCp ?? 0) > 20) return "vt-eval-pos";
  if ((ev.whiteCp ?? 0) < -20) return "vt-eval-neg";
  return "vt-eval-neutral";
}

// Shown when the user steps forward from a position that branches into more
// than one move. Lists each candidate move with its evaluation so the user can
// choose which line to follow.
export default function ForkDialog({ open, moves, onPick, onClose }) {
  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fork-backdrop" onClick={onClose} role="presentation">
      <div
        className="fork-window"
        role="dialog"
        aria-modal="true"
        aria-label="Choose a move"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="fork-head">
          <h3>Choose a move</h3>
          <button
            className="fork-close"
            onClick={onClose}
            aria-label="Cancel"
            title="Cancel (Esc)"
          >
            ✕
          </button>
        </div>
        <p className="fork-sub">
          This position branches. Pick which move to follow.
        </p>
        <ul className="fork-list">
          {(moves || []).map((m) => (
            <li key={m.id}>
              <button
                className="fork-move"
                onClick={() => onPick(m)}
                title="Follow this move"
              >
                <span className="fork-san">{m.move.san}</span>
                {m.eval ? (
                  <span className={"fork-eval " + evalClass(m.eval)}>
                    {formatEvalDisplay(m.eval)}
                  </span>
                ) : (
                  <span className="fork-eval vt-eval-neutral">game</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
