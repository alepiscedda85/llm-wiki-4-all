# Roadmap

Questa roadmap mantiene il progetto coerente con il vincolo MVP: locale, file-based, CLI-only, senza database, frontend, LangChain o vector database.

## Fatto

- CLI `init`, `ingest`, `query`, `query --save`, `lint`.
- Provider Ollama default.
- Provider OpenAI opzionale via API key.
- Workspace multipli con `--workspace`.
- `workspace/AGENTS.md` separato.
- `workspace/config.yaml` letto dalla CLI.
- Source path relativi al workspace.
- Test automatici `unittest`.

## Prossima priorita

1. Separare `scripts/llm_wiki.py` in moduli piu piccoli:
   - `llm_wiki/providers.py`
   - `llm_wiki/prompts.py`
   - `llm_wiki/storage.py`
   - `llm_wiki/search.py`
   - `llm_wiki/commands.py`

2. Aggiungere comandi workspace:
   - `workspace list`
   - `workspace create`
   - `workspace doctor`

3. Migliorare test CLI:
   - parsing completo;
   - errori attesi;
   - isolamento tra due workspace;
   - mock provider LLM.

4. Migliorare qualita output:
   - prompt piu rigidi;
   - validazione sezioni Markdown;
   - lingua forzata da `config.yaml`;
   - report su pagine malformate.

## Dopo MVP

- Export Markdown bundle.
- Export PDF.
- Template personalizzabili.
- Profili provider piu avanzati.
- Embedding locali opzionali.
- Frontend guidato opzionale.

## Cose da non fare ora

- Non introdurre database.
- Non introdurre vector database.
- Non introdurre LangChain.
- Non costruire SaaS.
- Non aggiungere frontend prima che la CLI sia stabile.
