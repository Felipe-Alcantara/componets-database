# 🤝 Contribuindo com o Felixo UI Index

Obrigado por querer contribuir! Este projeto reúne componentes de UI open source de
várias bibliotecas da comunidade em um banco pesquisável. Melhorar junto é a ideia.

Sinta-se à vontade para adicionar fontes novas, corrigir a coleta, melhorar a
documentação ou propor ideias. Toda contribuição — por menor que seja — é bem-vinda.

---

## 📋 Índice

- [Como Contribuir](#-como-contribuir)
- [Adicionar uma fonte nova](#-adicionar-uma-fonte-nova)
- [Padrões de Qualidade](#-padrões-de-qualidade)
- [Ética de Coleta](#-ética-de-coleta)
- [Fluxo de Pull Request](#-fluxo-de-pull-request)

---

## 🚀 Como Contribuir

1. **Faça um fork** do repositório.
2. **Crie uma branch** descritiva (`fix/...`, `feat/...`, `docs/...`).
3. **Faça suas mudanças** seguindo os padrões abaixo.
4. **Rode os testes** (`python -m unittest discover tests` na pasta `scraper/`).
5. **Abra um Pull Request** explicando o que mudou e por quê.

Não tem certeza por onde começar? Abra uma issue descrevendo a ideia — dá pra conversar
antes de investir tempo no código.

---

## ➕ Adicionar uma fonte nova

A coleta usa uma arquitetura de **adapters** (um por fonte). Para integrar uma biblioteca:

1. Crie `scraper/src/adapters/minha_fonte.py` implementando `SourceAdapter.collect(config)`,
   que devolve uma lista de `ComponentDTO` (veja `src/adapters/base.py`).
2. Registre o adapter em `scraper/src/registry.py`.
3. Adicione um teste offline em `scraper/tests/`.

O núcleo não conhece detalhes de cada site — tudo fica isolado no adapter.

---

## ✅ Padrões de Qualidade

Este projeto segue o contrato de qualidade do **Felixo System Design**
(`felixo-standards/core/GUIA_MINIMO_QUALIDADE.md`). Em resumo:

- Entenda o padrão existente antes de alterar — não invente convenções que o projeto
  já define.
- Mantenha responsabilidades separadas e prefira a solução mais simples que resolva o
  problema real.
- **Não exponha segredos** (tokens, credenciais) nem caminhos ou URLs privadas — no
  código, na documentação ou nos logs. Use placeholders genéricos.
- Escreva documentação e logs com **linguagem geral e acessível**, para qualquer leitor.
- Atualize README, guias ou `IA.md` quando a mudança exigir.
- Faça mudanças pequenas e rastreáveis, com escopo claro.

---

## ⚖️ Ética de Coleta

Componentes têm licenças diferentes. Ao adicionar ou alterar uma fonte:

- Prefira **APIs oficiais e registries públicos**; use git clone de repositórios públicos.
- **Respeite a licença** de cada fonte. Se ela proíbe redistribuir o código, colete
  **apenas metadados** (nome, categoria, link), como é feito com o Float UI.
- Preserve a licença original de cada componente no banco, junto ao link de origem.

---

## 🔄 Fluxo de Pull Request

Um bom PR responde claramente:

- **O que mudou?**
- **Por que mudou?**
- **Como foi validado?** (testes rodados, coleta verificada)
- **Qual risco sobrou?**

Mantenha o PR focado: evite misturar refatoração ampla com novas funcionalidades sem
necessidade.

---

⭐ Se este projeto te ajudou, considere deixar uma estrela no GitHub!
