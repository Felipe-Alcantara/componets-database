import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, ExternalLink, Copy, Check, Eye, Code2 } from "lucide-react";
import { Badge } from "./ui/Badge";
import { Button } from "./ui/Button";
import { cx, frameworkColor, licenseColor } from "../utils/cx";
import { buildPreview } from "../utils/preview";
import { fetchComponent } from "../api";

export function ComponentModal({ component, onClose, bg = "light" }) {
  const [detail, setDetail] = useState(null);
  const [tab, setTab] = useState("preview");
  const [activeFile, setActiveFile] = useState(0);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setDetail(null);
    setError("");
    setActiveFile(0);
    fetchComponent(component.external_id)
      .then(setDetail)
      .catch((e) => setError(e.message));
  }, [component.external_id]);

  // Fecha com ESC
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const files = detail?.files || [];
  const hasCode = files.length > 0;
  // Tenta montar o preview (HTML direto ou React via Babel). kind: html|react|none
  const preview = detail ? buildPreview(detail, files, bg) : { kind: "none" };
  const previewable = preview.kind !== "none";

  // Aba inicial: preview se houver; senão código; senão metadados
  useEffect(() => {
    if (!detail) return;
    if (previewable) setTab("preview");
    else if (hasCode) setTab("code");
    else setTab("info");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [detail]);

  const copyActive = () => {
    const content = files[activeFile]?.content;
    if (!content) return;
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  // Rótulo curto do arquivo: extensão ou nome do arquivo (sem o caminho longo)
  const fileLabel = (f, i) => {
    if (!f?.path) return `arquivo ${i + 1}`;
    const base = f.path.split("/").pop();
    return base || `arquivo ${i + 1}`;
  };

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="felixo-card-glow border border-purple-500/30 rounded-2xl bg-zinc-950 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col"
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-4 p-5 border-b border-white/10">
            <div className="min-w-0">
              <h2 className="text-lg font-bold text-zinc-50 truncate">
                {component.title || component.name}
              </h2>
              <p className="text-xs text-zinc-400 mt-0.5">
                {component.source_name} · {component.canonical_category}
              </p>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose} aria-label="Fechar">
              <X size={18} />
            </Button>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 px-5 pt-3">
            {previewable && (
              <TabButton active={tab === "preview"} onClick={() => setTab("preview")}>
                <Eye size={14} /> Preview
              </TabButton>
            )}
            {hasCode && (
              <TabButton active={tab === "code"} onClick={() => setTab("code")}>
                <Code2 size={14} /> Código
              </TabButton>
            )}
            <TabButton active={tab === "info"} onClick={() => setTab("info")}>
              Detalhes
            </TabButton>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-auto p-5">
            {error && <p className="text-red-400 text-sm">{error}</p>}
            {!detail && !error && (
              <p className="text-zinc-400 text-sm">Carregando…</p>
            )}

            {detail && tab === "preview" && previewable && (
              <div>
                <iframe
                  title="preview"
                  sandbox="allow-scripts"
                  srcDoc={preview.doc}
                  className="w-full h-[420px] rounded-xl border border-white/10"
                />
                {preview.kind === "react" && (
                  <p className="mt-2 text-[11px] text-zinc-500">
                    Preview React compilado no navegador — alguns componentes com
                    dependências específicas podem não renderizar; nesses casos, use a aba Código.
                  </p>
                )}
              </div>
            )}

            {detail && tab === "code" && hasCode && (
              <div>
                <div className="flex items-center justify-between mb-2 gap-2">
                  {/* Seletor de arquivo (só quando há mais de um) */}
                  {files.length > 1 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {files.map((f, i) => (
                        <button
                          key={i}
                          onClick={() => setActiveFile(i)}
                          className={cx(
                            "px-2.5 py-1 text-xs rounded-md font-mono border transition",
                            i === activeFile
                              ? "bg-purple-500/20 text-purple-200 border-purple-500/40"
                              : "bg-white/5 text-zinc-400 border-white/10 hover:text-zinc-200"
                          )}
                        >
                          {fileLabel(f, i)}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <span className="text-xs text-zinc-400 font-mono truncate">
                      {fileLabel(files[0], 0)}
                    </span>
                  )}
                  <Button variant="outline" size="sm" onClick={copyActive}>
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                    {copied ? "Copiado" : "Copiar"}
                  </Button>
                </div>
                <pre className="code-block text-xs text-zinc-200 bg-zinc-900/80 border border-white/10 rounded-xl p-4 overflow-auto max-h-[400px]">
                  {files[activeFile]?.content}
                </pre>
              </div>
            )}

            {detail && tab === "info" && (
              <InfoTab detail={detail} />
            )}
          </div>

          {/* Footer */}
          {detail && (
            <div className="p-4 border-t border-white/10 flex items-center justify-between gap-3">
              <div className="flex flex-wrap gap-1.5">
                {(detail.tags || []).map((t) => (
                  <Badge key={t} active={t === detail.canonical_category}>
                    {t}
                  </Badge>
                ))}
              </div>
              {detail.public_url && (
                <a href={detail.public_url} target="_blank" rel="noreferrer">
                  <Button variant="default" size="sm">
                    Ver na fonte <ExternalLink size={14} />
                  </Button>
                </a>
              )}
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

function TabButton({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={cx(
        "inline-flex items-center gap-1.5 px-3 py-2 text-sm rounded-t-lg border-b-2 transition",
        active
          ? "text-purple-300 border-purple-500"
          : "text-zinc-400 border-transparent hover:text-zinc-200"
      )}
    >
      {children}
    </button>
  );
}

function InfoTab({ detail }) {
  const rows = [
    ["Fonte", detail.source_name],
    ["Framework", detail.framework],
    ["Categoria", detail.canonical_category],
    ["Licença", detail.license],
    ["Demo", detail.is_demo ? "sim" : "não"],
  ];
  return (
    <div className="space-y-4">
      {detail.is_demo === 0 && detail.license && (
        <span
          className={cx(
            "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium border",
            licenseColor(detail.license)
          )}
        >
          {detail.license}
        </span>
      )}
      <dl className="grid grid-cols-[120px_1fr] gap-y-2 text-sm">
        {rows.map(([k, v]) => (
          <div key={k} className="contents">
            <dt className="text-zinc-500">{k}</dt>
            <dd className="text-zinc-200">{v || "—"}</dd>
          </div>
        ))}
      </dl>
      {detail.dependencies?.length > 0 && (
        <div>
          <p className="text-zinc-500 text-sm mb-1.5">Dependências</p>
          <div className="flex flex-wrap gap-1.5">
            {detail.dependencies.map((d) => (
              <Badge key={d.name}>{d.name}</Badge>
            ))}
          </div>
        </div>
      )}
      {!detail.files?.length && (
        <p className="text-xs text-yellow-200/80 bg-yellow-400/5 border border-yellow-400/20 rounded-xl p-3">
          Esta fonte não permite redistribuir o código. Apenas metadados são exibidos —
          use o botão "Ver na fonte" para acessar o componente original.
        </p>
      )}
    </div>
  );
}
