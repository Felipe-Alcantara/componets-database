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

/** Cores de fundo do preview, selecionáveis pelo usuário. */
export const PREVIEW_BACKGROUNDS = {
  light: "#f4f4f5",
  gray: "#71717a",
  dark: "#18181b",
};

function bgColor(bg) {
  return PREVIEW_BACKGROUNDS[bg] || PREVIEW_BACKGROUNDS.light;
}

/**
 * Auto-ajuste robusto: mede a "caixa" real do conteúdo (bounding box de todos os
 * filhos, cobrindo elementos posicionados/absolutos que estouram) e aplica um
 * scale para o componente caber inteiro e centralizado no iframe.
 */
const FIT_SCRIPT = `
  <script>
    (function () {
      function contentBox(box) {
        // Mede TODOS os descendentes (não só filhos diretos) para capturar
        // pseudo-conteúdo posicionado/absoluto que estoura a caixa do pai.
        var r0 = box.getBoundingClientRect();
        var minL = 0, minT = 0, maxR = box.scrollWidth, maxB = box.scrollHeight;
        var all = box.querySelectorAll("*");
        for (var i = 0; i < all.length; i++) {
          var el = all[i], r = el.getBoundingClientRect();
          if (!r.width && !r.height) continue;
          minL = Math.min(minL, r.left - r0.left);
          minT = Math.min(minT, r.top - r0.top);
          // inclui o scrollWidth/Height do elemento (conteúdo que transborda a
          // própria caixa, como texto maior que um botão de largura fixa)
          maxR = Math.max(maxR, r.left - r0.left + el.scrollWidth, r.right - r0.left);
          maxB = Math.max(maxB, r.top - r0.top + el.scrollHeight, r.bottom - r0.top);
        }
        return { w: maxR - Math.min(0, minL), h: maxB - Math.min(0, minT) };
      }
      function fit() {
        var box = document.getElementById("fit");
        if (!box) return;
        box.style.transform = "none";
        // espaço interno disponível (body já tem padding); folga extra p/ animações
        var cw = document.body.clientWidth - 16, ch = document.body.clientHeight - 16;
        var c = contentBox(box);
        if (!c.w || !c.h) return;
        // fator de segurança: deixa respiro p/ animações/pseudo-elementos que
        // expandem além da medição estática. Nunca amplia além de 1x.
        var s = Math.min(cw / c.w, ch / c.h, 1) * 0.9;
        box.style.transform = "scale(" + s + ")";
      }
      window.addEventListener("load", fit);
      window.addEventListener("resize", fit);
      // imagens podem mudar o tamanho ao carregar
      Array.prototype.forEach.call(document.images, function (im) {
        im.addEventListener("load", fit);
      });
      setTimeout(fit, 150); setTimeout(fit, 600); setTimeout(fit, 1500);
    })();
  </script>
`;

