import React from "react";

function Slider({ label, value, min, max, step, onChange, suffix, disabled }) {
  return (
    <div className="field">
      <label>{label}</label>
      <div className="num-input">
        <input
          type="range"
          min={min}
          max={max}
          step={step || 1}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(Number(e.target.value))}
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
      />
      <Slider
        label="Time per position"
        value={settings.moveTimeMs}
        min={200}
        max={5000}
        step={100}
        suffix=" ms"
        onChange={set("moveTimeMs")}
      />

      <div className="field-row">
        <Slider
          label="White moves"
          value={settings.whiteMoves}
          min={1}
          max={5}
          onChange={set("whiteMoves")}
        />
        <Slider
          label="Black moves"
          value={settings.blackMoves}
          min={1}
          max={5}
          onChange={set("blackMoves")}
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
        />
        <Slider
          label="Black threshold"
          value={settings.blackThreshold}
          min={10}
          max={300}
          step={10}
          suffix=" cp"
          onChange={set("blackThreshold")}
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
        />
        <Slider
          label="Engine threads"
          value={threadsVal}
          min={1}
          max={Math.max(1, maxThreads)}
          onChange={set("threads")}
          disabled={threadsLocked}
        />
      </div>
      {threadsLocked && (
        <p className="muted" style={{ marginTop: -4 }}>
          This in-browser engine build runs single-threaded.
        </p>
      )}
    </div>
  );
}
