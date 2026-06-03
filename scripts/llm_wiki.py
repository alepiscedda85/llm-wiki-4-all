#!/usr/bin/env python3
"""Local Markdown wiki maintainer powered by Ollama or OpenAI."""

from __future__ import annotations

import argparse
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

try:
    import requests
except ModuleNotFoundError:  # pragma: no cover - exercised before dependencies install.
    requests = None

# Le dipendenze LLM sono opzionali a import-time: `init` deve funzionare anche
# prima che l'utente abbia eseguito `pip install -r requirements.txt`.
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - .env support is optional until install.
    load_dotenv = None

try:
    from openai import OpenAI
except ModuleNotFoundError:  # pragma: no cover - OpenAI is optional unless selected.
    OpenAI = None


# Tutti i path sono calcolati dalla posizione dello script, cosi la CLI puo
# essere lanciata dalla root del progetto senza configurazione aggiuntiva.
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "raw"
SOURCES_DIR = RAW_DIR / "sources"
WIKI_DIR = ROOT / "wiki"
OUTPUTS_DIR = WIKI_DIR / "outputs"
CONTRADICTIONS_DIR = WIKI_DIR / "contradictions"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"
OVERVIEW_FILE = WIKI_DIR / "overview.md"
AGENTS_FILE = ROOT / "AGENTS.md"

DEFAULT_PROVIDER = "ollama"
DEFAULT_OLLAMA_MODEL = "qwen2.5:3b"
DEFAULT_OPENAI_MODEL = "gpt-5.2"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
SUPPORTED_EXTENSIONS = {".md", ".txt"}
MAX_SOURCE_CHARS = 45_000
MAX_CONTEXT_CHARS = 30_000


# Schema standard delle pagine generate. Mantenerlo stabile rende la wiki facile
# da leggere in Obsidian, GitHub o qualunque editor Markdown.
PAGE_SECTIONS = [
    "Sintesi operativa",
    "Punti chiave",
    "Implicazioni pratiche",
    "Output riutilizzabili",
    "Collegamenti",
    "Contraddizioni o rischi",
    "Domande aperte",
    "Fonti",
    "Note di manutenzione",
]


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def today_iso() -> str:
    return datetime.now().date().isoformat()


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def slugify(value: str, fallback: str = "pagina") -> str:
    """Crea nomi file leggibili e stabili a partire dai titoli generati."""
    value = value.lower().strip()
    replacements = {
        "à": "a",
        "è": "e",
        "é": "e",
        "ì": "i",
        "ò": "o",
        "ù": "u",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:80].strip("-") or fallback


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def append_log(action: str, detail: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(f"- {now_iso()} | {action} | {detail}\n")


def wiki_link(path: Path) -> str:
    relative = path.relative_to(WIKI_DIR).with_suffix("")
    return f"[[{relative.as_posix()}]]"


def update_index(
    title: str,
    path: Path,
    page_type: str,
    source: str = "",
    description: str = "",
) -> None:
    """Aggiunge una pagina all'indice senza duplicare wikilink gia presenti."""
    ensure_initialized()
    link = wiki_link(path)
    updated = today_iso()
    clean_description = description or title
    entry = (
        f"- {link} - categoria: {page_type} - aggiornato: {updated} "
        f"- descrizione: {clean_description}"
    )
    if source:
        entry += f" - fonte: `{source}`"

    current = read_text(INDEX_FILE)
    if link in current:
        return

    with INDEX_FILE.open("a", encoding="utf-8") as handle:
        handle.write(f"{entry}\n")


def ensure_initialized() -> None:
    if not WIKI_DIR.exists() or not INDEX_FILE.exists() or not LOG_FILE.exists():
        raise SystemExit(
            "Wiki non inizializzata. Esegui prima: python scripts/llm_wiki.py init"
        )


def base_frontmatter(title: str, page_type: str, source: str, tags: list[str] | None = None) -> str:
    created = today_iso()
    tag_text = ", ".join(tags or [])
    return (
        "---\n"
        f"title: {title}\n"
        f"type: {page_type}\n"
        f"source: {source}\n"
        f"created: {created}\n"
        f"updated: {created}\n"
        f"tags: [{tag_text}]\n"
        "status: draft\n"
        "---\n\n"
    )


def empty_page(title: str, page_type: str, source: str, tags: list[str] | None = None) -> str:
    sections = "\n\n".join(f"## {section}\n" for section in PAGE_SECTIONS)
    return f"{base_frontmatter(title, page_type, source, tags)}# {title}\n\n{sections}\n"


def init_project(_: argparse.Namespace) -> None:
    """Crea la struttura minima senza sovrascrivere contenuti esistenti."""
    for directory in [
        SOURCES_DIR,
        WIKI_DIR / "entities",
        WIKI_DIR / "concepts",
        OUTPUTS_DIR,
        CONTRADICTIONS_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    defaults = {
        INDEX_FILE: (
            "# llm-wiki-4-all\n\n"
            "Indice operativo della knowledge base.\n\n"
            "## Pagine principali\n\n"
            "- [[overview]] - categoria: overview - aggiornato: "
            f"{today_iso()} - descrizione: introduzione alla wiki\n\n"
            "## Pagine generate\n\n"
        ),
        LOG_FILE: "# Log manutenzione wiki\n\nRegistro cronologico append-only.\n\n",
        OVERVIEW_FILE: empty_page(
            "Overview",
            "overview",
            "init",
            ["wiki"],
        ),
    }

    for path, content in defaults.items():
        write_if_missing(path, content)

    append_log("init", "struttura verificata")
    print("LLM Wiki inizializzata.")


def load_environment() -> None:
    if load_dotenv:
        load_dotenv(ROOT / ".env")


def ollama_host() -> str:
    load_environment()
    return os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_HOST).rstrip("/")


def selected_provider(args: argparse.Namespace) -> str:
    load_environment()
    provider = args.provider or args.global_provider or os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER)
    if provider != "auto":
        return provider
    # `auto` e comodo nei fork: chi inserisce OPENAI_API_KEY usa OpenAI,
    # chi non la inserisce resta sul percorso gratuito locale con Ollama.
    return "openai" if os.getenv("OPENAI_API_KEY") else "ollama"


