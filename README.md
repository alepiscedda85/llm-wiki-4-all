# llm-wiki-4-all

`llm-wiki-4-all` e un framework locale, generico e file-based per costruire una wiki Markdown assistita da LLM su qualunque dominio.

L'idea e semplice: metti fonti grezze in `raw/sources/`, la CLI le trasforma in pagine strutturate dentro `wiki/`, poi puoi interrogare la wiki, salvare output riutilizzabili e lanciare un audit operativo con `lint`.

La repo nasce neutra: non contiene un dominio obbligatorio. Puoi usarla per lavoro, studio, ricerca, clienti, procedure interne, documentazione tecnica, knowledge base personale, analisi di mercato, manuali operativi o archivi tematici.

Di default usa modelli gratuiti/locali tramite Ollama. Se vuoi, puoi usare anche OpenAI inserendo la tua API key nel file `.env`.

Non usa database, vector database, LangChain o frontend.

## A cosa serve

Serve a trasformare materiale sparso in conoscenza operativa persistente.

Esempi di fonti:

- appunti `.md` o `.txt`;
- trascrizioni di call;
- brief cliente;
- procedure interne;
- note di ricerca;
- FAQ;
- documentazione tecnica;
- bozze di offerte;
- checklist;
- casi reali;
- decisioni di progetto.

Esempi di output:

- sintesi operative;
- checklist;
- template;
- FAQ;
- audit;
- pacchetti di lavoro;
- procedure;
- domande aperte;
- rischi e contraddizioni;
- pagine wiki collegate tra loro.

## Come funziona

Flusso base:

```text
raw/sources/*.md|txt
        |
        | ingest
        v
wiki/outputs/*.md
        |
        | index + log
        v
wiki/index.md + wiki/log.md
        |
        | query / lint
        v
risposte operative o nuovi output salvati
```

Ruoli delle cartelle:

- `raw/`: archivio delle fonti originali, da non modificare automaticamente.
- `wiki/`: conoscenza elaborata e mantenibile.
- `wiki/index.md`: catalogo delle pagine con wikilink Obsidian-style.
- `wiki/log.md`: registro cronologico append-only.
- `wiki/outputs/`: pagine generate, risposte salvate, report lint.
- `wiki/entities/`: persone, aziende, strumenti, luoghi, oggetti o attori rilevanti.
- `wiki/concepts/`: concetti riutilizzabili.
- `wiki/contradictions/`: pagine dedicate a rischi, contraddizioni o fonti deboli.

## Multi-workspace usage

Un workspace e una cartella autonoma che contiene una LLM Wiki separata.

Ogni workspace ha le proprie fonti, istruzioni, configurazione, indice, log e output:

```text
workspace/
  AGENTS.md
  config.yaml
  raw/
    sources/
  wiki/
    index.md
    log.md
    overview.md
    entities/
    concepts/
    outputs/
    contradictions/
```

Perche usarlo:

- separare progetti diversi;
- evitare che fonti e output si mischino;
- usare istruzioni diverse per wiki diverse;
- mantenere una repo unica con piu knowledge base locali;
- testare casi diversi senza sporcare la wiki principale.

Quando usare una singola wiki:

- stai lavorando su un solo dominio;
- vuoi una knowledge base personale semplice;
- non hai bisogno di separare clienti, progetti o contesti.

Quando usare piu workspace:

- hai piu progetti;
- vuoi una wiki per cliente;
- vuoi separare lavoro, studio e ricerca;
- vuoi mantenere istruzioni `AGENTS.md` diverse;
- vuoi distribuire un template vuoto e lasciare che ogni persona crei la propria istanza.

Senza `--workspace`, la CLI usa la directory corrente come workspace. Questo mantiene compatibile l'uso single-wiki:

```bash
python3 -B scripts/llm_wiki.py init
python3 -B scripts/llm_wiki.py ingest raw/sources/example.md
python3 -B scripts/llm_wiki.py query "Riassumi la wiki"
python3 -B scripts/llm_wiki.py lint
```

Con `--workspace`, tutti i path operativi vengono risolti dentro quella cartella:

```bash
python3 -B scripts/llm_wiki.py init --workspace instances/example
```

Aggiungi una fonte in:

```text
instances/example/raw/sources/example.md
```

Poi puoi ingerirla indicando solo il nome file, perche la CLI cerca anche in `workspace/raw/sources/`:

```bash
python3 -B scripts/llm_wiki.py ingest example.md --workspace instances/example
```

Interroga solo quella wiki:

```bash
python3 -B scripts/llm_wiki.py query "Riassumi la wiki" --workspace instances/example
```

