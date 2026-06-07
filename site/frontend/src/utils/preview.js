/**
 * Monta o documento HTML isolado para o preview de um componente dentro de um
 * <iframe sandbox>. Há dois modos:
 *
 *  - HTML/CSS (Uiverse, HyperUI, DaisyUI): injeta o markup direto, com Tailwind CDN.
 *  - React/JSX (shadcn, Magic UI, Aceternity, React Bits, 21st, Origin): compila o
 *    código com Babel standalone no navegador, resolvendo os imports comuns com
 *    stubs, e auto-renderiza o componente exportado.
 *
 * Quando o React não puder ser renderizado com segurança, o iframe mostra uma
 * mensagem clara — o usuário ainda tem a aba "Código".
 */

const TAILWIND_CDN = "https://cdn.tailwindcss.com";
const REACT_CDN = "https://unpkg.com/react@18/umd/react.development.js";
const REACT_DOM_CDN = "https://unpkg.com/react-dom@18/umd/react-dom.development.js";
const BABEL_CDN = "https://unpkg.com/@babel/standalone/babel.min.js";
const MOTION_CDN = "https://unpkg.com/framer-motion@10/dist/framer-motion.js";

/** Frameworks cujo conteúdo é HTML puro e pode ir direto no body. */
export function isHtmlFramework(framework = "") {
  const f = framework.toLowerCase();
  return f.includes("html") || (f.includes("css") && !f.includes("react"));
}

export function isReactFramework(framework = "") {
  return framework.toLowerCase().includes("react");
}

const DAISYUI_CDN = "https://cdn.jsdelivr.net/npm/daisyui@4/dist/full.min.css";

/** Documento para componentes HTML/CSS (markup + <style> embutido). */
function buildHtmlDoc(html, withDaisyUI = false) {
  // DaisyUI precisa do seu próprio CSS além do Tailwind para as classes (btn, alert…).
  const daisy = withDaisyUI ? `<link rel="stylesheet" href="${DAISYUI_CDN}" />` : "";
  return `<!doctype html>
<html class="dark" data-theme="dark">
  <head>
    <meta charset="utf-8" />
    ${daisy}
    <script src="${TAILWIND_CDN}"></script>
    <style>
      body { margin:0; min-height:100vh; display:flex; align-items:center;
             justify-content:center; padding:32px; background:#18181b; }
    </style>
  </head>
  <body>${html}</body>
</html>`;
}

/**
 * Transforma o código React coletado em algo executável no navegador:
 *  - remove imports (resolvidos por stubs globais)
 *  - remove anotações de tipo TS triviais que o preset react não cobre
 *  - detecta o nome do componente exportado para auto-renderizar
 */
function prepareReactSource(code) {
  let src = code;

  // Descobre o nome do componente exportado antes de remover os exports
  const exportNames = [];
  const namedExport = /export\s+(?:const|function|class)\s+([A-Z][A-Za-z0-9_]*)/g;
  let m;
  while ((m = namedExport.exec(src))) exportNames.push(m[1]);
  const defaultExport = /export\s+default\s+(?:function\s+)?([A-Z][A-Za-z0-9_]*)/.exec(src);
  if (defaultExport) exportNames.unshift(defaultExport[1]);

  // O preset typescript do Babel remove interface/type; aqui só tiramos
  // imports e neutralizamos os exports (sem mexer no corpo do código).
  src = stripImportsExports(src);
  const target = exportNames.find((n) => /^[A-Z]/.test(n)) || "__default__";
  return { src, target };
}

/**
 * Remove imports e exports, preservando as declarações.
 * Não tenta apagar tipos TS — isso fica a cargo do preset typescript do Babel,
 * que faz isso corretamente sem o risco de regex gulosa apagar código.
 */
