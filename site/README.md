# 🖥️ Felixo UI Index — Site

Interface web para navegar, buscar e visualizar os componentes coletados no banco.
Backend em **Flask** (API REST sobre o SQLite) + frontend em **React 18 + Tailwind +
Framer Motion + Vite**, seguindo o design system do Felixo System Design.

## ✨ O que o site faz

- **Grid** de componentes com glow roxo e identidade Felixo (tema escuro, partículas)
- **Busca** por nome, título e descrição (com debounce)
- **Filtros** combináveis: categoria, fonte, framework e tags (facetas multi-uso)
- **Modal de detalhe** com:
  - **Preview ao vivo** em iframe isolado:
    - HTML/CSS (Uiverse, HyperUI, DaisyUI) — renderiza direto, com Tailwind/DaisyUI via CDN
    - React (shadcn, Magic UI, Aceternity, etc.) — compila no navegador com Babel,
      usando o código do `-demo` como instância de uso quando disponível; cai num
      aviso claro (+ aba Código) quando o componente depende de algo não resolvível
  - **Código** com botão de copiar
  - **Metadados**: fonte, framework, licença, dependências, link de origem
- **Paginação** sobre os milhares de componentes

## 📁 Estrutura

```
site/
├── start_app.py          # Sobe backend + frontend e abre o navegador
├── backend/
│   ├── app.py            # API Flask (camada web fina)
│   ├── repository.py     # Acesso a dados (única ponte com o SQLite)
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx          # Página principal (busca, filtros, grid, paginação)
    │   ├── api.js           # Cliente da API
    │   ├── components/
    │   │   ├── ui/          # Button, Card, Badge, Input (design system Felixo)
    │   │   ├── BackgroundParticles.jsx
    │   │   ├── FilterSidebar.jsx
    │   │   ├── ComponentCard.jsx
    │   │   └── ComponentModal.jsx
    │   └── utils/cx.js
    ├── index.css            # Estilos de glow Felixo
    └── (configs Vite/Tailwind/PostCSS)
```

## 🚀 Como rodar

**Pré-requisito:** o banco precisa existir. Rode a coleta antes, na pasta `scraper/`:

```bash
python main.py --all-sources --commit --no-interactive
```

Depois, na pasta `site/`, um único comando instala tudo e abre o navegador:

```bash
python start_app.py
```

| Comando | O que faz |
|---------|-----------|
| `python start_app.py` | Instala deps (se preciso) + sobe API e frontend + abre o navegador |
| `python start_app.py restart` | Reinicia as instâncias nas portas |
| `python start_app.py --no-browser` | Sobe sem abrir o navegador |
| `python start_app.py --no-install` | Pula a instalação de dependências |

- Frontend: http://127.0.0.1:5173
- API: http://127.0.0.1:5001

## 🔌 API

| Rota | Descrição |
|------|-----------|
| `GET /api/health` | Status e se o banco existe |
| `GET /api/filters` | Opções de filtro (fontes, frameworks, categorias, tags) |
| `GET /api/components` | Busca paginada — params: `q`, `source`, `framework`, `category`, `tag`, `include_demos`, `page`, `per_page` |
| `GET /api/components/<external_id>` | Detalhe completo (código, dependências, tags) |

## 🏛️ Arquitetura

Segue a separação de responsabilidades do padrão backend Felixo:

- **`repository.py`** — única camada que toca o SQLite; devolve dicts puros
- **`app.py`** — camada web fina: valida entrada, chama o repository, serializa JSON
- **frontend** — consome a API via `/api` (proxy do Vite em dev, sem host hardcoded)

O preview ao vivo roda em `<iframe sandbox>` isolado, sem executar código no contexto da
página. Para HTML, injeta o markup com Tailwind (e DaisyUI quando for o caso) via CDN.
Para React, compila o código com Babel standalone dentro do iframe e renderiza a instância
de uso vinda do `-demo`; hooks do React e utilitários comuns (`cn`, `motion`, primitivos
de UI) são fornecidos por stubs. A lógica do preview fica em `src/utils/preview.js`.
