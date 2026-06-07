/** Combina classes condicionalmente, removendo valores falsy. */
export function cx(...classes) {
  return classes.filter(Boolean).join(" ");
}

/**
 * Cor de badge por framework/tecnologia (design system Felixo).
 * Retorna classes Tailwind para fundo/texto/borda.
 */
export function frameworkColor(framework = "") {
  const f = framework.toLowerCase();
  if (f.includes("react")) return "bg-cyan-500/10 text-cyan-300 border-cyan-500/20";
  if (f.includes("tailwind")) return "bg-sky-500/10 text-sky-300 border-sky-500/20";
  if (f.includes("html")) return "bg-orange-500/10 text-orange-300 border-orange-500/20";
  if (f.includes("css")) return "bg-blue-500/10 text-blue-300 border-blue-500/20";
  return "bg-zinc-500/10 text-zinc-300 border-zinc-500/20";
}

/** Cor de badge por licença (verde = livre, amarelo = restritiva). */
export function licenseColor(license = "") {
  const l = license.toLowerCase();
  if (l.includes("mit") && !l.includes("commons"))
    return "bg-green-950/60 text-green-300 border-green-700/50";
  if (l.includes("proprietary") || l.includes("custom") || l.includes("commons"))
    return "bg-yellow-400/10 text-yellow-200 border-yellow-400/30";
  return "bg-zinc-500/10 text-zinc-300 border-zinc-500/20";
}