/** Documento para componentes HTML/CSS (markup + <style> embutido). */
function buildHtmlDoc(html, withDaisyUI = false, bg = "light") {
  // DaisyUI precisa do seu próprio CSS além do Tailwind para as classes (btn, alert…).
  const daisy = withDaisyUI ? `<link rel="stylesheet" href="${DAISYUI_CDN}" />` : "";
  return `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    ${daisy}
    <script src="${TAILWIND_CDN}"></script>
    <style>
      html, body { margin:0; width:100%; height:100%; overflow:hidden;
        background:${bgColor(bg)}; }
      body { display:flex; align-items:center; justify-content:center; box-sizing:border-box;
        padding:20px; }
      #fit { transform-origin:center center; display:inline-block; }
      /* neutraliza margin:auto do elemento raiz, que desloca a medição */
      #fit > * { margin-left:0 !important; margin-right:0 !important; }
    </style>
  </head>
  <body><div id="fit">${html}</div>${FIT_SCRIPT}</body>
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
 * Extrai os nomes importados de lucide-react e os liga ao ícone genérico (_Icon),
 * já que removemos os imports. Sem isso, `<ArrowRight />` ficaria indefinido.
 */
function iconBindings(...codes) {
  const names = new Set();
  for (const code of codes) {
    const re = /import\s*\{([^}]+)\}\s*from\s*["']lucide-react["']/g;
    let m;
    while ((m = re.exec(code || ""))) {
      m[1].split(",").forEach((n) => {
        const clean = n.trim().split(/\s+as\s+/).pop().trim();
        if (/^[A-Za-z_$][\w$]*$/.test(clean)) names.add(clean);
      });
    }
  }
  if (!names.size) return "";
  return "const " + [...names].map((n) => `${n} = _Icon`).join(", ") + ";";
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
    const useTheme = () => ({ theme: "light", setTheme: () => {} });
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
    const _box = (cls, tag) => ({ className = "", children, ...p }) =>
      React.createElement(tag || "div", { className: cn(cls, className), ...p }, children);
    const Card = _box("rounded-xl border border-white/10 bg-zinc-900 text-zinc-100");
    const CardHeader = _box("p-4");
    const CardContent = _box("p-4");
    const CardFooter = _box("p-4");
    const CardTitle = _box("font-semibold", "h3");
    const CardDescription = _box("text-sm text-zinc-400", "p");
    const Button = ({ className = "", children, ...p }) =>
      React.createElement("button", { className: cn("inline-flex items-center justify-center gap-2 rounded-md bg-purple-600 px-4 py-2 text-sm text-white", className), ...p }, children);
    const Input = ({ className = "", ...p }) =>
      React.createElement("input", { className: cn("w-full rounded-md border border-white/10 bg-zinc-800 px-3 py-2 text-sm", className), ...p });
    const Label = _box("text-sm text-zinc-300", "label");
    const Badge = _box("inline-flex items-center rounded-full border border-white/10 bg-white/5 px-2.5 py-0.5 text-xs");
    const Separator = _box("my-2 h-px w-full bg-white/10");
    const ScrollArea = _box("overflow-auto");
    const Tooltip = _box(""), TooltipTrigger = _box(""), TooltipContent = _box(""),
          TooltipProvider = ({ children }) => children;
    const Avatar = _box("inline-flex h-10 w-10 overflow-hidden rounded-full bg-zinc-700");
    const AvatarImage = ({ className = "", ...p }) =>
      React.createElement("img", { className: cn("h-full w-full object-cover", className), ...p });
    const AvatarFallback = _box("flex h-full w-full items-center justify-center text-xs");
    // Ícones (lucide-react): qualquer ícone vira um quadradinho SVG genérico
    const _Icon = ({ size = 20, className = "" }) =>
      React.createElement("svg", { width: size, height: size, viewBox: "0 0 24 24",
        fill: "none", stroke: "currentColor", strokeWidth: 2, className },
        React.createElement("rect", { x: 4, y: 4, width: 16, height: 16, rx: 3 }));
    const Icons = new Proxy({}, { get: () => _Icon });
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
          '<div style="color:#52525b;font-family:sans-serif;text-align:center;max-width:340px">' +
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
function reactHtml(body, bg = "light") {
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
      html, body { margin:0; width:100%; height:100%; overflow:hidden; background:${bgColor(bg)}; }
      body { display:flex; align-items:center; justify-content:center; box-sizing:border-box; }
      #fit { transform-origin:center center; display:inline-block; }
    </style>
  </head>
  <body>
    <div id="fit"><div id="root"></div></div>
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
            '<div style="color:#52525b;font-family:sans-serif;text-align:center;max-width:340px">' +
            '<p style="font-size:14px">N\\u00e3o foi poss\\u00edvel renderizar este componente React automaticamente.</p>' +
            '<p style="font-size:12px;color:#71717a">Veja a aba <b>C\\u00f3digo</b> para o c\\u00f3digo-fonte completo.</p>' +
            '</div>';
        }
      })();
    </script>
    ${FIT_SCRIPT}
  </body>
</html>`;
}

/**
 * Documento React usando o DEMO como instância de uso.
 * Concatena o código do componente + o demo (que o instancia) e renderiza o demo.
 */
function buildReactDocWithDemo(componentCode, demoCode, bg = "light") {
  const icons = iconBindings(componentCode, demoCode);
  const comp = stripImportsExports(componentCode);
  const demoName = /export\s+default\s+function\s+([A-Za-z0-9_]+)/.exec(demoCode);
  const demo = stripImportsExports(demoCode);
  const target = demoName ? demoName[1] : "__default__";
  return reactHtml(`${reactRuntime()}\n${icons}\n${comp}\n${demo}\n${renderSnippet(target, false)}`, bg);
}

/** Documento para componentes React sem demo (auto-render do export). */
function buildReactDoc(code, bg = "light") {
  const icons = iconBindings(code);
  const { src, target } = prepareReactSource(code);
  return reactHtml(`${reactRuntime()}\n${icons}\n${src}\n${renderSnippet(target, true)}`, bg);
}

/**
 * Decide o tipo de preview a partir do componente e dos arquivos coletados.
 * Retorna { kind: 'html'|'react'|'none', doc } — doc é o srcDoc do iframe.
 */
export function buildPreview(component, files = [], bg = "light") {
  const list = Array.isArray(files) ? files : [];
  // Arquivo de marcação para preview: .html explícito, NUNCA .css (que renderiza
  // como texto cru). Se a fonte tem só CSS, não há preview.
  const htmlFile = list.find((f) => {
    const path = (f.path || "").toLowerCase();
    if (path.endsWith(".css") || f.type === "css") return false;
    return path.endsWith(".html") || f.type === "html" || /<[a-z][\s\S]*>/i.test(f.content || "");
  });
  const codeFile = list[0];

  if (isHtmlFramework(component.framework)) {
    if (!htmlFile?.content) return { kind: "none", doc: "" };
    const isDaisy = component.source_slug === "daisyui";
    return { kind: "html", doc: buildHtmlDoc(htmlFile.content, isDaisy, bg) };
  }
  if (isReactFramework(component.framework)) {
    const code = codeFile?.content;
    if (!code) return { kind: "none", doc: "" };
    // Com demo: renderiza a instância de uso (muito mais fiel). Sem: auto-render.
    if (component.demo_code) {
      return { kind: "react", doc: buildReactDocWithDemo(code, component.demo_code, bg) };
    }
    return { kind: "react", doc: buildReactDoc(code, bg) };
  }
  return { kind: "none", doc: "" };
}
