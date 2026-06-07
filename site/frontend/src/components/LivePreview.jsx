import { useEffect, useMemo, useRef, useState } from "react";
import { buildPreview, PREVIEW_BACKGROUNDS } from "../utils/preview";

/**
 * Mini-preview ao vivo de um componente, renderizado num iframe.
 * Só busca os dados quando entra na viewport (lazy-load); ao trocar a cor de
 * fundo (bg), reconstrói o doc sem refazer a requisição.
 */
export function LivePreview({ externalId, className = "", bg = "light" }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  const [data, setData] = useState(null);
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

  // Busca os dados quando visível
  useEffect(() => {
    if (!visible || state !== "idle") return;
    setState("loading");
    fetch(`/api/components/${encodeURIComponent(externalId)}/preview`)
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        setState("data");
      })
      .catch(() => setState("empty"));
  }, [visible, externalId, state]);

  // Reconstrói o doc quando há dados ou quando o bg muda (sem refetch)
  const result = useMemo(() => {
    if (!data) return null;
    return buildPreview(data, data.files || [], bg);
  }, [data, bg]);

  const bgStyle = { background: PREVIEW_BACKGROUNDS[bg] || PREVIEW_BACKGROUNDS.light };
  const ready = result && result.kind !== "none";

  return (
    <div ref={ref} className={className} style={{ pointerEvents: "none" }}>
      {ready ? (
        <iframe
          title="mini-preview"
          sandbox="allow-scripts"
          srcDoc={result.doc}
          loading="lazy"
          className="w-full h-full border-0"
          style={bgStyle}
          scrolling="no"
        />
      ) : (
        <div
          className="w-full h-full flex items-center justify-center text-[11px] text-zinc-400"
          style={bgStyle}
        >
          {state === "loading" || state === "idle" ? "" : "sem preview"}
        </div>
      )}
    </div>
  );
}
