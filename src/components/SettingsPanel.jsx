import React, { useEffect, useState } from "react";

function formatNum(v, decimals) {
  return decimals > 0 ? Number(v).toFixed(decimals) : String(v);
}

// A labelled control: a single text box you can type any sensible value into.
// Values are only clamped by a genuine lower bound and, where one exists, a real
// engine limit (hash/threads) — there is no artificial upper cap. Blank or
// invalid entries fall back to the previous value on commit (blur / Enter).
function Field({
  label,
  value,
  min,
  max,
  step,
  onChange,
  suffix,
  disabled,
  tip,
  decimals = 0,
}) {
  const [text, setText] = useState(() => formatNum(value, decimals));

  // Keep the box in step with the value coming from outside (e.g. a reset or an
  // engine-cap clamp) — but not while the user is mid-edit (committed on blur).
  useEffect(() => {
    setText(formatNum(value, decimals));
  }, [value, decimals]);

  function commit() {
    let v = Number(text);
    if (text.trim() === "" || !Number.isFinite(v)) {
      setText(formatNum(value, decimals));
      return;
    }
    if (min != null) v = Math.max(min, v);
    if (max != null) v = Math.min(max, v);
    if (decimals > 0) {
      const f = 10 ** decimals;
      v = Math.round(v * f) / f;
    } else {
      v = Math.round(v);
    }
    onChange(v);
    setText(formatNum(v, decimals));
  }

  return (
    <div className="field">
      <div className="field-top">
        <label title={tip}>{label}</label>
        <span className="num-edit-wrap">
          <input
            className="num-edit"
            type="number"
            min={min}
            max={max}
            step={step || 1}
            value={text}
            disabled={disabled}
            onChange={(e) => setText(e.target.value)}
            onBlur={commit}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                commit();
                e.currentTarget.blur();
              }
            }}
            title={tip}
          />
          {suffix ? <span className="num-suffix">{suffix}</span> : null}
        </span>
      </div>
    </div>
  );
}

export default function SettingsPanel({
  settings,
  onChange,
  disabled,
  maxThreads = 1,
  maxHash = 1024,
  localEngine = false,
}) {
  const set = (key) => (val) => onChange({ ...settings, [key]: val });
  const hashCap = Math.max(16, maxHash);
  const threadsCap = Math.max(1, maxThreads);
  const threadsLocked = maxThreads <= 1;
  const hashVal = Math.min(settings.hashMb ?? 64, hashCap);
  const threadsVal = Math.min(settings.threads ?? 1, threadsCap);
  const timeSec = (settings.moveTimeMs ?? 1500) / 1000;

  return (
    <div className="card" style={{ opacity: disabled ? 0.6 : 1 }}>
      <h2>Analysis Settings</h2>

      <Field
        label="Max depth (half-moves)"
        value={settings.maxDepth}
        min={1}
        onChange={set("maxDepth")}
        tip="How many moves deep the tree goes. One half-move is a single move by one player. Higher = deeper tree but slower. Type any whole number."
      />
      <Field
        label="Time per position"
        value={timeSec}
        min={0.1}
        step={0.1}
        decimals={1}
        suffix="s"
        onChange={(sec) =>
          onChange({ ...settings, moveTimeMs: Math.round(sec * 1000) })
        }
        tip="How long the engine thinks about each position, in seconds. More time = stronger moves but slower. Type any value (at least 0.1 s)."
      />

      <div className="field-row">
        <Field
          label="White moves"
          value={settings.whiteMoves}
          min={1}
          onChange={set("whiteMoves")}
          tip="How many candidate moves to keep for White at each position (e.g. 3 = explore White's top 3 moves). Type any whole number."
        />
        <Field
          label="Black moves"
          value={settings.blackMoves}
          min={1}
          onChange={set("blackMoves")}
          tip="How many candidate moves to keep for Black at each position (e.g. 3 = explore Black's top 3 moves). Type any whole number."
        />
      </div>

      <div className="field-row">
        <Field
          label="White threshold"
          value={settings.whiteThreshold}
          min={1}
          step={10}
          suffix="cp"
          onChange={set("whiteThreshold")}
          tip="Quality filter for White's moves, in centipawns (100 cp = one pawn). Keep a move only if it's within this much of White's best move. Smaller = stricter. Type any value."
        />
        <Field
          label="Black threshold"
          value={settings.blackThreshold}
          min={1}
          step={10}
          suffix="cp"
          onChange={set("blackThreshold")}
          tip="Quality filter for Black's moves, in centipawns (100 cp = one pawn). Keep a move only if it's within this much of Black's best move. Smaller = stricter. Type any value."
        />
      </div>

      <div className="field-row">
        <Field
          label="Engine hash"
          value={hashVal}
          min={16}
          max={hashCap}
          step={16}
          suffix="MB"
          onChange={set("hashMb")}
          tip="How much memory (MB) the engine may use to remember positions it has already worked out. Capped at what this engine/computer can spare. The default is fine for most uses."
        />
        <Field
          label="Engine threads"
          value={threadsVal}
          min={1}
          max={threadsCap}
          onChange={set("threads")}
          disabled={threadsLocked}
          tip={
            threadsLocked
              ? "How many CPU cores the engine uses. The built-in browser build runs single-threaded, so it is fixed at 1."
              : "How many CPU cores the engine uses. More cores = faster, stronger analysis. Capped at the cores this engine/computer reports."
          }
        />
      </div>
      {threadsLocked && (
        <p className="muted" style={{ marginTop: -4 }}>
          {localEngine
            ? "This engine reports a single usable core."
            : "The built-in browser engine runs single-threaded. To use more cores, connect your own engine in the Engine panel above."}
        </p>
      )}
    </div>
  );
}
