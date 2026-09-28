"""Validate extraction results and repair invalid LLM responses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


JsonExtractor = Callable[..., dict[str, Any]]


def validate_extraction_result(result: Any) -> list[str]:
    """Return human-readable errors for the extraction result schema."""
    errors: list[str] = []
    if not isinstance(result, dict):
        return ["Fehler: Der Output muss ein JSON-Objekt sein."]

    required_keys = {"dokumentensprache", "artikelnummer", "labels"}
    missing_keys = sorted(required_keys - result.keys())
    unexpected_keys = sorted(result.keys() - required_keys)
    if missing_keys:
        errors.append(f"Fehler: Fehlende Keys: {', '.join(missing_keys)}.")
    if unexpected_keys:
        errors.append(f"Fehler: Unerlaubte Keys: {', '.join(unexpected_keys)}.")

    for key in ("dokumentensprache", "artikelnummer"):
        if key in result and result[key] is not None and not isinstance(result[key], str):
            errors.append(f"Fehler: Der Wert fuer \"{key}\" muss ein String oder null sein.")

    labels = result.get("labels")
    if not isinstance(labels, list):
        errors.append('Fehler: Der Key "labels" muss ein Array sein.')
        return errors

    for index, label in enumerate(labels):
        prefix = f"Fehler: labels[{index}]"
        if not isinstance(label, dict):
            errors.append(f"{prefix} muss ein Objekt sein.")
            continue
        if set(label) != {"verpackungsebene", "label_inhalt"}:
            errors.append(
                f'{prefix} muss exakt die Keys "verpackungsebene" und "label_inhalt" enthalten.'
            )
        if not isinstance(label.get("verpackungsebene"), str):
            errors.append(f'{prefix}.verpackungsebene muss ein String sein.')
        if not isinstance(label.get("label_inhalt"), list) or not all(
            isinstance(item, str) for item in label.get("label_inhalt", [])
        ):
            errors.append(f'{prefix}.label_inhalt muss ein Array aus Strings sein.')
    return errors


def refine_extraction_result(
    *,
    initial_result: dict[str, Any],
    document_prompt: str,
    refinement_prompt: str,
    llm_extract: JsonExtractor,
    debug_directory: Path,
    max_attempts: int = 1,
) -> tuple[dict[str, Any], list[str]]:
    """Validate and, when necessary, repair an extraction result."""
    result = initial_result
    feedback: list[str] = []
    attempts = max(0, max_attempts)

    for attempt in range(attempts + 1):
        feedback = validate_extraction_result(result)
        if not feedback:
            return result, []
        if attempt == attempts:
            break

        follow_up = (
            f"Dokumententext:\n{document_prompt}\n\n"
            f"Vorheriger JSON-Output:\n{json.dumps(result, ensure_ascii=False, indent=2)}\n\n"
            "Automatisches Feedback:\n- " + "\n- ".join(feedback)
        )
        result = llm_extract(
            follow_up,
            refinement_prompt,
            debug_output_path=debug_directory / f"refinement_output_{attempt + 1:02d}.md",
        )

    return result, feedback