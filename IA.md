# 🤖 CONTEXTO-IA — Felixo UI Index

> Memória técnica do projeto para retomada por IA. Preencher continuamente conforme o projeto evolui.
> Baseado no template `IA.md` do Felixo System Design.

---

## 🎯 OBJETIVO DO PROJETO

[2026-06-05] Banco local pesquisável de componentes de UI open source, agregados de múltiplas
bibliotecas da comunidade (Uiverse, shadcn/ui, Magic UI, Aceternity, etc.). Coleta código,
metadados, licença e link de origem. Público: uso pessoal/portfólio Felixo. Prioridade:
coleta correta e respeitosa à licença > escala. Possível evolução: busca semântica por IA.

---

## 🏁 METAS & MILESTONES

- [2026-06-05] ✅ Pesquisa das fontes e métodos de coleta (API, registry JSON, GitHub, scraping)
- [2026-06-05] ✅ Scraper com 9 adapters funcionais + persistência idempotente
- [2026-06-05] ✅ Migração de coleta GitHub API → git clone (destrava teto de 1000/pasta)
- [2026-06-05] ✅ Coleta completa: ~4.700 componentes de 10 fontes no SQLite
- [2026-06-05] ✅ Float UI adicionado com coleta de metadados apenas (restrição de licença)
- [2026-06-05] ✅ Repositório formatado no padrão Felixo (README, IA.md, start_app, testes)
- [2026-06-06] ✅ Categorização canônica + tags multi-uso + flag is_demo
- [2026-06-06] ✅ Banco normalizado relacional (sources/components/tags/files) + índices
- [ ] ⬜ Busca semântica por IA — melhoria aberta à comunidade (ver README, "Próximos passos")

---

## 🛠️ STACK & DEPENDÊNCIAS

[2026-06-05] Python 3.11+ (sem framework web — é uma CLI/coletor)
[2026-06-05] httpx — cliente HTTP para registries JSON e APIs
[2026-06-05] beautifulsoup4 — parser HTML/offline (disponível para adapters que precisarem)
[2026-06-05] git (CLI) — clone shallow de repositórios públicos via subprocess
[2026-06-05] SQLite (stdlib) — persistência; sem ORM, SQL direto em persistence.py
[2026-06-05] Sem Django/banco externo por decisão explícita do usuário (foco no scraping)

---

## 📐 DECISÕES DE ARQUITETURA

[2026-06-05] Arquitetura de adapters (Strategy): um adapter por fonte em src/adapters/,
todos implementando SourceAdapter.collect(config) -> list[ComponentDTO]. Núcleo não conhece
detalhes de cada site. Seguir o guia GUIA-SCRAPING-MULTIFORMATO do Felixo.
[2026-06-05] registry.py é o único ponto de descoberta das fontes (sem if/else espalhado).
[2026-06-05] persistence.py é a única fronteira com SQLite. DTO (models.py) é puro, sem ORM.
[2026-06-05] Upsert idempotente por external_id: rodar duas vezes não duplica.
[2026-06-05] Salva JSON por fonte (auditoria) sempre; banco só com --commit (dry-run por padrão).
[2026-06-05] git_clone.py mantém cache em scraper/.cache/repos/ (ignorado pelo git).
[2026-06-06] Banco relacional normalizado em schema.py: sources, components, tags,
component_tags (N:N), component_files, component_dependencies, com FKs e índices.
persistence.py recria relações filhas no update (idempotente). query.py usa JOINs.

---

## 🎨 DECISÕES DE DESIGN & CONVENÇÕES

[2026-06-05] Nomes de código em inglês, comentários e logs em português.
[2026-06-05] external_id estável por fonte: formato "{slug}_{nome}" ou "{slug}_{cat}_{nome}".
[2026-06-05] capture_source registra a origem: registry_json | git_clone | git_clone_metadata_only.
[2026-06-05] Cada adapter define slug, display_name, framework e license como atributos de classe.

---

## 🧪 TESTES IMPORTANTES

[2026-06-05] Testes offline em scraper/tests/ validam parsers sem rede:
  - test_registry: registry resolve adapter por slug e ergue erro em slug desconhecido.
  - test_floatui_metadata: frontmatter é extraído SEM o código (campo ltr ignorado, files vazio).
  - test_persistence: upsert idempotente — rodar duas vezes não duplica.
  - test_models: ComponentDTO mantém contrato (campos obrigatórios e defaults).

---

## 🐛 BUGS & FIXES RELEVANTES

