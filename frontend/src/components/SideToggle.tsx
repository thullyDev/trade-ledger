type SideChoice = "" | "1" | "2";

type Props = {
  value: SideChoice;
  onChange: (v: SideChoice) => void;
};

export function SideToggle({ value, onChange }: Props) {
  return (
    <fieldset className="side-toggle">
      <legend>Buy / sell — you must choose one</legend>
      <div className="side-buttons">
        <button
          type="button"
          className={value === "1" ? "side-btn buy active" : "side-btn buy"}
          aria-pressed={value === "1"}
          onClick={() => onChange("1")}
        >
          Buy
        </button>
        <button
          type="button"
          className={value === "2" ? "side-btn sell active" : "side-btn sell"}
          aria-pressed={value === "2"}
          onClick={() => onChange("2")}
        >
          Sell
        </button>
      </div>
      {!value && <p className="hint">No side selected yet</p>}
    </fieldset>
  );
}