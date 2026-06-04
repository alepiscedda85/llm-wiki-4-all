from __future__ import annotations

import argparse
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

from llm_wiki.config import parse_simple_yaml
from llm_wiki.workspace import Workspace

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "llm_wiki.py"


def load_cli_module():
    spec = importlib.util.spec_from_file_location("llm_wiki_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class WorkspaceTests(unittest.TestCase):
    def test_workspace_paths_and_source_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Workspace(Path(tmp))
            workspace.ensure_dirs()
            source = workspace.sources_dir / "example.md"
            source.write_text("# Example\n", encoding="utf-8")

            self.assertEqual(workspace.resolve_source("example.md"), source.resolve())
            self.assertEqual(
                workspace.resolve_source("raw/sources/example.md"),
                source.resolve(),
            )
            self.assertEqual(workspace.display_path(source.resolve()), "raw/sources/example.md")

    def test_parse_simple_yaml_flat_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text(
                "# comment\nname: Test Wiki\nlanguage: en\nprovider: ollama\nmodel: llama3.2\n",
                encoding="utf-8",
            )

            config = parse_simple_yaml(path)
            self.assertEqual(config["name"], "Test Wiki")
            self.assertEqual(config["language"], "en")
            self.assertEqual(config["provider"], "ollama")
            self.assertEqual(config["model"], "llama3.2")


class CliWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.cli = load_cli_module()

    def test_init_creates_workspace_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace_path = Path(tmp) / "instances" / "example"
            args = argparse.Namespace(workspace=str(workspace_path), global_workspace=None)

            self.cli.init_project(args)

            workspace = Workspace(workspace_path.resolve())
            self.assertTrue(workspace.agents_file.exists())
            self.assertTrue(workspace.config_file.exists())
            self.assertTrue(workspace.sources_dir.exists())
            self.assertTrue(workspace.index_file.exists())
            self.assertTrue(workspace.log_file.exists())
            self.assertTrue(workspace.outputs_dir.exists())

    def test_config_precedence_cli_env_config_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Workspace(Path(tmp))
            workspace.ensure_dirs()
            workspace.config_file.write_text(
                "provider: openai\nmodel: config-model\nlanguage: en\n",
                encoding="utf-8",
            )
            args = argparse.Namespace(
                provider=None,
                global_provider=None,
                model=None,
                global_model=None,
            )
            previous_provider = os.environ.pop("LLM_PROVIDER", None)
            previous_openai_model = os.environ.pop("OPENAI_MODEL", None)
            previous_ollama_model = os.environ.pop("OLLAMA_MODEL", None)
            try:
                self.assertEqual(self.cli.selected_provider(args, workspace), "openai")
                self.assertEqual(self.cli.selected_model(args, workspace), "config-model")
                args.model = "cli-model"
                self.assertEqual(self.cli.selected_model(args, workspace), "cli-model")
            finally:
                if previous_provider is not None:
                    os.environ["LLM_PROVIDER"] = previous_provider
                if previous_openai_model is not None:
                    os.environ["OPENAI_MODEL"] = previous_openai_model
                if previous_ollama_model is not None:
                    os.environ["OLLAMA_MODEL"] = previous_ollama_model


    def test_ingest_writes_only_inside_workspace_and_uses_relative_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace_path = Path(tmp) / "workspace"
            init_args = argparse.Namespace(workspace=str(workspace_path), global_workspace=None)
            self.cli.init_project(init_args)

            source = workspace_path / "raw" / "sources" / "example.md"
            source.write_text("# Example\n", encoding="utf-8")
            captured: dict[str, str] = {}
            original_call_llm = self.cli.call_llm

            def fake_call_llm(prompt, args, system=None, workspace=None):
                captured["prompt"] = prompt
                return """---
title: Generated Example
type: output
source: raw/sources/example.md
created: 2026-06-04
updated: 2026-06-04
tags: []
status: draft
---

# Generated Example

## Sintesi operativa

Test.
"""

            self.cli.call_llm = fake_call_llm
            try:
                ingest_args = argparse.Namespace(
                    source="example.md",
                    workspace=str(workspace_path),
                    global_workspace=None,
                    provider=None,
                    global_provider=None,
                    model=None,
                    global_model=None,
                )
                self.cli.command_ingest(ingest_args)
            finally:
                self.cli.call_llm = original_call_llm

            workspace = Workspace(workspace_path.resolve())
            output = workspace.outputs_dir / "generated-example.md"
            self.assertTrue(output.exists())
            self.assertIn("source: raw/sources/example.md", captured["prompt"])
            self.assertNotIn(str(workspace_path.resolve()), captured["prompt"])
            self.assertIn("[[outputs/generated-example]]", workspace.index_file.read_text(encoding="utf-8"))

    def test_ingest_prompt_uses_workspace_relative_source(self):
        prompt = self.cli.source_prompt(
            "raw/sources/example.md",
            "# Example",
            "# Index",
            "it",
        )

        self.assertIn("source: raw/sources/example.md", prompt)
        self.assertNotIn(str(ROOT), prompt)
        self.assertIn("Rispondi solo in lingua: it", prompt)


if __name__ == "__main__":
    unittest.main()
