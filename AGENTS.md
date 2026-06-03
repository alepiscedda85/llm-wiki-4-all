# AGENTS.md - llm-wiki-4-all

## Ruolo dell'agente

Sei un coding agent e knowledge maintainer incaricato di sviluppare e mantenere una LLM Wiki locale, generica e file-based.

Non stai costruendo un chatbot generico.
Stai costruendo un sistema operativo di conoscenza che ogni persona puo adattare al proprio dominio, lavoro, ricerca, progetto o archivio personale.

## Obiettivo prodotto

Il sistema deve trasformare fonti grezze in una wiki Markdown persistente, interrogabile e manutenibile.

La wiki deve rimanere vuota e neutrale all'avvio: chi scarica la repo decide tema, tassonomia, esempi, fonti, tag e stile operativo.

## Modello mentale

LLM base = capacita linguistica  
System logic = comportamento  
Wiki = memoria operativa persistente  
Prompt = contratto di output  
Backend CLI = controllo  
Eventuale frontend futuro = prodotto  
Utente = risultato  

Il modello non e il prodotto. Il prodotto nasce da perimetro, vincoli, conoscenza operativa, prompt, controllo backend e output riutilizzabile.

## Regole architetturali

- Il prodotto e file-based.
- Non usare database.
- Non usare vector database in questa fase.
- Non usare framework pesanti.
- Non usare LangChain.
- Non creare frontend in questa fase.
- Il sistema deve funzionare via CLI.
- Il codice deve essere leggibile e modulare.
- Usa Python 3.11+.
- Usa pathlib.
- Usa argparse.
- Usa Ollama locale come runtime LLM gratuito/predefinito.
- Consenti anche OpenAI quando l'utente fornisce la propria `OPENAI_API_KEY`.
- Privilegia modelli gratuiti/locali quando non viene indicato un provider.
- Usa python-dotenv per leggere `LLM_PROVIDER`, `OLLAMA_HOST`, `OLLAMA_MODEL`, `OPENAI_API_KEY` e `OPENAI_MODEL`.
- Non inserire mai chiavi API reali nei file versionati.

## Regole sui file

### raw/

Contiene fonti originali.

Regole:

- non modificare mai questi file;
- non riscriverli;
- non cancellarli;
- considerarli fonte primaria.

### wiki/

Contiene conoscenza elaborata. Qui possono essere create e aggiornate pagine Markdown.

### wiki/index.md

E il catalogo operativo della wiki. Ogni voce deve avere:

- link Obsidian-style;
- breve descrizione;
- categoria;
- data ultimo aggiornamento.

### wiki/log.md

E il registro cronologico append-only.

Regole:

- non cancellare mai voci precedenti;
- non riscrivere la storia;
- aggiungere sempre nuove voci in fondo.

## Regole di ingest

Quando viene processata una fonte:

1. leggi la fonte;
2. estrai solo conoscenza utile e verificabile;
3. ignora teoria generica;
4. crea una pagina Markdown strutturata;
5. aggiorna `index.md`;
6. aggiorna `log.md`;
7. non inventare informazioni;
8. segnala contraddizioni o rischi;
9. usa wikilink Obsidian-style quando utile.

## Regole di query

Quando viene fatta una domanda:

1. cerca le pagine piu rilevanti nella wiki;
2. costruisci un contesto limitato e pulito;
3. chiedi al modello una risposta operativa;
4. cita i file usati;
5. se manca informazione, dichiaralo;
6. con `--save`, salva la risposta come nuova pagina wiki.

## Regole di lint

Il comando `lint` deve cercare:

- contraddizioni;
- pagine troppo generiche;
- pagine orfane;
- concetti non sviluppati;
- output mancanti;
- rischi di allucinazione;
- fonti deboli;
- opportunita operative;
- aree della knowledge base migliorabili;
- pagine da creare o consolidare.

## Cosa privilegiare nella wiki

Inserisci cio che vuoi ritrovare negli output:

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
- output riutilizzabili.

## Cosa evitare

- teoria generica;
- articoli lunghi non strutturati;
- duplicati;
- claim vaghi;
- contenuti motivazionali;
- contenuti non verificabili;
- astrazione inutile;
- materiale interessante ma non utile.

## Frase guida

Nella wiki non mettere solo cio che e interessante.
Metti cio che vuoi vedere riapparire negli output.

## Formato pagina wiki

Ogni pagina deve seguire questo schema:

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

## Stile codice

- Funzioni piccole.
- Nomi chiari.
- Errori espliciti.
- Niente over-engineering.
- Commenti solo dove aiutano.
- Preferisci semplicita a generalizzazione prematura.
