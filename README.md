# llm-wiki-4-all

Template locale e generico per trasformare fonti grezze in una wiki Markdown persistente, interrogabile e manutenibile.

La repo parte vuota e neutrale: chi la scarica puo usarla per studio, lavoro, ricerca, clienti, procedure interne, documentazione tecnica, knowledge base personale o qualunque altro dominio.

Di default usa modelli gratuiti/locali tramite Ollama, con default `qwen2.5:3b`. In alternativa puoi inserire la tua chiave OpenAI nel file `.env` e usare il provider OpenAI. Non usa database, LangChain o frontend.

## Struttura

```text
raw/sources/          fonti originali .md o .txt
wiki/                 wiki generata
wiki/index.md         indice principale
wiki/log.md           registro append-only
wiki/overview.md      introduzione
wiki/entities/        persone, aziende, luoghi, strumenti, oggetti, attori rilevanti
wiki/concepts/        concetti riutilizzabili
wiki/outputs/         output operativi, template, audit, checklist, lint report
wiki/contradictions/  contraddizioni, rischi e fonti deboli
scripts/llm_wiki.py   CLI principale
```

## Installazione

Richiede Python 3.11+. Ollama serve per l'uso gratuito locale; OpenAI e opzionale.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Uso gratuito con Ollama

Installa e avvia Ollama:

```bash
brew install ollama
ollama serve
```

Scarica il modello consigliato:

```bash
ollama pull qwen2.5:3b
```

Fallback leggero:

```bash
ollama pull llama3.2
```

## Configurazione

Puoi copiare `.env.example` in `.env`:

```bash
cp .env.example .env
```

Configurazione default:

```env
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

Non serve alcuna API key per usare l'MVP gratis: di default la CLI usa Ollama.

Per usare OpenAI, aggiungi la tua chiave nel file `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
```

Provider:

- `--provider ollama`: default, usa Ollama locale.
- `--provider openai`: forza OpenAI e richiede `OPENAI_API_KEY`.
- `--provider auto`: usa OpenAI se `OPENAI_API_KEY` e presente, altrimenti Ollama.

## Comandi

Inizializza struttura e file base:

```bash
python scripts/llm_wiki.py init
```

Output atteso:

```text
LLM Wiki inizializzata.
```

Ingerisci una fonte con path esplicito:

```bash
python scripts/llm_wiki.py ingest raw/sources/appunti-progetto.md
```

Oppure usa il nome file: la CLI cerchera anche in `raw/sources/`.

```bash
python scripts/llm_wiki.py ingest appunti-progetto.md
```

Usa un modello diverso:

```bash
python scripts/llm_wiki.py ingest appunti-progetto.md --model llama3.2
```

Forza Ollama:

```bash
python scripts/llm_wiki.py ingest appunti-progetto.md --provider ollama
```

Usa OpenAI con la tua chiave:

```bash
python scripts/llm_wiki.py ingest appunti-progetto.md --provider openai --model gpt-5.2
```

Interroga la wiki:

```bash
python scripts/llm_wiki.py query "Riassumi le decisioni operative emerse finora"
```

Salva la risposta:

```bash
python scripts/llm_wiki.py query "Crea una checklist operativa dai documenti disponibili" --save
```

Analizza qualita, rischi e opportunita:

```bash
python scripts/llm_wiki.py lint
```

Il report lint viene salvato in `wiki/outputs/lint-YYYY-MM-DD.md`.

## Esempio fonte generica

Crea `raw/sources/appunti-progetto.md`:

```md
# Appunti progetto

Obiettivo: raccogliere fonti, decisioni e procedure in una wiki locale.

Problema: le informazioni sono sparse tra note, documenti e messaggi.

Vincoli: mantenere le fonti originali immutabili, citare i file usati e segnalare informazioni mancanti.

Output utili: checklist, FAQ, sintesi operative, template e domande aperte.
```

Poi esegui:

```bash
python scripts/llm_wiki.py ingest appunti-progetto.md
```

## Esempio output atteso

La CLI generera una pagina in `wiki/outputs/` con:

- sintesi operativa
- punti chiave
- implicazioni pratiche
- output riutilizzabili
- collegamenti wiki
- contraddizioni o rischi
- domande aperte
- fonti
- note di manutenzione

`wiki/index.md` ricevera un wikilink Obsidian-style con categoria, descrizione e data ultimo aggiornamento. `wiki/log.md` registrera l'operazione in append.

## Limiti MVP

- Ricerca locale lessicale, non embedding.
- Provider LLM attivi: Ollama locale oppure OpenAI via API key personale.
- Nessun database.
- Nessun frontend.
- Nessun export PDF.
- La qualita dipende dal modello scelto e dalla chiarezza delle fonti.
- I modelli piccoli possono sbagliare: usare `lint` e mantenere fonti verificabili.

## Prossimi step

- Frontend guidato per consultazione e manutenzione.
- Export PDF.
- RAG ibrido con embedding locali.
- Profili multi-progetto.
- Template personalizzabili per domini diversi.
- Selezione provider piu avanzata con profili per progetto/team.
