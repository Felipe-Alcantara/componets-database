import { motion } from "framer-motion";
import { LivePreview } from "./LivePreview";
import { cx, frameworkColor } from "../utils/cx";

/**
 * Card de um componente no grid, no padrão de galeria (Uiverse/21st):
 * preview grande em cima, informação compacta embaixo.
 */
export function ComponentCard({ component, onOpen }) {
  const { external_id, name, title, source_name, framework, canonical_category } =
    component;

  return (
    <motion.button
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      onClick={() => onOpen(component)}
      className="group text-left rounded-2xl border border-white/10 bg-zinc-950/40 overflow-hidden hover:border-purple-500/40 transition"
    >
      {/* Preview ao vivo (fundo claro, ocupa a maior parte do card) */}
      <div className="aspect-[4/3] bg-zinc-100 overflow-hidden">
        <LivePreview externalId={external_id} className="w-full h-full" />
      </div>

      {/* Info compacta */}
      <div className="px-3 py-2.5 flex items-center justify-between gap-2 border-t border-white/5">
        <div className="min-w-0">
          <h3 className="text-sm font-medium text-zinc-100 truncate">
            {title || name}
          </h3>
          <p className="text-[11px] text-zinc-500 truncate">
            {source_name} · {canonical_category}
          </p>
        </div>
        <span
          className={cx(
            "shrink-0 inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium border",
            frameworkColor(framework)
          )}
        >
          {framework.split(/[\s(]/)[0]}
        </span>
      </div>
    </motion.button>
  );
}