def selected_model(args: argparse.Namespace) -> str:
    if args.model:
        return args.model
    if args.global_model:
        return args.global_model
    provider = selected_provider(args)
    if provider == "openai":
        return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    return os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def call_llm(prompt: str, args: argparse.Namespace, system: str | None = None) -> str:
    """Instrada la richiesta verso il provider scelto mantenendo invariati i prompt."""
    provider = selected_provider(args)
    model = selected_model(args)
    if provider == "openai":
        return call_openai(prompt, model, system)
    return call_ollama(prompt, model, system)


def call_ollama(prompt: str, model: str, system: str | None = None) -> str:
    if requests is None:
        raise SystemExit(
            "Dipendenza mancante: requests. Installa con `pip install -r requirements.txt`."
        )

    # Ollama usa una API HTTP locale; `stream=False` semplifica la CLI MVP.
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 32768,
        },
    }
    if system:
        payload["system"] = system

    url = f"{ollama_host()}/api/generate"
    try:
        response = requests.post(url, json=payload, timeout=300)
    except requests.ConnectionError as exc:
        raise SystemExit(
            "Ollama non risponde. Avvialo con `ollama serve` e verifica OLLAMA_HOST."
        ) from exc
    except requests.Timeout as exc:
        raise SystemExit("Timeout durante la chiamata a Ollama.") from exc

    if response.status_code == 404:
        raise SystemExit(
            f"Modello `{model}` non trovato o API Ollama non disponibile. "
            f"Esegui: ollama pull {model}"
        )
    if response.status_code >= 400:
        raise SystemExit(f"Errore Ollama {response.status_code}: {response.text}")

    data = response.json()
    text = data.get("response", "").strip()
    if not text:
        raise SystemExit("Ollama ha restituito una risposta vuota.")
    return text


def call_openai(prompt: str, model: str, system: str | None = None) -> str:
    load_environment()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "Manca OPENAI_API_KEY. Crea un file .env o esporta la variabile."
        )
    if OpenAI is None:
        raise SystemExit(
            "Dipendenza mancante: openai. Installa con `pip install -r requirements.txt`."
        )

    client = OpenAI()
    try:
        # Responses API: AGENTS.md va in `instructions`, il prompt specifico
        # del comando va in `input`.
        response = client.responses.create(
            model=model,
            instructions=system,
            input=prompt,
        )
    except Exception as exc:
        raise SystemExit(f"Errore OpenAI: {exc}") from exc

    text = getattr(response, "output_text", "").strip()
    if not text:
        raise SystemExit("OpenAI ha restituito una risposta vuota.")
    return text


