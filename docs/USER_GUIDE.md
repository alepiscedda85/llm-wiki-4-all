# Guida pratica llm-wiki-4-all

Questa guida spiega come usare `llm-wiki-4-all` e come adattarlo a lavori, progetti e domini diversi.

Il progetto e pensato per persone che vogliono trasformare fonti sparse in una wiki Markdown locale, interrogabile e manutenibile.

## 1. Idea base

`llm-wiki-4-all` funziona come una piccola officina di conoscenza:

```text
fonti grezze -> ingest -> pagine wiki -> query -> output operativi -> lint
```

Le fonti restano in `raw/sources/` e non vengono modificate. La conoscenza elaborata viene salvata in `wiki/`.

## 2. Installazione rapida

```bash
git clone https://github.com/alepiscedda85/llm-wiki-4-all.git
cd llm-wiki-4-all
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Installa Ollama e scarica il modello consigliato:

```bash
brew install ollama
ollama serve
ollama pull qwen2.5:3b
```

Inizializza una wiki:

```bash
python3 -B scripts/llm_wiki.py init
```

## 3. Uso base single-wiki

Crea una fonte:

```text
raw/sources/appunti-progetto.md
```

Esempio:

```md
# Appunti progetto

Obiettivo: raccogliere decisioni, procedure e domande aperte in una wiki locale.

Vincoli:
- non modificare le fonti originali;
- salvare output riutilizzabili;
- citare sempre i file usati.

