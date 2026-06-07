import { motion } from "framer-motion";
import { Card } from "./ui/Card";
import { Badge } from "./ui/Badge";
import { LivePreview } from "./LivePreview";
import { cx, frameworkColor } from "../utils/cx";

/** Card de um componente no grid, com mini-preview ao vivo. */
export function ComponentCard({ component, onOpen }) {
  const { external_id, name, title, source_name, framework, canonical_category, tags } =
    component;

  return (
    <motion.button
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      onClick={() => onOpen(component)}
      className="text-left"
    >
      <Card glow className="h-full cursor-pointer hover:border-white/20 overflow-hidden">
        {/* Mini-preview ao vivo */}
        <div className="h-40 border-b border-white/10 bg-zinc-900/60">
          <LivePreview externalId={external_id} className="w-full h-full" />
        </div>

        {/* Info */}
        <div className="p-4">
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-sm font-semibold text-zinc-50 truncate">
              {title || name}
            </h3>
            <span
              className={cx(
                "shrink-0 inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium border",
                frameworkColor(framework)
              )}
            >
              {framework}
            </span>
          </div>
          <p className="mt-0.5 text-xs text-zinc-400">{source_name}</p>

          <div className="mt-2.5 flex flex-wrap gap-1.5">
            {(tags || []).slice(0, 4).map((t) => (
              <Badge key={t} active={t === canonical_category}>
                {t}
              </Badge>
            ))}
          </div>
        </div>
      </Card>
    </motion.button>
  );
}