def maintainer_system_prompt() -> str:
    fallback = (
        "Sei il manutentore operativo di llm-wiki-4-all, una LLM Wiki Markdown locale. "
        "Non sei un chatbot generico. Non inventare informazioni. Se un dato manca, "
        "scrivi che manca. Privilegia SOP, checklist, template, FAQ, esempi, vincoli "
        "operativi, casi reali e output riutilizzabili. Evita teoria generica e claim vaghi. "
        "Usa wikilink Obsidian-style quando proponi collegamenti."
    )
    if AGENTS_FILE.exists():
        return read_text(AGENTS_FILE)
    return fallback


def source_prompt(source_path: Path, source_text: str, index_text: str) -> str:
    """Costruisce il contratto di output per trasformare una fonte in pagina wiki."""
    truncated = source_text[:MAX_SOURCE_CHARS]
    return f"""Trasforma questa fonte grezza in una pagina wiki Markdown operativa.

Regole:
- Restituisci solo Markdown.
- Non inventare informazioni.
- Se una sezione non ha dati sufficienti, scrivi "Non disponibile nella fonte."
- Usa wikilink Obsidian-style nella sezione Collegamenti quando utile.
- Mantieni esattamente il frontmatter YAML e le sezioni richieste.
- Orienta il contenuto a conoscenza operativa, riuso pratico e decisioni concrete.
- Usa l'indice esistente per evitare duplicati e proporre collegamenti coerenti.
- Se la fonte e debole, generica o non verificabile, segnalalo chiaramente.

Frontmatter da compilare:
---
title:
type: output
source: {source_path.as_posix()}
created: {today_iso()}
updated: {today_iso()}
tags: []
status: draft
---

Sezioni obbligatorie:
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

Fonte:
```text
{truncated}
```

Indice wiki attuale:
```md
{index_text[:12000]}
```
"""


def extract_title(markdown: str, fallback: str) -> str:
    frontmatter_title = re.search(r"^title:\s*(.+)$", markdown, flags=re.MULTILINE)
    if frontmatter_title and frontmatter_title.group(1).strip():
        return frontmatter_title.group(1).strip().strip('"')
    heading = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
    if heading:
        return heading.group(1).strip()
    return fallback


def normalize_generated_page(markdown: str, source: str, fallback_title: str) -> tuple[str, str]:
    """Garantisce che ogni output salvato abbia almeno una pagina Markdown valida."""
    title = extract_title(markdown, fallback_title)
    if markdown.startswith("---"):
        return markdown.rstrip() + "\n", title
    return empty_page(title, "output", source, ["llm-wiki"]) + "\n" + markdown.rstrip() + "\n"


def resolve_source_path(source: str) -> Path:
    """Cerca prima il path indicato e poi raw/sources/, senza modificare raw/."""
    requested = Path(source)
    candidates = []
    if requested.is_absolute():
        candidates.append(requested)
    else:
        candidates.append((ROOT / requested).resolve())
        candidates.append((SOURCES_DIR / requested).resolve())

    for candidate in candidates:
        if candidate.exists():
            return candidate

    tried = "\n".join(f"- {candidate}" for candidate in candidates)
    raise SystemExit(f"File sorgente non trovato. Path provati:\n{tried}")


def command_ingest(args: argparse.Namespace) -> None:
    ensure_initialized()
    source_path = resolve_source_path(args.source)

    if source_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise SystemExit("Formato non supportato. Usa file .md o .txt.")
    try:
        source_path.relative_to(RAW_DIR)
    except ValueError:
        pass

    source_text = read_text(source_path)
    if not source_text.strip():
        raise SystemExit("La fonte e vuota.")

    fallback_title = source_path.stem.replace("-", " ").replace("_", " ").title()
    index_text = read_text(INDEX_FILE)
    generated = call_llm(
        source_prompt(source_path, source_text, index_text),
        args,
        maintainer_system_prompt(),
    )
    page, title = normalize_generated_page(generated, source_path.as_posix(), fallback_title)
    target = unique_path(OUTPUTS_DIR / f"{slugify(title)}.md")
    target.write_text(page, encoding="utf-8")

    update_index(
        title,
        target,
        "output",
        source_path.as_posix(),
        "pagina generata da fonte grezza",
    )
    append_log("ingest", f"{source_path.as_posix()} -> {target.relative_to(ROOT).as_posix()}")
    print(f"Pagina creata: {target.relative_to(ROOT).as_posix()}")


