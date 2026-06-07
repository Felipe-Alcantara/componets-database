import { useEffect, useMemo, useRef, useState } from "react";
import { Search, Loader2, SlidersHorizontal, Shuffle } from "lucide-react";
import { BackgroundParticles } from "./components/BackgroundParticles";
import { FilterSidebar } from "./components/FilterSidebar";
import { ComponentCard } from "./components/ComponentCard";
import { ComponentModal } from "./components/ComponentModal";
import { Input } from "./components/ui/Input";
import { Button } from "./components/ui/Button";
import { fetchFilters, fetchComponents } from "./api";

const EMPTY_FILTERS = { q: "", source: "", framework: "", category: "", tag: "" };

export default function App() {
  const [filters, setFilters] = useState(null);
  const [active, setActive] = useState(EMPTY_FILTERS);
  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  // Ordenação: aleatória por padrão (como Uiverse). seed muda ao embaralhar.
  const [sort, setSort] = useState("random");
  const [seed, setSeed] = useState(() => Math.floor(Math.random() * 100000) + 1);
  const debounce = useRef(null);

  // Carrega as opções de filtro uma vez
  useEffect(() => {
    fetchFilters().then(setFilters).catch((e) => setError(e.message));
  }, []);

  // Busca componentes sempre que filtros, página ou ordenação mudam
  useEffect(() => {
    setLoading(true);
    clearTimeout(debounce.current);
    debounce.current = setTimeout(() => {
      fetchComponents({ ...active, sort, seed, page, per_page: 24 })
        .then((d) => {
          setData(d);
          setError("");
        })
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(debounce.current);
  }, [active, page, sort, seed]);

  const shuffle = () => {
    setSort("random");
    setSeed(Math.floor(Math.random() * 100000) + 1);
    setPage(1);
  };

  const updateFilter = (patch) => {
    setActive((prev) => ({ ...prev, ...patch }));
    setPage(1);
  };

  const clearAll = () => {
    setActive(EMPTY_FILTERS);
    setPage(1);
  };

  const activeCount = useMemo(
    () => Object.entries(active).filter(([k, v]) => k !== "q" && v).length,
    [active]
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-zinc-950 to-black text-zinc-50">
      <BackgroundParticles />

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-10">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold">
            <span className="text-felixo-purple-glow">Felixo UI Index</span>
          </h1>
          <p className="mt-3 text-zinc-400 max-w-2xl mx-auto">
            Biblioteca pesquisável de componentes de UI open source, reunidos de{" "}
            {filters?.sources?.length || 10} fontes da comunidade.
          </p>
          {data && (
            <p className="mt-1 text-sm text-zinc-500">
              {data.total.toLocaleString("pt-BR")} componentes encontrados
            </p>
          )}
        </header>

        {/* Busca */}
        <div className="max-w-2xl mx-auto mb-6 flex gap-2">
          <div className="relative flex-1">
            <Search
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400"
            />
            <Input
              className="pl-9"
              placeholder="Buscar por nome, título ou descrição…"
              value={active.q}
              onChange={(e) => updateFilter({ q: e.target.value })}
            />
          </div>
          {/* Ordenação */}
          <select
            value={sort}
            onChange={(e) => {
              setSort(e.target.value);
              setPage(1);
            }}
            className="h-10 rounded-xl bg-zinc-800/50 border border-white/10 px-3 text-sm text-zinc-200 outline-none"
            aria-label="Ordenar"
          >
            <option value="random">Aleatório</option>
            <option value="smart">Recomendado</option>
            <option value="name">Nome (A-Z)</option>
          </select>
          {sort === "random" && (
            <Button variant="outline" onClick={shuffle} title="Embaralhar">
              <Shuffle size={16} />
            </Button>
          )}
          <Button
            variant="outline"
            onClick={() => setShowFilters((s) => !s)}
            className="lg:hidden"
          >
            <SlidersHorizontal size={16} />
            {activeCount > 0 && <span>{activeCount}</span>}
          </Button>
        </div>

        <div className="grid lg:grid-cols-[260px_1fr] gap-8">
          {/* Sidebar de filtros */}
          <div className={showFilters ? "block" : "hidden lg:block"}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-zinc-300">Filtros</h3>
              {activeCount > 0 && (
                <button
                  onClick={clearAll}
                  className="text-xs text-purple-400 hover:text-purple-300"
                >
                  Limpar ({activeCount})
                </button>
              )}
            </div>
            <FilterSidebar filters={filters} active={active} onChange={updateFilter} />
          </div>

          {/* Grid de componentes */}
          <main>
            {error && (
              <div className="rounded-xl border border-red-500/30 bg-red-950/30 p-4 text-red-300 text-sm">
                {error}
              </div>
            )}

            {loading && !data && (
              <div className="flex items-center justify-center py-20 text-zinc-400">
                <Loader2 className="animate-spin mr-2" size={20} /> Carregando…
              </div>
            )}

            {data && data.items.length === 0 && !loading && (
              <div className="text-center py-20 text-zinc-400">
                Nenhum componente encontrado. Tente outros filtros.
              </div>
            )}

            {data && data.items.length > 0 && (
              <>
                <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
                  {data.items.map((c) => (
                    <ComponentCard
                      key={c.external_id}
                      component={c}
                      onOpen={setSelected}
                    />
                  ))}
                </div>

                {/* Paginação */}
                {data.pages > 1 && (
                  <div className="flex items-center justify-center gap-3 mt-8">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page <= 1}
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                    >
                      Anterior
                    </Button>
                    <span className="text-sm text-zinc-400">
                      Página {data.page} de {data.pages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page >= data.pages}
                      onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                    >
                      Próxima
                    </Button>
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </div>

      {selected && (
        <ComponentModal component={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
}