function stripImportsExports(code) {
  return code
    .replace(/^\s*["']use client["'];?\s*$/gm, "")
    // import { ... } from "x"  /  import X from "x"  (inclui multilinha)
    .replace(/^\s*import\s+[\s\S]*?\s+from\s+["'][^"']*["'];?/gm, "")
    // import "x"  (efeito colateral)
    .replace(/^\s*import\s+["'][^"']*["'];?/gm, "")
    .replace(/export\s+default\s+function\s+([A-Za-z0-9_]+)/g, "function $1")
    .replace(/export\s+default\s+/g, "const __default__ = ")
    .replace(/export\s+(const|function|class|interface|type|enum)\s+/g, "$1 ");
}

/**
 * Stubs dos imports comuns para o código rodar sem resolver módulos:
 * - cn/clsx/twMerge: junta classes
 * - cva: variantes (no-op)
 * - motion/AnimatePresence: do framer-motion via CDN, com fallback a tags simples
 * - useTheme: tema fixo "dark"
 * - Card/Button/Input/Label e afins: stubs genéricos com classes Tailwind, para os
 *   demos do ecossistema shadcn que importam esses primitivos de @/components/ui
 */
function reactRuntime() {
  return `
    // Hooks/utilitários do React expostos no escopo (os imports foram removidos)
    const { useState, useEffect, useRef, useMemo, useCallback, useContext,
            useLayoutEffect, useReducer, useId, forwardRef, createContext,
            Fragment, useImperativeHandle } = React;
    const cn = (...a) => a.flat(Infinity).filter(Boolean).join(" ");
    const clsx = cn, twMerge = cn;
    const cva = () => () => "";
    const useTheme = () => ({ theme: "dark", setTheme: () => {} });
    const FM = window.FramerMotion || {};
    const motion = FM.motion || new Proxy({}, { get: (_, tag) => (p) => React.createElement(tag, p, p.children) });
    const AnimatePresence = FM.AnimatePresence || (({ children }) => children);
    // Hooks de motion-value usados por alguns componentes (magic-card etc.)
    const useMotionValue = FM.useMotionValue || ((v) => ({ get: () => v, set: () => {}, on: () => () => {} }));
    const useMotionTemplate = FM.useMotionTemplate || (() => "");
    const useTransform = FM.useTransform || (() => useMotionValue(0));
    const useSpring = FM.useSpring || ((v) => v);
    const useInView = FM.useInView || (() => true);
    // Primitivos genéricos (shadcn-like) para os demos
    const _box = (cls) => ({ className = "", children, ...p }) =>
      React.createElement("div", { className: cn(cls, className), ...p }, children);
    const Card = _box("rounded-xl border border-white/10 bg-zinc-900 text-zinc-100");
    const CardHeader = _box("p-4");
    const CardContent = _box("p-4");
    const CardFooter = _box("p-4");
    const CardTitle = ({ children, className = "" }) =>
      React.createElement("h3", { className: cn("font-semibold", className) }, children);
    const CardDescription = ({ children, className = "" }) =>
      React.createElement("p", { className: cn("text-sm text-zinc-400", className) }, children);
    const Button = ({ className = "", children, ...p }) =>
      React.createElement("button", { className: cn("inline-flex items-center justify-center rounded-md bg-purple-600 px-4 py-2 text-sm text-white", className), ...p }, children);
    const Input = ({ className = "", ...p }) =>
      React.createElement("input", { className: cn("w-full rounded-md border border-white/10 bg-zinc-800 px-3 py-2 text-sm", className), ...p });
    const Label = ({ className = "", children, ...p }) =>
      React.createElement("label", { className: cn("text-sm text-zinc-300", className), ...p }, children);
  `;
}

/** Snippet que renderiza o alvo, com fallback claro em caso de erro. */
function renderSnippet(target, withChildren) {
  const childrenArg = withChildren ? ', "Exemplo"' : "";
  return `
    (function () {
      try {
        const Comp = ${target};
        if (typeof Comp !== "function" && typeof Comp !== "object")
          throw new Error("nada para renderizar");
        ReactDOM.createRoot(document.getElementById("root"))
          .render(React.createElement(Comp, {}${childrenArg}));
      } catch (err) {
        document.getElementById("root").innerHTML =
          '<div style="color:#a1a1aa;font-family:sans-serif;text-align:center;max-width:340px">' +
          '<p style="font-size:14px">Não foi possível renderizar este componente React automaticamente.</p>' +
          '<p style="font-size:12px;color:#71717a">Veja a aba <b>Código</b> para o código-fonte completo.</p>' +
          '</div>';
      }
    })();
  `;
}

/**
 * Casca HTML do iframe React. Em vez do auto-transform via type="text/babel"
 * (que não ativa o preset TypeScript de forma confiável), compilamos o código
 * explicitamente com Babel.transform usando filename .tsx — isso remove os
 * tipos (interface/type/anotações) corretamente antes de executar.
 * O código vai num <script type="application/json"> para não ser interpretado
 * como JS cru pelo navegador.
 */
function reactHtml(body) {
  const payload = JSON.stringify(body);
  return `<!doctype html>
<html class="dark">
  <head>
    <meta charset="utf-8" />
    <script src="${TAILWIND_CDN}"></script>
    <script src="${REACT_CDN}"></script>
    <script src="${REACT_DOM_CDN}"></script>
    <script src="${MOTION_CDN}"></script>
    <script src="${BABEL_CDN}"></script>
    <style>
      body { margin:0; min-height:100vh; display:flex; align-items:center;
             justify-content:center; padding:32px; background:#18181b; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script>
      (function () {
        var source = ${payload};
        try {
          var out = Babel.transform(source, {
            presets: ["react", "typescript"],
            filename: "component.tsx",
          }).code;
          (0, eval)(out);
        } catch (err) {
          document.getElementById("root").innerHTML =
            '<div style="color:#a1a1aa;font-family:sans-serif;text-align:center;max-width:340px">' +
            '<p style="font-size:14px">N\\u00e3o foi poss\\u00edvel renderizar este componente React automaticamente.</p>' +
            '<p style="font-size:12px;color:#71717a">Veja a aba <b>C\\u00f3digo</b> para o c\\u00f3digo-fonte completo.</p>' +
            '</div>';
        }
      })();
    </script>
  </body>
</html>`;
}

/**
 * Documento React usando o DEMO como instância de uso.
 * Concatena o código do componente + o demo (que o instancia) e renderiza o demo.
 */
function buildReactDocWithDemo(componentCode, demoCode) {
  const comp = stripImportsExports(componentCode);
  const demoName = /export\s+default\s+function\s+([A-Za-z0-9_]+)/.exec(demoCode);
  const demo = stripImportsExports(demoCode);
  const target = demoName ? demoName[1] : "__default__";
  return reactHtml(`${reactRuntime()}\n${comp}\n${demo}\n${renderSnippet(target, false)}`);
}

/** Documento para componentes React sem demo (auto-render do export). */
function buildReactDoc(code) {
  const { src, target } = prepareReactSource(code);
  return reactHtml(`${reactRuntime()}\n${src}\n${renderSnippet(target, true)}`);
}

/**
 * Decide o tipo de preview a partir do componente e dos arquivos coletados.
 * Retorna { kind: 'html'|'react'|'none', doc } — doc é o srcDoc do iframe.
 */
export function buildPreview(component, files = []) {
  const list = Array.isArray(files) ? files : [];
  // Para HTML, prioriza o arquivo .html; para React, o primeiro arquivo de código.
  const htmlFile = list.find((f) => (f.path || "").endsWith(".html") || f.type === "html");
  const codeFile = list[0];

  if (isHtmlFramework(component.framework)) {
    const html = htmlFile?.content || codeFile?.content;
    if (!html) return { kind: "none", doc: "" };
    const isDaisy = component.source_slug === "daisyui";
    return { kind: "html", doc: buildHtmlDoc(html, isDaisy) };
  }
  if (isReactFramework(component.framework)) {
    const code = codeFile?.content;
    if (!code) return { kind: "none", doc: "" };
    // Com demo: renderiza a instância de uso (muito mais fiel). Sem: auto-render.
    if (component.demo_code) {
      return { kind: "react", doc: buildReactDocWithDemo(code, component.demo_code) };
    }
    return { kind: "react", doc: buildReactDoc(code) };
  }
  return { kind: "none", doc: "" };
}
