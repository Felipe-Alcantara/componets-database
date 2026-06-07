import { cx } from "../../utils/cx";

export function Card({ className = "", glow = false, children, ...props }) {
  return (
    <div
      className={cx(
        "rounded-3xl border bg-zinc-950/50 border-white/10 transition",
        glow && "hover-felixo-card-glow",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className = "", children }) {
  return <div className={cx("p-5 border-b border-white/5", className)}>{children}</div>;
}

export function CardContent({ className = "", children }) {
  return <div className={cx("p-5", className)}>{children}</div>;
}

export function CardFooter({ className = "", children }) {
  return (
    <div className={cx("p-5 border-t border-white/5 flex items-center gap-3", className)}>
      {children}
    </div>
  );
}

export function CardTitle({ className = "", children }) {
  return <h3 className={cx("text-base font-semibold", className)}>{children}</h3>;
}

export function CardDescription({ className = "", children }) {
  return <p className={cx("text-xs text-zinc-400", className)}>{children}</p>;
}