Output desiderati:
- checklist;
- FAQ;
- sintesi operative;
- piano prossime azioni.
```

Ingerisci la fonte:

```bash
python3 -B scripts/llm_wiki.py ingest raw/sources/appunti-progetto.md
```

Interroga la wiki:

```bash
python3 -B scripts/llm_wiki.py query "Riassumi le decisioni operative"
```

Salva un output:

```bash
python3 -B scripts/llm_wiki.py query "Crea una checklist di lavoro" --type checklist --save
```

Esegui lint:

```bash
python3 -B scripts/llm_wiki.py lint
```

## 4. Uso multi-workspace

Un workspace e una wiki separata. Usalo quando vuoi separare lavori, clienti o domini.

Crea un workspace:

```bash
python3 -B scripts/llm_wiki.py init --workspace instances/client-alpha
```

Aggiungi fonti in:

```text
instances/client-alpha/raw/sources/
```

Ingerisci una fonte:

```bash
python3 -B scripts/llm_wiki.py ingest brief.md --workspace instances/client-alpha
```

Query sul workspace:

```bash
python3 -B scripts/llm_wiki.py query "Quali sono le priorita del cliente?" --workspace instances/client-alpha
```

Salva un output nel workspace:

```bash
python3 -B scripts/llm_wiki.py query "Crea una proposta operativa" --type proposta --workspace instances/client-alpha --save
```

## 5. Configurare un workspace

Ogni workspace puo avere un `config.yaml`:

```yaml
name: client-alpha
language: it
provider: ollama
model: qwen2.5:3b
```

La precedenza e:

1. opzioni CLI;
2. `.env`;
3. `workspace/config.yaml`;
4. default interni.

Esempio override modello:

```bash
python3 -B scripts/llm_wiki.py query "Riassumi" --workspace instances/client-alpha --model llama3.2
```

## 6. Usare OpenAI opzionalmente

Di default il progetto usa Ollama. Per OpenAI crea `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
```

Poi usa normalmente la CLI:

```bash
python3 -B scripts/llm_wiki.py query "Riassumi la wiki"
```

## 7. Esempi per lavori diversi

### Consulente o freelance

Fonti utili:

- brief cliente;
- note call;
- preventivi;
- obiettivi;
- vincoli;
- feedback.

Comandi:

```bash
python3 -B scripts/llm_wiki.py init --workspace instances/cliente-rossi
python3 -B scripts/llm_wiki.py ingest brief.md --workspace instances/cliente-rossi
python3 -B scripts/llm_wiki.py query "Crea una proposta di lavoro" --type proposta --workspace instances/cliente-rossi --save
```

Output utili:

- proposta commerciale;
- piano operativo;
- checklist onboarding;
- FAQ cliente;
- rischi e domande aperte.

### Agenzia marketing

Fonti utili:

- audit sito;
- buyer personas;
- campagne precedenti;
- report analytics;
- messaggi approvati;
- competitor.

Comandi:

```bash
python3 -B scripts/llm_wiki.py init --workspace instances/campagna-q3
python3 -B scripts/llm_wiki.py ingest audit-sito.md --workspace instances/campagna-q3
python3 -B scripts/llm_wiki.py query "Crea un piano contenuti di 30 giorni" --type piano-editoriale --workspace instances/campagna-q3 --save
```

Output utili:

- piano editoriale;
- angoli creativi;
- checklist landing page;
- script ads;
- report criticita.

### Studio professionale

Fonti utili:

- procedure interne;
- FAQ clienti;
- normative riassunte manualmente;
- checklist documentale;
- casi ricorrenti.

Comandi:

```bash
python3 -B scripts/llm_wiki.py init --workspace instances/studio-procedure
python3 -B scripts/llm_wiki.py ingest procedura-onboarding.md --workspace instances/studio-procedure
python3 -B scripts/llm_wiki.py query "Crea una checklist per il cliente" --type checklist --workspace instances/studio-procedure --save
```

Output utili:

- checklist operative;
- email template;
- FAQ;
- SOP interne;
- domande mancanti per il cliente.

### Team software

Fonti utili:

- README tecnici;
- decision record;
- issue importanti;
- note architetturali;
- runbook;
- postmortem.

Comandi:

```bash
python3 -B scripts/llm_wiki.py init --workspace instances/software-docs
python3 -B scripts/llm_wiki.py ingest architecture-notes.md --workspace instances/software-docs
python3 -B scripts/llm_wiki.py query "Crea un runbook operativo" --type runbook --workspace instances/software-docs --save
```

Output utili:

- runbook;
- ADR sintetici;
- checklist deploy;
- troubleshooting;
- onboarding developer.

### Ricerca personale o studio

Fonti utili:

- appunti di lettura;
- paper riassunti;
- lezioni;
- domande aperte;
- mappe concettuali.

Comandi:

```bash
python3 -B scripts/llm_wiki.py init --workspace instances/personal-knowledge
python3 -B scripts/llm_wiki.py ingest appunti-libro.md --workspace instances/personal-knowledge
python3 -B scripts/llm_wiki.py query "Crea una scheda di ripasso" --type scheda-studio --workspace instances/personal-knowledge --save
```

Output utili:

- schede studio;
- domande di ripasso;
- sintesi;
- glossario;
- collegamenti tra concetti.

### HR e formazione

Fonti utili:

- job description;
- processi onboarding;
- policy interne;
- materiali formativi;
- feedback colloqui.

Comandi:

```bash
python3 -B scripts/llm_wiki.py init --workspace instances/hr-training
python3 -B scripts/llm_wiki.py ingest onboarding.md --workspace instances/hr-training
python3 -B scripts/llm_wiki.py query "Crea un percorso onboarding" --type piano-formazione --workspace instances/hr-training --save
```

Output utili:

- piano onboarding;
- checklist manager;
- FAQ nuovo assunto;
- template colloquio;
- matrice competenze.

## 8. Come scrivere buone fonti

Una buona fonte contiene:

- contesto;
- obiettivo;
- vincoli;
- dati verificabili;
- esempi;
- output desiderati;
- domande aperte.

Template fonte:

```md
# Titolo fonte

## Contesto

## Obiettivo

## Vincoli

## Informazioni disponibili

## Esempi o casi reali

## Output desiderati

## Domande aperte
```

## 9. Routine consigliata

1. Crea o scegli un workspace.
2. Aggiungi fonti in `raw/sources/`.
3. Esegui `ingest`.
4. Leggi e correggi gli output importanti.
5. Usa `query --save` per produrre asset riutilizzabili.
6. Esegui `lint`.
7. Sposta manualmente le pagine mature in `entities/` o `concepts/`.

## 10. Cosa non fare

- Non inserire chiavi API in git.
- Non usare fonti private in repo pubbliche.
- Non fidarti ciecamente degli output del modello.
- Non usare la wiki come unica fonte di verita legale, medica o finanziaria.
- Non mischiare clienti o domini nello stesso workspace se devono restare separati.

## 11. Checklist di avvio

```text
[ ] Ho installato Python 3.11+
[ ] Ho installato le dipendenze
[ ] Ho installato Ollama o configurato OpenAI
[ ] Ho creato un workspace
[ ] Ho aggiunto almeno una fonte in raw/sources/
[ ] Ho eseguito ingest
[ ] Ho fatto una query
[ ] Ho salvato un output utile
[ ] Ho eseguito lint
```
