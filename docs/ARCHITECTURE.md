# Architettura

`llm-wiki-4-all` e un framework locale, file-based e CLI-first per creare wiki Markdown assistite da LLM.

## Principi

- Locale prima di tutto.
- Nessun database.
- Nessun vector database nell'MVP.
- Nessun frontend nell'MVP.
- Nessun LangChain o framework pesante.
- Storage Markdown leggibile da qualunque editor.
- Workspace separati per evitare contaminazione tra progetti.

## Componenti

```text
scripts/llm_wiki.py   CLI principale
llm_wiki/workspace.py modello dei path workspace
llm_wiki/config.py    parser config.yaml minimale
raw/sources/          fonti originali
wiki/                 conoscenza elaborata
instances/            workspace multipli opzionali
tests/                test automatici unittest
```

## Flusso dati

```text
Fonte .md/.txt
    |
    | ingest
    v
Prompt + AGENTS + index
    |
    | provider LLM
    v
Pagina Markdown in wiki/outputs/
    |
    | update_index + append_log
    v
wiki/index.md + wiki/log.md
```

## Provider LLM

La CLI supporta:

- Ollama locale, default gratuito;
- OpenAI opzionale con API key dell'utente.

La selezione provider/modello segue questa precedenza:

1. opzioni CLI: `--provider`, `--model`;
2. variabili `.env`: `LLM_PROVIDER`, `OLLAMA_MODEL`, `OPENAI_MODEL`;
3. `workspace/config.yaml`;
4. default interni.

## Workspace

Un workspace e la root operativa di una singola wiki. Tutti i path operativi sono relativi al workspace selezionato:

```text
AGENTS.md
config.yaml
raw/sources/
wiki/index.md
wiki/log.md
wiki/overview.md
wiki/entities/
wiki/concepts/
wiki/outputs/
wiki/contradictions/
```

Senza `--workspace`, il workspace e la directory corrente.

## Isolamento

`ingest`, `query`, `query --save` e `lint` devono leggere e scrivere solo nel workspace selezionato.

Esempio:

```bash
python3 -B scripts/llm_wiki.py query "Riassumi" --workspace instances/example
```

Questo comando deve usare solo:

```text
instances/example/wiki/
instances/example/AGENTS.md
instances/example/config.yaml
```

## Configurazione

`config.yaml` supporta, per ora, chiavi flat:

```yaml
name: workspace
language: it
provider: ollama
model: qwen2.5:3b
```

Il parser e volutamente minimale e non richiede PyYAML.

## Limiti architetturali attuali

- Gran parte della logica comando vive ancora in `scripts/llm_wiki.py`.
- Non esistono ancora comandi `workspace list/create/doctor`.
- La ricerca e lessicale, non semantica.
- Non esiste export PDF.
