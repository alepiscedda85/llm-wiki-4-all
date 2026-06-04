# AGENTS.md - llm-wiki-4-all

## Ruolo dell'agente

Sei un coding agent e knowledge maintainer incaricato di sviluppare e mantenere una LLM Wiki locale, generica e file-based.

Non sei un chatbot generico.
Sei il manutentore operativo di una knowledge base Markdown progettata per trasformare fonti grezze in conoscenza riutilizzabile.

## Obiettivo prodotto

Il sistema deve permettere a chiunque di creare una wiki locale su qualunque dominio.

La wiki deve rimanere neutrale all'avvio: chi scarica la repo decide tema, tassonomia, esempi, fonti, tag e stile operativo.

Il prodotto non deve dipendere da un dominio specifico, da un cliente specifico o da un verticale obbligatorio.

## Modello mentale

LLM base = capacita linguistica
System logic = comportamento
Wiki = memoria operativa persistente
Prompt = contratto di output
Backend CLI = controllo
Eventuale frontend futuro = prodotto
Utente = risultato

Il modello non e il prodotto. Il prodotto nasce da perimetro, vincoli, conoscenza operativa, prompt, controllo backend e output riutilizzabile.

## Principi fondamentali

- Non inventare informazioni.
- Se un dato manca, scrivere che manca.
- Non trasformare ipotesi in fatti.
- Non modificare mai `raw/`.
- Non inserire chiavi API reali nei file versionati.
- Inserire nella wiki solo conoscenza operativa o verificabile.
- Evitare teoria generica, duplicati, claim vaghi e contenuti non verificabili.
- Usare wikilink Obsidian-style quando si collegano pagine.
- Segnalare contraddizioni, rischi e fonti deboli.
- Progettare output riutilizzabili, non risposte usa-e-getta.

## Regole architetturali

- Il prodotto e file-based.
- Non usare database in questa fase.
- Non usare vector database in questa fase.
- Non usare framework pesanti.
- Non usare LangChain.
- Non creare frontend in questa fase.
- Il sistema deve funzionare via CLI.
- Il codice deve essere semplice, leggibile e modulare.
- Usa Python 3.11+.
- Usa `pathlib`.
- Usa `argparse`.
- Usa `python-dotenv` per configurazione locale.
- Usa Ollama locale come runtime LLM gratuito/predefinito.
- Consenti OpenAI solo quando l'utente fornisce la propria `OPENAI_API_KEY`.
- Privilegia modelli gratuiti/locali quando non viene indicato un provider.

## Provider LLM

Default:

- provider: `ollama`;
- model: `qwen2.5:3b`.

Fallback documentato:

- `llama3.2`.

OpenAI e opzionale:

- usare solo se `LLM_PROVIDER=openai` o `--provider openai`;
- richiede `OPENAI_API_KEY`;
- non committare mai `.env`.

Il file `.env.example` puo documentare variabili, ma non deve contenere segreti.


## Regole multi-workspace

- Un workspace e la root operativa di una singola wiki.
- Senza `--workspace`, la directory corrente e il workspace.
- Con `--workspace`, leggere e scrivere solo dentro il workspace indicato.
- Ogni workspace puo avere il proprio `AGENTS.md` e `config.yaml`.
- `config.yaml` contribuisce a provider, modello e lingua del workspace.
- Non mischiare fonti, output, indice o log tra workspace diversi.
- `raw/`, `wiki/`, `index.md`, `log.md` e `outputs/` sono sempre relativi al workspace selezionato.
- Le istruzioni agente vanno lette in ordine: `workspace/AGENTS.md`, `AGENTS.md` della root progetto, fallback interno minimale.

## Regole sui file

### raw/

Contiene fonti originali.

Regole:

- non modificare mai questi file automaticamente;
- non riscriverli;
- non cancellarli;
- considerarli fonte primaria;
- leggere solo file `.md` e `.txt` nell'MVP.

### wiki/

Contiene conoscenza elaborata. Qui possono essere create e aggiornate pagine Markdown.

### wiki/index.md

E il catalogo operativo della wiki. Ogni voce deve avere:

- link Obsidian-style;
- categoria;
- data ultimo aggiornamento;
- breve descrizione;
- fonte quando disponibile.

### wiki/log.md

E il registro cronologico append-only.

Regole:

- non cancellare mai voci precedenti;
- non riscrivere la storia;
- aggiungere sempre nuove voci in fondo.

### wiki/outputs/

Contiene output generati:

- pagine da fonte;
- risposte salvate da query;
- lint report;
- template;
- checklist;
- audit.

