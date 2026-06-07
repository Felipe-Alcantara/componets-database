import { cx } from "../../utils/cx";

export function Input({ className = "", ...props }) {
  return (
    <input
      className={cx(
        "w-full h-10 rounded-xl bg-zinc-800/50 border border-white/10 px-3 text-sm",
        "text-white outline-none placeholder:text-zinc-400 input-glowing-border",
        className
      )}
      {...props}
    />
  );
}
