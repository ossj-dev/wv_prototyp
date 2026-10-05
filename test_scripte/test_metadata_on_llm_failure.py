import json
import sys
from pathlib import Path

import main


class DummyLayoutResult:
    elements = {"dummy": "layout"}
    backend = "dummy-backend"


class DummyLayoutExtractor:
    def extract(self, pdf_paths):
        return DummyLayoutResult()


class DummyLlmClient:
    def __init__(self):
        self.last_usage = None

    def extract_json(self, *args, **kwargs):
        raise json.JSONDecodeError("Expecting value", "", 0)


def test_metadata_written_when_llm_json_is_invalid(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "LayoutExtractor", DummyLayoutExtractor)
    monkeypatch.setattr(
        main,
        "find_article_pdfs",
        lambda input_root, article_number=None: [("20323-000", tmp_path / "dummy.pdf")],
    )
    monkeypatch.setattr(main, "load_system_prompt", lambda prompt_path: "system prompt")
    monkeypatch.setattr(main, "LlmClient", lambda: DummyLlmClient())

    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("system prompt", encoding="utf-8")

    monkeypatch.setenv("INPUT_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("RESULTS_ROOT", str(tmp_path / "Ergebnisse"))
    monkeypatch.setenv("OFFLINE_MODE", "false")
    monkeypatch.setattr(sys, "argv", ["main.py", "20323-000", "--prompt-file", str(prompt_file)])

    main.main()

    result_dirs = sorted((tmp_path / "Ergebnisse").glob("20323-000_*"))
    assert result_dirs, "Es sollte ein Ergebnisverzeichnis erzeugt werden."

    metadata_file = result_dirs[0] / "metadata.json"
    assert metadata_file.exists(), "metadata.json sollte auch bei LLM-Fehlern erzeugt werden."

    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    assert metadata["article_number"] == "20323-000"
    assert metadata["status"] == "llm_json_error"