def unique_path(path: Path) -> Path:
    """Evita sovrascritture aggiungendo un suffisso numerico quando serve."""
    if not path.exists():
        return path
    stem = path.stem
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise SystemExit(f"Impossibile creare un nome file unico per {path}")


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9àèéìòù]+", text.lower())


def wiki_markdown_files() -> list[Path]:
    if not WIKI_DIR.exists():
        return []
    return sorted(path for path in WIKI_DIR.rglob("*.md") if path.is_file())


def score_file(query_terms: Counter[str], path: Path) -> tuple[int, Path, str]:
    text = read_text(path)
    terms = Counter(tokenize(text))
    score = sum(terms[term] * weight for term, weight in query_terms.items())
    return score, path, text


def relevant_context(question: str, limit: int = 6) -> tuple[str, list[str]]:
    """Seleziona pagine rilevanti con scoring lessicale semplice, senza database."""
    query_terms = Counter(tokenize(question))
    if not query_terms:
        return "", []

    scored = [score_file(query_terms, path) for path in wiki_markdown_files()]
    selected = [item for item in sorted(scored, key=lambda item: item[0], reverse=True) if item[0] > 0]
    chunks = []
    files = []
    used = 0
    for _, path, text in selected[:limit]:
        relative = path.relative_to(WIKI_DIR).as_posix()
        excerpt = text[:6000]
        chunk = f"\n\n---\nFILE: {relative}\n{excerpt}"
        if used + len(chunk) > MAX_CONTEXT_CHARS:
            break
        chunks.append(chunk)
        files.append(relative)
        used += len(chunk)
    return "".join(chunks), files


def query_prompt(
    question: str,
    context: str,
    context_files: list[str],
    index_text: str,
) -> str:
    """Costruisce il prompt di risposta usando solo il contesto locale selezionato."""
    return f"""Rispondi alla domanda usando solo il contesto della wiki locale.

Regole:
- Se il contesto non basta, dillo chiaramente.
- Produci una risposta operativa, vendibile e riutilizzabile.
- Evidenzia assunzioni, rischi e prossime azioni.
- Cita esplicitamente i file wiki usati nella sezione "File wiki usati".
- Usa wikilink Obsidian-style quando citi pagine della wiki.

File wiki selezionati:
{format_file_list(context_files)}

Indice wiki:
```md
{index_text[:12000]}
```

Domanda:
{question}

Contesto wiki:
{context or "Nessun contesto rilevante trovato."}
"""


def command_query(args: argparse.Namespace) -> None:
    ensure_initialized()
    context, context_files = relevant_context(args.question)
    index_text = read_text(INDEX_FILE)
    answer = call_llm(
        query_prompt(args.question, context, context_files, index_text),
        args,
        maintainer_system_prompt(),
    )
    print(answer)

    if args.save:
        title = f"Query - {args.question[:80]}"
        target = unique_path(OUTPUTS_DIR / f"query-{now_stamp()}-{slugify(args.question)}.md")
        page = (
            base_frontmatter(title, "query-output", "query", ["query", "output"])
            + f"# {title}\n\n"
            + f"## Domanda\n\n{args.question}\n\n"
            + "## Risposta operativa\n\n"
            + answer.rstrip()
            + "\n\n## File wiki usati\n\n"
            + format_file_list(context_files)
            + "\n\n## Contesto usato\n\n"
            + (context.strip() or "Nessun contesto rilevante trovato.")
            + "\n"
        )
        target.write_text(page, encoding="utf-8")
        update_index(title, target, "query-output", "query", "risposta salvata da query")
        append_log("query-save", target.relative_to(ROOT).as_posix())
        print(f"\nRisposta salvata: {target.relative_to(ROOT).as_posix()}")