Salva un output operativo in quel workspace:

```bash
python3 -B scripts/llm_wiki.py query "Crea una checklist" --type checklist --workspace instances/example --save
```

Esegui lint solo su quel workspace:

```bash
python3 -B scripts/llm_wiki.py lint --workspace instances/example
```

Esempio di struttura multi-wiki:

```text
instances/
  example/
  personal-knowledge/
  software-docs/
  client-alpha/
```

Ogni istanza ha `AGENTS.md`, `config.yaml`, `raw/` e `wiki/` separati. Il motore resta unico: `scripts/llm_wiki.py` e il package `llm_wiki/`.

## Struttura progetto

```text
.env.example          configurazione di esempio
.gitignore            file esclusi da git
AGENTS.md             istruzioni fallback per agenti e modelli
README.md             guida pratica del progetto
requirements.txt      dipendenze Python
llm_wiki/             package core, inclusa la logica Workspace
scripts/llm_wiki.py   CLI principale
instances/            workspace opzionali, uno per wiki
raw/sources/          fonti originali della wiki corrente
config.yaml           configurazione della wiki corrente, se inizializzata
wiki/index.md         indice principale della wiki corrente
wiki/log.md           registro append-only della wiki corrente
wiki/overview.md      introduzione della wiki corrente
wiki/entities/        entita rilevanti
wiki/concepts/        concetti riutilizzabili
wiki/outputs/         output generati e report
wiki/contradictions/  rischi e contraddizioni
```

## Requisiti

- Python 3.11+
- Ollama per uso locale gratuito
- Connessione internet solo per scaricare dipendenze e modelli
- OpenAI API key solo se vuoi usare il provider OpenAI

Su macOS spesso il comando corretto e `python3`, non `python`. Negli esempi sotto uso `python3 -B` per evitare la creazione di `__pycache__` durante i test.

## Installazione

Crea un ambiente virtuale:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Inizializza la wiki:

```bash
python3 -B scripts/llm_wiki.py init
```

Output atteso:

```text
LLM Wiki inizializzata in: /path/del/workspace
```

## Uso gratuito con Ollama

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

Configurazione `.env` consigliata:

```env
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

## Uso opzionale con OpenAI

Copia la configurazione di esempio:

```bash
cp .env.example .env
```

Poi imposta:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
```

Puoi anche usare il provider automatico:

```env
LLM_PROVIDER=auto
```

Con `auto`, la CLI usa OpenAI se trova `OPENAI_API_KEY`; altrimenti resta su Ollama.

## Provider e modelli

Default:

```text
provider: ollama
model: qwen2.5:3b
```

Override globale:

```bash
python3 -B scripts/llm_wiki.py --provider ollama --model llama3.2 query "Riassumi la wiki"
```

Override sul singolo comando:

```bash
python3 -B scripts/llm_wiki.py query "Riassumi la wiki" --model llama3.2
```

OpenAI:

```bash
python3 -B scripts/llm_wiki.py query "Riassumi la wiki" --provider openai --model gpt-5.2
```

## Comandi principali

### init

Crea cartelle e file base in modo idempotente nella directory corrente:

```bash
python3 -B scripts/llm_wiki.py init
```

Oppure in un workspace dedicato:

```bash
python3 -B scripts/llm_wiki.py init --workspace instances/example
```

### ingest

Legge una fonte `.md` o `.txt`, la manda al modello e salva una pagina strutturata in `wiki/outputs/`:

```bash
python3 -B scripts/llm_wiki.py ingest raw/sources/appunti-progetto.md
```

Puoi indicare solo il nome file: la CLI cerca prima il path dato e poi `raw/sources/`.

```bash
python3 -B scripts/llm_wiki.py ingest appunti-progetto.md
```

`ingest` aggiorna anche:

- `wiki/index.md`;
- `wiki/log.md`.

### query

Cerca nella wiki con scoring lessicale semplice, costruisce un contesto e chiede al modello una risposta operativa:

```bash
python3 -B scripts/llm_wiki.py query "Riassumi la conoscenza disponibile nella wiki"
```

La risposta deve citare i file wiki usati.

### query --save

Salva la risposta in `wiki/outputs/` e aggiorna indice/log:

```bash
python3 -B scripts/llm_wiki.py query "Crea un output operativo basato sulla wiki" --save
```

Puoi indicare un tipo di output:

```bash
python3 -B scripts/llm_wiki.py query "Crea una checklist" --type checklist --save
```

### lint

Analizza la wiki e salva un report operativo in `wiki/outputs/`:

```bash
python3 -B scripts/llm_wiki.py lint
```

