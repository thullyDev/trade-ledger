import type { ThemeMode } from "../hooks/useTheme";

type Props = {
  mode: ThemeMode;
  isDark: boolean;
  onSetMode: (mode: ThemeMode) => void;
};

export function ThemeToggle({ mode, isDark, onSetMode }: Props) {
  return (
    <div className="theme-toggle" role="group" aria-label="Theme">
      <button
        type="button"
        className={mode === "light" ? "active" : ""}
        onClick={() => onSetMode("light")}
        title="Light — red / black / white"
      >
        Light
      </button>
      <button
        type="button"
        className={mode === "dark" || (mode === "system" && isDark) ? "active" : ""}
        onClick={() => onSetMode("dark")}
        title="Dark — green accent"
      >
        Dark
      </button>
    </div>
  );
}