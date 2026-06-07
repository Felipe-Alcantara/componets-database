# 🧩 Felixo UI Index

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![httpx](https://img.shields.io/badge/httpx-API_Client-2A6DB0?style=for-the-badge)
![Git](https://img.shields.io/badge/Git-Clone_Collector-F05032?style=for-the-badge&logo=git&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Banco pesquisável de componentes de UI open source, coletados de múltiplas fontes da comunidade.**

[📋 Sobre](#-sobre-o-projeto) • [📁 Estrutura](#-estrutura-do-projeto) • [🚀 Como Usar](#-como-usar) • [🔌 Fontes](#-fontes-coletadas)

</div>

---

Um agregador que cataloga componentes de UI de bibliotecas open source da comunidade (Uiverse, shadcn/ui, Magic UI, Aceternity e outras), salvando código, metadados, licença e link de origem em um banco SQLite pesquisável. A coleta é feita por uma arquitetura de **adapters** (um por fonte), com persistência idempotente e respeito às licenças de cada projeto.

## 📋 Índice

- [📋 Sobre o Projeto](#-sobre-o-projeto)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🔌 Fontes Coletadas](#-fontes-coletadas)
- [🗄️ Banco de Dados](#️-banco-de-dados)
- [🚀 Como Usar](#-como-usar)
- [🔧 Funcionalidades Técnicas](#-funcionalidades-técnicas)
- [⚠️ Limitações](#️-limitações)
- [🛡️ Licenças & Ética de Coleta](#️-licenças--ética-de-coleta)
- [🚀 Próximos passos abertos à comunidade](#-próximos-passos-abertos-à-comunidade)
- [📝 Licença](#-licença)
- [👤 Autor](#-autor)

---

## 📋 Sobre o Projeto

Existem centenas de bibliotecas de componentes React/Tailwind/CSS espalhadas pela comunidade, mas elas ficam isoladas em "catálogos" pouco conhecidos. O **Felixo UI Index** resolve isso reunindo todas em um único banco local, pesquisável por nome, categoria, framework e licença.

O coletor segue o padrão de **scraping multiformato** do Felixo System Design: prioriza **APIs oficiais e registries JSON** quando existem, usa **git clone** para repositórios públicos (sem gastar rate limit nem esbarrar em tetos de API), e respeita a licença de cada fonte — inclusive coletando **apenas metadados** quando a redistribuição do código é proibida.

### ✨ Destaques

- 🔌 **10 fontes** integradas, cada uma com seu adapter isolado
- 🧩 **4.700+ componentes** coletados em uma rodada completa
- 📦 **Persistência idempotente** — rodar de novo atualiza, não duplica
- ⚖️ **Consciente de licença** — bloqueia redistribuição quando a fonte não permite
- 🚀 **Um comando** para instalar e coletar tudo

---

## 📁 Estrutura do Projeto

```
componets-database/
│
├── 📁 scraper/                    # Coletor de componentes
│   ├── main.py                    # CLI principal (--source, --all-sources)
│   ├── query.py                   # Consulta o banco (JOINs, --tags, --category)
│   ├── migrate_relational.py      # Migração: banco flat -> esquema relacional
│   ├── requirements.txt           # Dependências Python
│   ├── 📁 src/
│   │   ├── config.py              # Limites operacionais (env vars)
│   │   ├── models.py              # ComponentDTO (contrato puro)
│   │   ├── schema.py              # Esquema relacional + índices
│   │   ├── categorize.py          # Categoria canônica + tags de faceta
│   │   ├── registry.py            # Mapa de todos os adapters
│   │   ├── persistence.py         # Upsert idempotente no banco relacional
│   │   ├── git_clone.py           # Cache de clones de repositórios
│   │   └── 📁 adapters/           # Um adapter por fonte
│   └── 📁 tests/                  # Testes offline (31 testes)
│
├── 📁 site/                       # Site: biblioteca visual de componentes
│   ├── start_app.py              # Sobe backend + frontend e abre o navegador
│   ├── 📁 backend/               # API Flask (app.py + repository.py)
│   └── 📁 frontend/              # React 18 + Tailwind + Framer Motion (Vite)
│
├── 📁 felixo-standards/           # Padrões de qualidade (submódulo)
├── start_app.py                   # Setup + coleta com um comando
├── IA.md                          # Contexto operacional para IA
├── README.md                      # Este arquivo
└── LICENSE                        # MIT
```

---

## 🔌 Fontes Coletadas

| Fonte | Componentes | Método de coleta | Licença |
|-------|------------:|------------------|---------|
| Uiverse.io | ~3800 | git clone | MIT |
| Magic UI | ~245 | registry JSON | MIT |
| Float UI | ~198 | git clone (**só metadados**) | proprietária |
| React Bits | ~133 | git clone | MIT + Commons Clause |
| Aceternity UI | ~66 | registry JSON | custom |
| HyperUI | ~65 | git clone (MDX) | MIT |
| DaisyUI | ~58 | git clone (CSS) | MIT |
| shadcn/ui | ~56 | git clone | MIT |
| Origin UI | ~53 | git clone | MIT |
| 21st.dev | ~38 | registry JSON | MIT |

> Os números variam a cada coleta conforme as fontes recebem novos componentes.

---

## 🗄️ Banco de Dados

O banco é **SQLite** com esquema **relacional normalizado** (chaves estrangeiras e
índices). Listas como tags, arquivos e dependências viram tabelas próprias — buscas
usam JOIN indexado em vez de varrer texto.

```
sources (1) ──< (N) components (N) >──< (N) tags        [via component_tags]
                         │
                         ├──< (N) component_files         (código por arquivo)
                         └──< (N) component_dependencies  (deps npm)
```

| Tabela | Papel |
|--------|-------|
| `sources` | Uma linha por fonte (slug, framework, licença) |
| `components` | Núcleo: nome, categoria primária, is_demo, URLs, FK p/ source |
| `tags` + `component_tags` | Facetas multi-uso (N:N) — um botão animado é `button` E `animation` |
| `component_files` | Código dos componentes (1 linha por arquivo) |
| `component_dependencies` | Dependências npm declaradas |

**Categorização em duas camadas:**
- `canonical_category` — categoria **primária** única, para navegação
- `tags` — **todas as facetas** aplicáveis, para busca por caso de uso

```bash
python query.py --categories          # totais por categoria primária
python query.py --tags                # totais por faceta
python query.py --category animation  # tudo que é animado, de qualquer tipo
```

Variações de demonstração (`-demo`) são marcadas com `is_demo` e escondidas por
padrão; use `--include-demos` para vê-las.

---

## 🚀 Como Usar

### Opção 1: Forma mais fácil (Recomendado!) 🚀

Um único comando instala as dependências e coleta tudo:

```bash
python start_app.py
```

### Opção 2: Para desenvolvedores

#### Instalação

```bash
# Clone o repositório
git clone https://github.com/Felipe-Alcantara/componets-database.git
cd componets-database/scraper

# Instale as dependências
pip install -r requirements.txt
```

#### (Opcional) Token do GitHub

As fontes via API/clone funcionam sem token, mas um token sobe o limite do GitHub de 60 → 5000 requisições/hora:

```bash
cp .env.example .env
# edite o .env e cole seu token (https://github.com/settings/tokens)
```

#### Executando

```bash
# Listar fontes disponíveis
python main.py --list-sources

# Coletar de uma fonte (preview, não grava no banco)
python main.py --source magicui --limit 50

# Coletar tudo e gravar no banco SQLite
python main.py --all-sources --commit --no-interactive

# Consultar o banco
python query.py --stats                 # totais por fonte
python query.py --categories            # totais por categoria primária
python query.py --tags                  # totais por faceta (tag)
python query.py --search "button" --framework React
python query.py --category animation    # busca multi-uso (qualquer tipo animado)
python query.py --show magicui_shimmer-button
```

### Opção 3: Navegar pela biblioteca visual (site) 🖥️

Depois de coletar, suba o site para explorar os componentes com busca, filtros, preview
ao vivo e código — na pasta `site/`:

```bash
python start_app.py
```

Sobe a API (Flask) e o frontend (React/Vite) e abre o navegador. Detalhes em
[`site/README.md`](site/README.md).

---

## 🔧 Funcionalidades Técnicas

### Arquitetura de adapters

Cada fonte implementa a interface `SourceAdapter` (`src/adapters/base.py`), com um único método `collect(config)` que devolve uma lista de `ComponentDTO`. O núcleo não conhece detalhes de seletor, JSON ou estrutura de pasta de cada site — tudo fica isolado no adapter da fonte.

- **`registry.py`** — ponto único de descoberta das fontes suportadas
- **`schema.py`** — esquema relacional (sources, components, tags, files) + índices
- **`persistence.py`** — única fronteira com o banco; upsert idempotente por `external_id`
- **`categorize.py`** — deriva categoria primária e tags de faceta a partir do nome
- **`git_clone.py`** — clona repositórios públicos uma vez em `.cache/repos/` e lê do disco

### Modos de coleta

- **`registry JSON`** — `magicui`, `aceternity`, `21stdev`: baixam o JSON oficial (código inline)
- **`git_clone`** — `uiverse`, `shadcn`, `reactbits`, `hyperui`, `daisyui`, `originui`: clone shallow
- **`git_clone_metadata_only`** — `floatui`: clona mas grava **só metadados**, sem o código

---

## ⚠️ Limitações

- **Float UI**: por restrição de licença, apenas metadados (nome, categoria, link) são salvos — **sem código**.
- **Rate limit**: as fontes via API/clone pontual usam o GitHub; sem token, o limite é 60 req/hora.
- **Cobertura**: a lista de componentes de algumas fontes (ex.: Aceternity, 21st) é mantida manualmente nos adapters e pode ficar atrás de novos lançamentos.

---

## 🛡️ Licenças & Ética de Coleta

Este projeto segue o guia de **scraping multiformato** do Felixo System Design:

- ✅ Prioriza **APIs oficiais e registries públicos** antes de qualquer coleta agressiva
- ✅ Usa **git clone de repositórios públicos**, respeitando a licença declarada
- ✅ **Não redistribui** código de fontes com licença restritiva (coleta só metadados)
- ✅ **Nunca grava** tokens, cookies ou segredos no repositório (`.env` é ignorado pelo git)

A licença original de cada componente é preservada no campo `license` do banco, junto ao link da fonte para atribuição.

---

## 📝 Licença

Este projeto está sob a licença MIT — veja o arquivo [`LICENSE`](LICENSE).
Os componentes coletados mantêm a licença original de suas respectivas fontes.

## 👤 Autor

**Felipe Martin**
- GitHub: [@Felipe-Alcantara](https://github.com/Felipe-Alcantara)

## 🚀 Próximos passos abertos à comunidade

Ideias que o projeto poderia expandir, para quem quiser contribuir:

- **Busca semântica por IA** — encontrar componentes por descrição em linguagem natural
  (ex.: "um card estilo cyberpunk para dashboard") em vez de só por nome/categoria.
- **Novas fontes** — adicionar adapters para outras bibliotecas de componentes da comunidade.
- **Preview visual** — gerar ou coletar imagens de preview dos componentes.
- **Exportação** — formatos para importar componentes direto em projetos.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Adicionar um novo adapter de fonte (veja `src/adapters/base.py`)
- Reportar bugs ou problemas de coleta
- Melhorar a documentação

---

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!
