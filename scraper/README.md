# 🔌 Scraper — Coletor de Componentes

Módulo de coleta do **Felixo UI Index**. Reúne componentes de UI de múltiplas fontes
open source num banco SQLite, seguindo o padrão de scraping multiformato do Felixo System Design.

## 📁 Estrutura

```
scraper/
├── main.py            # CLI de coleta
├── query.py           # CLI de consulta ao banco
├── requirements.txt   # Dependências
├── src/
│   ├── config.py      # Limites operacionais (env vars)
│   ├── models.py      # ComponentDTO — contrato puro, sem ORM
│   ├── registry.py    # Mapa de adapters (ponto único de descoberta)
│   ├── persistence.py # Upsert idempotente em JSON + SQLite
│   ├── git_clone.py   # Cache de clones de repositórios públicos
│   └── adapters/      # Um adapter por fonte (interface SourceAdapter)
└── tests/             # Testes offline dos parsers (sem rede)
```

## 🚀 Uso

```bash
pip install -r requirements.txt

python main.py --list-sources                       # lista fontes
python main.py --source magicui --limit 50          # preview (não grava)
python main.py --all-sources --commit --no-interactive  # coleta tudo no banco

python query.py --stats                             # totais por fonte
python query.py --search button --framework React   # busca
```

## ⚙️ Configuração (env vars)

Todas têm default em `src/config.py`. Use o `.env` (ignorado pelo git):

| Variável | Default | Descrição |
|----------|--------:|-----------|
| `GITHUB_TOKEN` | _(vazio)_ | Token GitHub — sobe limite p/ 5000 req/h |
| `SCRAPER_MAX_COMPONENTS` | 500 | Máximo por fonte |
| `SCRAPER_REQUEST_DELAY` | 0.5 | Delay entre requisições (s) |
| `SCRAPER_TIMEOUT_MS` | 30000 | Timeout HTTP |

## ➕ Adicionar uma fonte nova

1. Crie `src/adapters/minha_fonte.py` implementando `SourceAdapter.collect(config)`.
2. Registre o adapter em `src/registry.py`.
3. Adicione um teste offline em `tests/`.

O núcleo não conhece detalhes da fonte — tudo fica isolado no adapter.

## 🧪 Testes

```bash
python -m pytest tests/ -v        # com pytest
python -m unittest discover tests # ou só com a stdlib
```

## 🛡️ Ética de coleta

- Prioriza APIs/registries oficiais; usa git clone para repos públicos.
- **Não redistribui** código de fontes com licença restritiva (ex.: Float UI → só metadados).
- Nunca grava tokens ou segredos no repositório.