[2026-06-05] BUG: shadcn/Origin UI retornavam 404 nos endpoints HTTP /r/{name}.json.
CAUSA: shadcn moveu o registry para o monorepo no GitHub (apps/v4/...); Origin UI bloqueia
direto e teve repo movido (redirect 301).
FIX: ambos migrados para coleta via git clone do repositório oficial.

[2026-06-05] BUG: Uiverse coletava no máx 1000 itens por categoria.
CAUSA: a API GitHub /contents lista no máximo 1000 itens por pasta. Buttons tem 1231.
FIX: trocado para git clone + leitura do disco. Destravou 3802 componentes (era ~3000).

---

## 🔗 INTEGRAÇÕES & SERVIÇOS EXTERNOS

[2026-06-05] GitHub — git clone de repos públicos + GitHub API (fallback). Token opcional via
.env (GITHUB_TOKEN) sobe limite de 60 → 5000 req/hora. .env é ignorado pelo git.
[2026-06-05] Registries JSON públicos: magicui.design/registry.json, ui.aceternity.com/registry,
21st.dev/r/{author}/{name}.

---

## 📝 NOTAS GERAIS

[2026-06-05] Float UI tem licença proprietária que proíbe redistribuir componentes standalone.
Decisão: coletar SÓ metadados (title, category, slug, link), nunca o código. files=[] e
capture_source="git_clone_metadata_only". Verificado: 198/198 com files vazio.
[2026-06-05] Não é app web → start_app.py adaptado para "setup + coleta", não "subir servidor".

---

## 🧠 RESUMOS DE DECISÃO

[2026-06-05] CONTEXTO: coletar todas as fontes citadas sem estourar rate limit nem perder itens.
ALTERNATIVAS: (a) GitHub API /contents por arquivo; (b) Git Trees API; (c) git clone local.
DECISÃO: git clone shallow das fontes baseadas em repositório. Sem teto de 1000/pasta, gasta
~zero rate limit, lê do disco, repos ficam em cache para a próxima rodada.
VALIDAÇÃO: coleta completa rodou em exit 0, 4714 componentes no banco; Uiverse subiu de ~3000
(limite da API) para 3802 reais.

[2026-06-05] CONTEXTO: incluir Float UI sem violar a licença que proíbe redistribuição.
ALTERNATIVAS: (a) deixar de fora; (b) só metadados; (c) coletar tudo assumindo o risco.
DECISÃO: coletar só metadados — indexa a existência do componente e o link oficial, sem
guardar o código licenciado.
VALIDAÇÃO: SQL confirmou files='[]' em todos os 198 registros do floatui.

[2026-06-06] CONTEXTO: categorização inconsistente (Buttons/buttons/""/components),
405 sem categoria, e componentes multi-uso (botão animado) presos a uma categoria só.
ALTERNATIVAS: (a) categoria única normalizada; (b) lista de categorias sem primária;
(c) primária + tags de faceta.
DECISÃO: (c) — canonical_category continua como primária (navegação/ordenação) e
category_tags (JSON) guarda todas as facetas para busca multi-uso. Facetas transversais
(animation, effect, 3d, theme...) somam-se à categoria estrutural. Demos do Magic UI
marcados com is_demo e escondidos por padrão na busca.
VALIDAÇÃO: 392 componentes com 2+ tags; busca por 'animation' passou a trazer modal/
tooltip/progress animados; 139 demos marcados; 26 testes passando. Regras em
src/categorize.py (derivação aplicada na persistência e na migração relacional).

[2026-06-06] CONTEXTO: banco era 1 tabela "larga" com listas em JSON (tags, files, deps)
e sem índices — buscas faziam full table scan e não eram relacionais de verdade.
ALTERNATIVAS: (a) só adicionar índices; (b) normalizar em tabelas com FK; (c) Postgres.
DECISÃO: (a)+(b) em SQLite — esquema relacional (sources, components, tags, component_tags,
component_files, component_dependencies) com FKs e índices. Postgres ficou para quando
virar serviço/web.
VALIDAÇÃO: migrate_relational.py converteu os 4714 sem perda (integrity ok, 0 fk_errors,
52 tags, 5174 relações, 4484 arquivos). EXPLAIN QUERY PLAN confirma uso de índice
(SEARCH USING INDEX) em vez de SCAN. 31 testes passando.

---

> Baseado no template `IA.md` do **Felixo System Design**.
> Origem: https://github.com/Felipe-Alcantara/Felixo-System-Design