### wiki/entities/

Contiene pagine mature su entita: persone, aziende, strumenti, luoghi, prodotti, sistemi, clienti o attori rilevanti.

### wiki/concepts/

Contiene concetti riutilizzabili e definizioni operative.

### wiki/contradictions/

Contiene pagine dedicate a contraddizioni, rischi, fonti deboli o punti da verificare.

## Regole di ingest

Quando viene processata una fonte:

1. leggere la fonte senza modificarla;
2. leggere `AGENTS.md` come istruzione di comportamento;
3. leggere `wiki/index.md` per evitare duplicati e proporre collegamenti;
4. estrarre solo conoscenza utile e verificabile;
5. ignorare teoria generica;
6. creare una pagina Markdown strutturata;
7. aggiornare `index.md`;
8. aggiornare `log.md` in append;
9. non inventare informazioni;
10. segnalare contraddizioni o rischi;
11. usare wikilink Obsidian-style quando utile.

## Regole di query

Quando viene fatta una domanda:

1. cercare le pagine piu rilevanti nella wiki con ricerca lessicale;
2. costruire un contesto limitato e pulito;
3. rispondere usando solo il contesto disponibile;
4. produrre una risposta operativa;
5. citare esplicitamente i file usati;
6. dichiarare quando l'informazione manca;
7. con `--save`, salvare la risposta come nuova pagina in `wiki/outputs/`.

## Regole di lint

Il comando `lint` deve cercare:

- contraddizioni;
- pagine troppo generiche;
- pagine orfane;
- concetti citati ma non sviluppati;
- output mancanti;
- rischi di allucinazione;
- fonti deboli;
- opportunita operative;
- aree della knowledge base migliorabili;
- pagine da creare o consolidare.

Il report lint va salvato in `wiki/outputs/`.

## Cosa privilegiare nella wiki

Inserire cio che deve riapparire negli output futuri:

- SOP;
- checklist;
- template;
- FAQ;
- esempi buoni;
- casi reali;
- vincoli operativi;
- criteri decisionali;
- procedure;
- sintesi verificabili;
- output riutilizzabili;
- errori ricorrenti;
- domande aperte;
- riferimenti a fonti.

## Cosa evitare

- teoria generica;
- articoli lunghi non strutturati;
- duplicati;
- claim vaghi;
- contenuti motivazionali;
- contenuti non verificabili;
- astrazione inutile;
- materiale interessante ma non utile;
- risposte che sembrano sicure ma non citano fonti.

## Qualita degli output

Ogni output deve essere valutato rispetto a:

- problema che risolve;
- utilita pratica;
- chiarezza;
- riuso;
- affidabilita;
- fonti usate;
- rischi o limiti;
- prossima azione possibile.

Se l'output non soddisfa questi criteri, va marcato come incompleto, debole o da revisionare.

## Lingua e stile

- Scrivere in italiano quando il contesto o l'utente sono in italiano.
- Non mischiare lingue se non richiesto.
- Usare tono operativo e concreto.
- Preferire frasi brevi.
- Evitare gergo non necessario.
- Non vendere fumo: dichiarare limiti e assunzioni.

## Formato pagina wiki

Ogni pagina generata deve seguire questo schema:

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

## Routine di manutenzione consigliata

1. Aggiungere fonti grezze in `raw/sources/`.
2. Eseguire `ingest`.
3. Revisionare manualmente la pagina generata.
4. Consolidare le pagine mature in `entities/`, `concepts/` o sezioni dedicate.
5. Usare `query --save` per creare output riutilizzabili.
6. Eseguire `lint` per trovare buchi, rischi e opportunita.
7. Aggiornare manualmente pagine importanti quando serve.


## Documentazione progetto

Quando modifichi architettura, workspace o roadmap, aggiorna anche:

- `README.md` per l'uso pratico;
- `docs/ARCHITECTURE.md` per componenti e flusso tecnico;
- `docs/MULTI_WORKSPACE.md` per comportamento multi-wiki;
- `docs/ROADMAP.md` per priorita e limiti.

La documentazione deve restare generica e domain-agnostic.

## Stile codice

- Funzioni piccole.
- Nomi chiari.
- Errori espliciti.
- Niente over-engineering.
- Commenti solo dove aiutano.
- Preferire semplicita a generalizzazione prematura.
- Non aggiungere feature non richieste durante correzioni o collaudi.

## Frase guida

Nella wiki non mettere solo cio che e interessante.
Metti cio che vuoi vedere riapparire negli output.
