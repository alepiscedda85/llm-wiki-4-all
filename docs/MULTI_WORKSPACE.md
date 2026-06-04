# Multi-workspace

La multi-wiki si basa sul concetto di workspace.

Un workspace e una cartella autonoma con fonti, istruzioni, configurazione, indice, log e output separati.

## Perche usare piu workspace

Usa piu workspace quando vuoi separare:

- progetti diversi;
- clienti diversi;
- domini diversi;
- esperimenti;
- knowledge base personali e lavorative;
- istruzioni `AGENTS.md` differenti.

## Struttura workspace

```text
instances/example/
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

## Creare un workspace

```bash
python3 -B scripts/llm_wiki.py init --workspace instances/example
```

Il comando crea file e cartelle mancanti senza sovrascrivere contenuti esistenti.

## Aggiungere fonti

Aggiungi file `.md` o `.txt` in:

```text
instances/example/raw/sources/
```

Esempio:

```text
instances/example/raw/sources/example.md
```

## Ingest

Puoi indicare il path completo relativo al workspace:

```bash
python3 -B scripts/llm_wiki.py ingest raw/sources/example.md --workspace instances/example
```

Oppure solo il nome file:

```bash
python3 -B scripts/llm_wiki.py ingest example.md --workspace instances/example
```

La CLI cerca in questo ordine:

1. path assoluto, se fornito;
2. path relativo al workspace;
3. path relativo a `workspace/raw/sources/`.

## Query

```bash
python3 -B scripts/llm_wiki.py query "Riassumi la wiki" --workspace instances/example
```

La query cerca solo in `instances/example/wiki/`.

## Salvare output

```bash
python3 -B scripts/llm_wiki.py query "Crea una checklist" --type checklist --workspace instances/example --save
```

La risposta viene salvata in:

```text
instances/example/wiki/outputs/
```

## Lint

```bash
python3 -B scripts/llm_wiki.py lint --workspace instances/example
```

Il report viene salvato in:

```text
instances/example/wiki/outputs/lint-YYYY-MM-DD.md
```

## AGENTS.md per workspace

La lettura istruzioni segue questa priorita:

1. `workspace/AGENTS.md`;
2. `AGENTS.md` della root progetto;
3. fallback interno minimale.

## config.yaml per workspace

Ogni workspace puo personalizzare:

```yaml
name: personal-knowledge
language: it
provider: ollama
model: qwen2.5:3b
```

Precedenza:

1. CLI;
2. `.env`;
3. `workspace/config.yaml`;
4. default interni.

## Regola importante

Non spostare fonti tra workspace automaticamente. Non copiare output tra workspace automaticamente. La separazione e una caratteristica del prodotto.
