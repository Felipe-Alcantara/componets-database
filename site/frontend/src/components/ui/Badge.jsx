import { cx } from "../../utils/cx";

export function Badge({ className = "", active = false, children, ...props }) {
  return (
    <span
      className={cx(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium border",
        active
          ? "bg-purple-500/20 text-purple-200 border-purple-500/40"
          : "bg-white/5 text-zinc-300 border-white/10",
        props.onClick && "cursor-pointer hover:border-white/20 transition",
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
