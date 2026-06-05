import React from "react";

function Slider({ label, value, min, max, step, onChange, suffix, disabled, tip }) {
  return (
    <div className="field">
      <label title={tip}>{label}</label>
      <div className="num-input">
        <input
          type="range"
          min={min}
          max={max}
          step={step || 1}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(Number(e.target.value))}
          title={tip}
        />
        <span className="val">
          {value}
          {suffix || ""}
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
  const hashCap = Math.min(maxHash, 1024);
  const threadsLocked = maxThreads <= 1;
  const hashVal = Math.min(settings.hashMb ?? 64, hashCap);
  const threadsVal = Math.min(settings.threads ?? 1, Math.max(1, maxThreads));

  return (
    <div className="card" style={{ opacity: disabled ? 0.6 : 1 }}>
      <h2>Analysis Settings</h2>

      <Slider
        label="Max depth (half-moves)"
        value={settings.maxDepth}
        min={1}
        max={12}
        onChange={set("maxDepth")}
        tip="How many moves deep the tree goes. One half-move is a single move by one player. Higher = deeper tree but slower."
      />
      <Slider
        label="Time per position"
        value={settings.moveTimeMs}
        min={200}
        max={5000}
        step={100}
        suffix=" ms"
        onChange={set("moveTimeMs")}
        tip="How long the engine thinks about each position, in milliseconds (1000 ms = 1 second). More time = stronger moves but slower."
      />

      <div className="field-row">
        <Slider
          label="White moves"
          value={settings.whiteMoves}
          min={1}
          max={5}
          onChange={set("whiteMoves")}
          tip="How many candidate moves to keep for White at each position (e.g. 3 = explore White's top 3 moves)."
        />
        <Slider
          label="Black moves"
          value={settings.blackMoves}
          min={1}
          max={5}
          onChange={set("blackMoves")}
          tip="How many candidate moves to keep for Black at each position (e.g. 3 = explore Black's top 3 moves)."
        />
      </div>

      <div className="field-row">
        <Slider
          label="White threshold"
          value={settings.whiteThreshold}
          min={10}
          max={300}
          step={10}
          suffix=" cp"
          onChange={set("whiteThreshold")}
          tip="Quality filter for White's moves, in centipawns (100 cp = one pawn). Keep a move only if it's within this much of White's best move. Smaller = stricter."
        />
        <Slider
          label="Black threshold"
          value={settings.blackThreshold}
          min={10}
          max={300}
          step={10}
          suffix=" cp"
          onChange={set("blackThreshold")}
          tip="Quality filter for Black's moves, in centipawns (100 cp = one pawn). Keep a move only if it's within this much of Black's best move. Smaller = stricter."
        />
      </div>

      <div className="field-row">
        <Slider
          label="Engine hash"
          value={hashVal}
          min={16}
          max={hashCap}
          step={16}
          suffix=" MB"
          onChange={set("hashMb")}
          tip="How much memory (MB) the engine may use to remember positions it has already worked out. The default is fine for most uses."
        />
        <Slider
          label="Engine threads"
          value={threadsVal}
          min={1}
          max={Math.max(1, maxThreads)}
          onChange={set("threads")}
          disabled={threadsLocked}
          tip={
            threadsLocked
              ? "How many CPU cores the engine uses. The built-in browser build runs single-threaded, so it is fixed at 1."
              : "How many CPU cores the engine uses. More cores = faster, stronger analysis."
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
