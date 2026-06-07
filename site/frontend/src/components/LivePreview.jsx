import { useEffect, useRef, useState } from "react";
import { buildPreview } from "../utils/preview";

/**
 * Mini-preview ao vivo de um componente, renderizado num iframe.
 * Só busca os dados e monta o iframe quando entra na viewport (lazy-load),
 * para não carregar dezenas de previews de uma vez.
 */
export function LivePreview({ externalId, className = "" }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  const [doc, setDoc] = useState(null);
  const [state, setState] = useState("idle"); // idle | loading | ready | empty

  // Observa a entrada na viewport
  useEffect(() => {
    const el = ref.current;
    if (!el || visible) return;
    const obs = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setVisible(true);
          obs.disconnect();
        }
      },
      { rootMargin: "200px" }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [visible]);

  // Busca os dados e monta o preview quando visível
  useEffect(() => {
    if (!visible || state !== "idle") return;
    setState("loading");
    fetch(`/api/components/${encodeURIComponent(externalId)}/preview`)
      .then((r) => r.json())
      .then((data) => {
        const p = buildPreview(data, data.files || []);
        if (p.kind === "none") {
          setState("empty");
        } else {
          setDoc(p.doc);
          setState("ready");
        }
      })
      .catch(() => setState("empty"));
  }, [visible, externalId, state]);

  return (
    <div
      ref={ref}
      className={className}
      style={{ pointerEvents: "none" }} // o card todo é clicável; o iframe não intercepta
    >
      {state === "ready" && doc ? (
        <iframe
          title="mini-preview"
          sandbox="allow-scripts"
          srcDoc={doc}
          loading="lazy"
          className="w-full h-full border-0 bg-zinc-900"
          scrolling="no"
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center text-[11px] text-zinc-600">
          {state === "loading" ? "carregando…" : state === "empty" ? "sem preview" : ""}
        </div>
      )}
    </div>
  );
}
