# Felixo UI Index

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![httpx](https://img.shields.io/badge/httpx-API_Client-2A6DB0?style=for-the-badge)
![Git](https://img.shields.io/badge/Git-Clone_Collector-F05032?style=for-the-badge&logo=git&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Banco pesquisavel de componentes de UI open source, coletados de multiplas fontes da comunidade.**

[Sobre](#sobre-o-projeto) | [Estrutura](#estrutura-do-projeto) | [Como Usar](#como-usar) | [Fontes](#fontes-coletadas)

</div>

---

## Indice

- [Sobre o Projeto](#sobre-o-projeto)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Fontes Coletadas](#fontes-coletadas)
- [Banco de Dados](#banco-de-dados)
- [Funcionalidades Tecnicas](#funcionalidades-tecnicas)
- [Limitacoes](#limitacoes)
- [Padroes de Qualidade (felixo-standards)](#padroes-de-qualidade-felixo-standards)
- [Licencas & Etica de Coleta](#licencas--etica-de-coleta)
- [Proximos Passos Abertos a Comunidade](#proximos-passos-abertos-a-comunidade)
- [Licenca](#licenca)
- [Autor](#autor)

---

## Sobre o Projeto

Existem centenas de bibliotecas de componentes React/Tailwind/CSS espalhadas pela comunidade, mas elas ficam isoladas em "catalogos" pouco conhecidos. O **Felixo UI Index** resolve isso reunindo todas em um unico banco local, pesquisavel por nome, categoria, framework e licenca.

O coletor segue o padrao de **scraping multiformato** do Felixo System Design: prioriza **APIs oficiais e registries JSON** quando existem, usa **git clone** para repositorios publicos (sem gastar rate limit nem esbarrar em tetos de API), e respeita a licenca de cada fonte — inclusive coletando **apenas metadados** quando a redistribuicao do codigo e proibida.

### Destaques

- **10 fontes** integradas, cada uma com seu adapter isolado
- **4.900+ componentes** coletados em uma rodada completa
- **Persistencia idempotente** — rodar de novo atualiza, nao duplica
- **Consciente de licenca** — bloqueia redistribuicao quando a fonte nao permite
- **Um comando** para instalar e coletar tudo

---

## Como Usar

> **Pre-requisitos**: Python 3.11+ e Node.js 18+. O banco com **os ~4.900 componentes
> ja vem no clone** (`scraper/data/components.db`) — nao precisa coletar para ver o site.

### 1. Clonar o repositorio

```bash
git clone https://github.com/Felipe-Alcantara/componets-database.git
cd componets-database
```

### 2. Subir o site (biblioteca visual)

Um unico comando instala as dependencias (backend Flask + frontend Vite), sobe os dois
e abre o navegador na galeria — com mini-preview ao vivo, busca, filtros e codigo:

**Linux / macOS / Git Bash:**
```bash
cd site
python3 start_app.py
```

**PowerShell / CMD (Windows):**
```powershell
cd site
python start_app.py
```

Abre em `http://127.0.0.1:5173`. Detalhes em [`site/README.md`](site/README.md).

---

### (Opcional) Atualizar o banco

O banco versionado e um retrato da coleta. Para atualiza-lo com os componentes mais
recentes das fontes, rode a coleta a partir da raiz:

**Linux / macOS / Git Bash:**
```bash
python3 start_app.py --commit
```

**PowerShell / CMD (Windows):**
```powershell
python start_app.py --commit
```

As fontes funcionam **sem token**, mas um token do GitHub sobe o limite de 60 → 5000
requisicoes/hora:

```bash
cp scraper/.env.example scraper/.env
# edite scraper/.env e cole seu token: https://github.com/settings/tokens
```

### Comandos avulsos (scraper)

Na pasta `scraper/`:

```bash
python main.py --list-sources                       # lista as fontes
python main.py --source magicui --limit 50          # previa de uma fonte
python main.py --all-sources --commit --no-interactive  # coleta tudo no banco

python query.py --stats                 # totais por fonte
python query.py --categories            # totais por categoria primaria
python query.py --tags                  # totais por faceta (tag)
python query.py --search "button" --framework React
python query.py --category animation    # busca multi-uso (qualquer tipo animado)
python query.py --show magicui_shimmer-button
```

### Escolha rapida por cenario

| Cenario | O que rodar |
|---------|-------------|
| Quero ver o site (banco ja vem no clone) | `cd site && python start_app.py` |
| Re-rodar o site sem reinstalar deps | `cd site && python start_app.py --no-install` |
| Reiniciar o site nas portas | `cd site && python start_app.py restart` |
| Atualizar o banco com a coleta mais nova | `python start_app.py --commit` (na raiz) |
| Testar uma fonte so | `cd scraper && python main.py --source magicui --limit 20` |
| Consultar o banco no terminal | `cd scraper && python query.py --stats` |

---

## Estrutura do Projeto

```
componets-database/
│
├── scraper/                    # Coletor de componentes
│   ├── main.py                    # CLI principal (--source, --all-sources)
│   ├── query.py                   # Consulta o banco (JOINs, --tags, --category)
│   ├── migrate_relational.py      # Migracao: banco flat -> esquema relacional
│   ├── requirements.txt           # Dependencias Python
│   ├── src/
│   │   ├── config.py              # Limites operacionais (env vars)
│   │   ├── models.py              # ComponentDTO (contrato puro)
│   │   ├── schema.py              # Esquema relacional + indices
│   │   ├── categorize.py          # Categoria canonica + tags de faceta
│   │   ├── registry.py            # Mapa de todos os adapters
│   │   ├── persistence.py         # Upsert idempotente no banco relacional
│   │   ├── git_clone.py           # Cache de clones de repositorios
│   │   └── adapters/           # Um adapter por fonte
│   └── tests/                  # Testes offline (31 testes)
│
├── site/                       # Site: biblioteca visual de componentes
│   ├── start_app.py              # Sobe backend + frontend e abre o navegador
│   ├── backend/               # API Flask (app.py + repository.py)
│   └── frontend/              # React 18 + Tailwind + Framer Motion (Vite)
│
├── start_app.py                   # Setup + coleta com um comando
├── IA.md                          # Contexto operacional para IA
├── CONTRIBUTING.md                # Guia de contribuicao
├── README.md                      # Este arquivo
└── LICENSE                        # MIT
```

---

## Fontes Coletadas

| Fonte | Componentes | Metodo de coleta | Licenca |
|-------|------------:|------------------|---------|
| Uiverse.io | ~3800 | git clone | MIT |
| HyperUI | ~294 | git clone (HTML) | MIT |
| Magic UI | ~245 | registry JSON | MIT |
| Float UI | ~198 | git clone (**so metadados**) | proprietaria |
| React Bits | ~133 | git clone | MIT + Commons Clause |
| Aceternity UI | ~66 | registry JSON | custom |
| DaisyUI | ~58 | git clone (HTML + CSS) | MIT |
| shadcn/ui | ~56 | git clone | MIT |
| Origin UI | ~53 | git clone | MIT |
| 21st.dev | ~38 | registry JSON | MIT |

> Os numeros variam a cada coleta conforme as fontes recebem novos componentes.

---

## Banco de Dados

O banco e **SQLite** com esquema **relacional normalizado** (chaves estrangeiras e
indices). Listas como tags, arquivos e dependencias viram tabelas proprias — buscas
usam JOIN indexado em vez de varrer texto.

```
sources (1) ──< (N) components (N) >──< (N) tags        [via component_tags]
                         │
                         ├──< (N) component_files         (codigo por arquivo)
                         └──< (N) component_dependencies  (deps npm)
```

| Tabela | Papel |
|--------|-------|
| `sources` | Uma linha por fonte (slug, framework, licenca) |
| `components` | Nucleo: nome, categoria primaria, is_demo, URLs, FK p/ source |
| `tags` + `component_tags` | Facetas multi-uso (N:N) — um botao animado e `button` E `animation` |
| `component_files` | Codigo dos componentes (1 linha por arquivo) |
| `component_dependencies` | Dependencias npm declaradas |

**Categorizacao em duas camadas:**
- `canonical_category` — categoria **primaria** unica, para navegacao
- `tags` — **todas as facetas** aplicaveis, para busca por caso de uso

```bash
python query.py --categories          # totais por categoria primaria
python query.py --tags                # totais por faceta
python query.py --category animation  # tudo que e animado, de qualquer tipo
```

Variacoes de demonstracao (`-demo`) sao marcadas com `is_demo` e escondidas por
padrao; use `--include-demos` para ve-las.

---

## Funcionalidades Tecnicas

### Arquitetura de adapters

Cada fonte implementa a interface `SourceAdapter` (`src/adapters/base.py`), com um unico metodo `collect(config)` que devolve uma lista de `ComponentDTO`. O nucleo nao conhece detalhes de seletor, JSON ou estrutura de pasta de cada site — tudo fica isolado no adapter da fonte.

- **`registry.py`** — ponto unico de descoberta das fontes suportadas
- **`schema.py`** — esquema relacional (sources, components, tags, files) + indices
- **`persistence.py`** — unica fronteira com o banco; upsert idempotente por `external_id`
- **`categorize.py`** — deriva categoria primaria e tags de faceta a partir do nome
- **`git_clone.py`** — clona repositorios publicos uma vez em `.cache/repos/` e le do disco

### Modos de coleta

- **`registry JSON`** — `magicui`, `aceternity`, `21stdev`: baixam o JSON oficial (codigo inline)
- **`git_clone`** — `uiverse`, `shadcn`, `reactbits`, `hyperui`, `daisyui`, `originui`: clone shallow
- **`git_clone_metadata_only`** — `floatui`: clona mas grava **so metadados**, sem o codigo

---

## Limitacoes

- **Float UI**: por restricao de licenca, apenas metadados (nome, categoria, link) sao salvos — **sem codigo**.
- **Rate limit**: as fontes via API/clone pontual usam o GitHub; sem token, o limite e 60 req/hora.
- **Cobertura**: a lista de componentes de algumas fontes (ex.: Aceternity, 21st) e mantida manualmente nos adapters e pode ficar atras de novos lancamentos.

---

## Padroes de Qualidade (felixo-standards)

Este projeto segue o **[Felixo System Design](https://github.com/Felipe-Alcantara/Felixo-System-Design)**.
A pasta `felixo-standards/` (ignorada pelo git) e sincronizada localmente. Para puxar a
versao mais recente, use o metodo mais adequado:

> **Sobre submodulos:** o Felixo System Design inclui o submodulo `componets-database/` — que e **este proprio projeto**. Para os padroes `core/` e `guias/` (o que interessa aqui), **clone sem `--recurse-submodules`**: assim voce evita baixar uma copia recursiva deste repositorio dentro de `felixo-standards/`. Os comandos abaixo ja sao a variante leve, sem submodulo.

### 1. Sincronizar sem `.git` (recomendado)

**Linux / macOS / Git Bash:**
```bash
tmp_dir="$(mktemp -d)" && git clone --depth 1 https://github.com/Felipe-Alcantara/Felixo-System-Design.git "$tmp_dir/repo" && find "$tmp_dir/repo" -name .git -prune -exec rm -rf {} + && mkdir -p ./felixo-standards && rsync -a --delete "$tmp_dir/repo/" ./felixo-standards/ && rm -rf "$tmp_dir"
```

**PowerShell (Windows):**
```powershell
$tmpDir = Join-Path $env:TEMP ("felixo-standards-" + [guid]::NewGuid())
git clone --depth 1 https://github.com/Felipe-Alcantara/Felixo-System-Design.git $tmpDir
Remove-Item -Recurse -Force (Join-Path $tmpDir ".git")
New-Item -ItemType Directory -Force -Path "./felixo-standards" | Out-Null
robocopy $tmpDir "./felixo-standards" /MIR | Out-Null
Remove-Item -Recurse -Force $tmpDir
```

#### Atalho global `felixo` (Bash/Zsh)

A funcao traz apenas `core/` e `guias/` por padrao. A flag `-s` / `--with-submodules`
existe por paridade com o repositorio original, mas **aqui nao e recomendada** (baixaria
uma copia recursiva deste projeto).

```bash
felixo() {
  local dest="./felixo-standards"
  local repo_url="https://github.com/Felipe-Alcantara/Felixo-System-Design.git"
  local clone_args=(--depth 1)
  [[ "$1" == "--with-submodules" || "$1" == "-s" ]] && clone_args+=(--recurse-submodules)
  local tmp_dir
  tmp_dir="$(mktemp -d)" || return 1
  git clone "${clone_args[@]}" "$repo_url" "$tmp_dir/repo" || { rm -rf "$tmp_dir"; return 1; }
  find "$tmp_dir/repo" -name .git -prune -exec rm -rf {} +
  mkdir -p "$dest"
  rsync -a --delete "$tmp_dir/repo/" "$dest/"
  rm -rf "$tmp_dir"
}
```

### 2. Baixar como ZIP

**Linux / macOS:**
```bash
curl -L https://github.com/Felipe-Alcantara/Felixo-System-Design/archive/refs/heads/main.zip -o felixo.zip
unzip felixo.zip && mv Felixo-System-Design-main felixo-standards && rm felixo.zip
```

### 3. Baixar com `npx degit`

```bash
npx degit Felipe-Alcantara/Felixo-System-Design ./felixo-standards
```

| Cenario | Melhor opcao |
|---------|--------------|
| Quero atualizar quando quiser | sincronizacao sem `.git` / atalho `felixo` |
| Quero da forma mais simples | ZIP |
| Quero sem `.git` via terminal | `npx degit` |

---

## Licencas & Etica de Coleta

Este projeto segue o guia de **scraping multiformato** do Felixo System Design:

- Prioriza **APIs oficiais e registries publicos** antes de qualquer coleta agressiva
- Usa **git clone de repositorios publicos**, respeitando a licenca declarada
- **Nao redistribui** codigo de fontes com licenca restritiva (coleta so metadados)
- **Nunca grava** tokens, cookies ou segredos no repositorio (`.env` e ignorado pelo git)

A licenca original de cada componente e preservada no campo `license` do banco, junto ao link da fonte para atribuicao.

---

## Proximos Passos Abertos a Comunidade

Ideias que o projeto poderia expandir, para quem quiser contribuir:

- **Busca semantica por IA** — encontrar componentes por descricao em linguagem natural
  (ex.: "um card estilo cyberpunk para dashboard") em vez de so por nome/categoria.
- **Novas fontes** — adicionar adapters para outras bibliotecas de componentes da comunidade.
- **Exportacao** — formatos para importar componentes direto em projetos.

---

## Contribuicoes

Contribuicoes sao bem-vindas! Veja o [`CONTRIBUTING.md`](CONTRIBUTING.md). Em resumo:
- Adicionar um novo adapter de fonte (veja `scraper/src/adapters/base.py`)
- Reportar bugs ou problemas de coleta
- Melhorar a documentacao

---

## Licenca

Este projeto esta sob a licenca MIT — veja o arquivo [`LICENSE`](LICENSE).
Os componentes coletados mantem a licenca original de suas respectivas fontes.

## Autor

**Felipe Martin**
- GitHub: [@Felipe-Alcantara](https://github.com/Felipe-Alcantara)

---

> **Assinatura de Origem**  
> Este arquivo foi criado por **Felipe Martin** e faz parte do repositorio **componets-database**.  
> Origem: https://github.com/Felipe-Alcantara/componets-database  
> Data desta versao: 2026-06-09  
> Sugestoes e pull requests sao bem-vindos.
