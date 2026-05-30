import React from "react";

function Slider({ label, value, min, max, step, onChange, suffix }) {
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

export default function SettingsPanel({ settings, onChange, disabled }) {
  const set = (key) => (val) => onChange({ ...settings, [key]: val });

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
    </div>
  );
}
