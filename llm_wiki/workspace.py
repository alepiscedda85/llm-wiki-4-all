"""Workspace path model for llm-wiki-4-all."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Workspace:
    """Root operativa di una singola LLM Wiki file-based."""

    root: Path

    @property
    def agents_file(self) -> Path:
        return self.root / "AGENTS.md"

    @property
    def config_file(self) -> Path:
        return self.root / "config.yaml"

    @property
    def raw_dir(self) -> Path:
        return self.root / "raw"

    @property
    def sources_dir(self) -> Path:
        return self.raw_dir / "sources"

    @property
    def wiki_dir(self) -> Path:
        return self.root / "wiki"

    @property
    def index_file(self) -> Path:
        return self.wiki_dir / "index.md"

    @property
    def log_file(self) -> Path:
        return self.wiki_dir / "log.md"

    @property
    def overview_file(self) -> Path:
        return self.wiki_dir / "overview.md"

    @property
    def entities_dir(self) -> Path:
        return self.wiki_dir / "entities"

    @property
    def concepts_dir(self) -> Path:
        return self.wiki_dir / "concepts"

    @property
    def outputs_dir(self) -> Path:
        return self.wiki_dir / "outputs"

    @property
    def contradictions_dir(self) -> Path:
        return self.wiki_dir / "contradictions"

    def ensure_dirs(self) -> None:
        for directory in [
            self.sources_dir,
            self.entities_dir,
            self.concepts_dir,
            self.outputs_dir,
            self.contradictions_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def resolve_source(self, source_path: str) -> Path:
        """Resolve source path inside this workspace without modifying raw/."""
        requested = Path(source_path).expanduser()
        candidates: list[Path] = []
        if requested.is_absolute():
            candidates.append(requested.resolve())
        else:
            candidates.append((self.root / requested).resolve())
            candidates.append((self.sources_dir / requested).resolve())

        for candidate in candidates:
            if candidate.exists():
                return candidate

        tried = "\n".join(f"- {candidate}" for candidate in candidates)
        raise SystemExit(f"File sorgente non trovato. Path provati:\n{tried}")

    def display_path(self, path: Path) -> str:
        """Return a readable path, relative to the workspace when possible."""
        resolved_root = self.root.resolve()
        resolved_path = path.resolve()
        try:
            return resolved_path.relative_to(resolved_root).as_posix()
        except ValueError:
            return resolved_path.as_posix()
