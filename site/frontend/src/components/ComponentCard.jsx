import { motion } from "framer-motion";
import { Card, CardContent, CardFooter } from "./ui/Card";
import { Badge } from "./ui/Badge";
import { cx, frameworkColor } from "../utils/cx";

/** Card de um componente no grid. Clica para abrir o detalhe. */
export function ComponentCard({ component, onOpen }) {
  const { name, title, source_name, framework, canonical_category, tags } = component;

  return (
    <motion.button
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      onClick={() => onOpen(component)}
      className="text-left"
    >
      <Card glow className="h-full cursor-pointer hover:border-white/20">
        <CardContent>
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-base font-semibold text-zinc-50 truncate">
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
          <p className="mt-1 text-xs text-zinc-400">{source_name}</p>

          <div className="mt-3 flex flex-wrap gap-1.5">
            {(tags || []).slice(0, 4).map((t) => (
              <Badge key={t} active={t === canonical_category}>
                {t}
              </Badge>
            ))}
          </div>
        </CardContent>
        <CardFooter className="justify-between">
          <span className="text-[11px] text-zinc-500">Ver detalhes & código</span>
          <span className="text-purple-400 text-sm">→</span>
        </CardFooter>
      </Card>
    </motion.button>
  );
}
