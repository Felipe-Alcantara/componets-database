import { cx } from "../../utils/cx";

const VARIANTS = {
  default: "bg-white text-black border-white/10 hover:bg-zinc-100",
  outline: "bg-transparent text-white border-white/20 hover:bg-white/5",
  ghost: "bg-transparent text-white border-transparent hover:bg-white/5",
  secondary: "bg-zinc-800 text-white border-white/10 hover:bg-zinc-700",
};

const SIZES = {
  md: "h-10 px-4",
  sm: "h-9 px-3",
  icon: "h-10 w-10 p-2",
};

export function Button({
  variant = "default",
  size = "md",
  className = "",
  children,
  ...props
}) {
  return (
    <button
      className={cx(
        "inline-flex items-center justify-center gap-2 rounded-2xl text-sm font-medium",
        "transition shadow-sm border",
        VARIANTS[variant],
        SIZES[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