def lint_prompt(context: str) -> str:
    """Chiede al modello un audit operativo della wiki corrente."""
    return f"""Analizza questa wiki Markdown come manutentore operativo.

Produci un report in Markdown con sezioni:
# Lint report

## Contraddizioni
## Pagine troppo generiche
## Pagine orfane
## Concetti citati ma non sviluppati
## Output mancanti
## Opportunita operative
## Rischi di allucinazione
## Fonti deboli
## Possibili pagine da creare
## Aree della knowledge base migliorabili
## Azioni prioritarie

Regole:
- Non inventare evidenze.
- Cita i file quando individui un problema.
- Valuta sempre problema, utilita pratica, riuso e affidabilita.

Contesto wiki:
{context or "Wiki vuota o senza contenuto rilevante."}
"""


def full_wiki_context() -> str:
    """Compatta la wiki in un contesto limitato per il comando lint."""
    chunks = []
    used = 0
    for path in wiki_markdown_files():
        relative = path.relative_to(WIKI_DIR).as_posix()
        text = read_text(path)
        chunk = f"\n\n---\nFILE: {relative}\n{text[:5000]}"
        if used + len(chunk) > MAX_CONTEXT_CHARS:
            break
        chunks.append(chunk)
        used += len(chunk)
    return "".join(chunks)


def command_lint(args: argparse.Namespace) -> None:
    ensure_initialized()
    report = call_llm(
        lint_prompt(full_wiki_context()),
        args,
        maintainer_system_prompt(),
    )
    title = f"Lint report {today_iso()}"
    target = unique_path(OUTPUTS_DIR / f"lint-{today_iso()}.md")
    page = base_frontmatter(title, "lint-report", "wiki", ["lint", "rischi"]) + report.rstrip() + "\n"
    target.write_text(page, encoding="utf-8")
    update_index(title, target, "lint-report", "wiki", "report qualita wiki")
    append_log("lint", target.relative_to(ROOT).as_posix())
    print(report)
    print(f"\nReport salvato: {target.relative_to(ROOT).as_posix()}")


def build_parser() -> argparse.ArgumentParser:
    """Definisce l'interfaccia CLI pubblica."""
    parser = argparse.ArgumentParser(
        description="llm-wiki-4-all - CLI locale con Ollama o OpenAI"
    )
    parser.add_argument(
        "--provider",
        dest="global_provider",
        choices=["auto", "ollama", "openai"],
        default=None,
        help="Provider LLM. Default: ollama. Usa openai con OPENAI_API_KEY.",
    )
    parser.add_argument(
        "--model",
        dest="global_model",
        default=None,
        help=(
            f"Modello LLM. Default Ollama: {DEFAULT_OLLAMA_MODEL}; "
            f"default OpenAI: {DEFAULT_OPENAI_MODEL}."
        ),
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_model_argument(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "--provider",
            choices=["auto", "ollama", "openai"],
            default=None,
            help="Provider LLM per questo comando.",
        )
        subparser.add_argument(
            "--model",
            default=None,
            help=(
                f"Modello LLM. Default Ollama: {DEFAULT_OLLAMA_MODEL}; "
                f"default OpenAI: {DEFAULT_OPENAI_MODEL}."
            ),
        )

    init_parser = subparsers.add_parser("init", help="Crea struttura e file base")
    init_parser.set_defaults(func=init_project)

    ingest_parser = subparsers.add_parser("ingest", help="Ingerisce una fonte .md o .txt")
    ingest_parser.add_argument("source", help="Path fonte, es. raw/sources/offerta.md")
    add_model_argument(ingest_parser)
    ingest_parser.set_defaults(func=command_ingest)

    query_parser = subparsers.add_parser("query", help="Interroga la wiki locale")
    query_parser.add_argument("question", help="Domanda operativa")
    query_parser.add_argument("--save", action="store_true", help="Salva la risposta in wiki/outputs")
    add_model_argument(query_parser)
    query_parser.set_defaults(func=command_query)

    lint_parser = subparsers.add_parser("lint", help="Analizza la wiki e salva un report")
    add_model_argument(lint_parser)
    lint_parser.set_defaults(func=command_lint)

    return parser


def format_file_list(files: list[str]) -> str:
    if not files:
        return "- Nessun file wiki rilevante trovato."
    return "\n".join(f"- `{file_name}`" for file_name in files)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit("\nOperazione interrotta.")
