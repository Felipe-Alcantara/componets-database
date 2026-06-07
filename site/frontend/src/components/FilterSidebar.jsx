import { Badge } from "./ui/Badge";

/**
 * Bloco de um grupo de filtros.
 * `valueKey` define o valor enviado ao filtro; `labelKey` o texto exibido.
 * Strings simples (frameworks) usam o próprio valor como label.
 */
function FilterGroup({
  title,
  options,
  selected,
  onSelect,
  labelKey = "name",
  valueKey = "name",
  countKey = "count",
}) {
  return (
    <div className="mb-6">
      <h4 className="text-xs uppercase tracking-wide text-zinc-500 mb-2">{title}</h4>
      <div className="flex flex-wrap gap-1.5">
        {options.map((opt) => {
          const isStr = typeof opt === "string";
          const value = isStr ? opt : opt[valueKey];
          const label = isStr ? opt : opt[labelKey];
          const count = isStr ? null : opt[countKey];
          return (
            <Badge
              key={value}
              active={selected === value}
              onClick={() => onSelect(selected === value ? "" : value)}
            >
              {label}
              {count != null && <span className="ml-1 text-zinc-500">{count}</span>}
            </Badge>
          );
        })}
      </div>
    </div>
  );
}

export function FilterSidebar({ filters, active, onChange }) {
  if (!filters) return null;

  return (
    <aside className="space-y-2">
      <FilterGroup
        title="Categoria"
        options={filters.categories.slice(0, 18)}
        selected={active.category}
        onSelect={(v) => onChange({ category: v, tag: "" })}
      />
      <FilterGroup
        title="Fonte"
        options={filters.sources}
        labelKey="display_name"
        valueKey="slug"
        selected={active.source}
        onSelect={(v) => onChange({ source: v })}
      />
      <FilterGroup
        title="Framework"
        options={filters.frameworks}
        selected={active.framework}
        onSelect={(v) => onChange({ framework: v })}
      />
      <FilterGroup
        title="Tags populares"
        options={filters.tags.slice(0, 20)}
        selected={active.tag}
        onSelect={(v) => onChange({ tag: v, category: "" })}
      />
    </aside>
  );
}