Il report copre:

- contraddizioni;
- pagine troppo generiche;
- pagine orfane;
- concetti citati ma non sviluppati;
- output mancanti;
- opportunita operative;
- rischi di allucinazione;
- fonti deboli;
- possibili pagine da creare;
- aree migliorabili.

## Primo test end-to-end

Crea `raw/sources/example.md`:

```md
# Example Knowledge Source

Obiettivo: verificare che la wiki locale trasformi fonti grezze in conoscenza Markdown riutilizzabile.

Contesto: questo file e una fonte neutra di collaudo. Non appartiene a un dominio specifico.

Punti operativi:
- mantenere le fonti originali in raw/sources/;
- generare pagine strutturate in wiki/outputs/;
- aggiornare index e log;
- interrogare la wiki citando i file usati;
- segnalare informazioni mancanti o deboli.

Output attesi: sintesi, checklist, domande aperte e note di manutenzione.
```

Esegui:

```bash
python3 -B scripts/llm_wiki.py init
python3 -B scripts/llm_wiki.py ingest raw/sources/example.md
python3 -B scripts/llm_wiki.py query "Riassumi la conoscenza disponibile nella wiki"
python3 -B scripts/llm_wiki.py query "Crea un output operativo basato sulla wiki" --save
python3 -B scripts/llm_wiki.py lint
```

## Formato delle pagine generate

Ogni pagina wiki generata deve avere frontmatter YAML:

```md
---
title:
type:
source:
created:
updated:
tags:
status: draft
---
```

E queste sezioni:

```md
# Titolo

## Sintesi operativa

## Punti chiave

## Implicazioni pratiche

## Output riutilizzabili

## Collegamenti

## Contraddizioni o rischi

## Domande aperte

## Fonti

## Note di manutenzione
```

## Come usare bene la wiki

Buone fonti producono buoni output. Conviene inserire materiale concreto:

- decisioni gia prese;
- vincoli reali;
- esempi riusciti;
- procedure esistenti;
- criteri di qualita;
- problemi ricorrenti;
- domande frequenti;
- template da riusare.

Evita di ingerire materiale troppo generico, duplicato o non verificabile. Se una fonte e debole, meglio che la wiki lo segnali invece di trasformarla in falsa certezza.

## Manutenzione consigliata

Routine semplice:

1. Aggiungi fonti in `raw/sources/`.
2. Esegui `ingest` sulle fonti nuove.
3. Leggi le pagine generate in `wiki/outputs/`.
4. Correggi o consolida manualmente le pagine importanti.
5. Usa `query --save` per creare output riutilizzabili.
6. Esegui `lint` periodicamente.
7. Sposta o riscrivi a mano le pagine mature in `wiki/entities/`, `wiki/concepts/` o altre sezioni.

## Cosa committare

Per una repo template pubblica conviene committare:

- codice;
- README;
- AGENTS;
- `.env.example`;
- struttura base della wiki;
- eventuali esempi piccoli e neutri, se utili.

Conviene evitare di committare:

- `.env`;
- chiavi API;
- fonti private;
- output generati da test locali;
- materiale cliente o dati sensibili.

## Troubleshooting

### `python: command not found`

Usa `python3`:

```bash
python3 -B scripts/llm_wiki.py init
```

### Ollama non risponde

Avvia Ollama:

```bash
ollama serve
```

Controlla l'host:

```bash
curl http://localhost:11434/api/tags
```

### Modello non trovato

Scaricalo:

```bash
ollama pull qwen2.5:3b
```

### OpenAI non funziona

Verifica `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
```

Poi reinstalla le dipendenze se serve:

```bash
python3 -m pip install -r requirements.txt
```

### Output del modello troppo generico

Migliora la fonte. Aggiungi:

- contesto;
- esempi;
- vincoli;
- obiettivi;
- criteri decisionali;
- dati verificabili;
- output attesi.

## Limiti MVP

- Ricerca locale lessicale, non semantica.
- Nessun embedding.
- Nessun database.
- Nessun frontend.
- Nessun export PDF.
- Nessuna gestione multiutente.
- La qualita dipende dal modello scelto e dalla qualita delle fonti.
- I modelli piccoli possono mischiare lingue o produrre risposte imperfette: usare `lint` e revisionare gli output importanti.

## Prossimi step possibili

- Prompt piu rigidi per lingua e formato.
- Test automatici CLI.
- Profili di progetto separati.
- Template pagina personalizzabili.
- Export PDF.
- Frontend guidato.
- RAG ibrido con embedding locali.
- Supporto multi-wiki o multi-dominio.
