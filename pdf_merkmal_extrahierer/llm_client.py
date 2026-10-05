"""OpenAI-compatible client for a local LM Studio server."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


FewShotExample = tuple[str, str]


@dataclass
class CallMetrics:
    """Timing and token usage for one inference call."""

    step: str
    duration_seconds: float
    usage: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return int(self.usage.get("total_tokens") or 0)


@dataclass
class ExtractionRun:
    """Result and measurements for one extraction run."""

    result: dict[str, Any]
    calls: list[CallMetrics]

    @property
    def total_duration_seconds(self) -> float:
        return sum(call.duration_seconds for call in self.calls)

    @property
    def total_tokens(self) -> int:
        return sum(call.total_tokens for call in self.calls)

    def usage_totals(self) -> dict[str, int]:
        fields = ("prompt_tokens", "completion_tokens", "total_tokens")
        return {
            field_name: sum(
                int(call.usage.get(field_name) or 0) for call in self.calls
            )
            for field_name in fields
        }


def build_extraction_schema() -> dict[str, Any]:
    """Build the strict Internal-CoT schema with reasoning as the first field."""
    properties: dict[str, Any] = {
        "_gedankengang": {
            "type": "string",
            "description": (
                "Schreibe eine ausführliche Klartextanalyse mit den Abschnitten "
                "BELEGE, CHECKBOX-ENTSCHEIDUNGEN, ABLEITUNG und UNSICHERHEITEN. "
                "Nenne konkrete Fundstellen und begründe jede Zuordnung. "
                "Gib kein JSON und kein fertiges Extraktionsergebnis aus."
            ),
        },
        "dokumentensprache": {"type": ["string", "null"]},
        "artikelnummer": {"type": ["string", "null"]},
        "labels": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "verpackungsebene": {"type": "string"},
                    "label_inhalt": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["verpackungsebene", "label_inhalt"],
            },
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties),
    }


class LlmClient:
    """Send extraction prompts to an OpenAI-compatible local LLM endpoint."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        from dotenv import load_dotenv

        load_dotenv()
        self.base_url = base_url or os.getenv(
            "LM_STUDIO_BASE_URL", "http://127.0.0.1:1234/v1"
        )
        self.api_key = api_key or os.getenv("LM_STUDIO_API_KEY", "lm-studio")
        self.model = model or os.getenv("LM_STUDIO_MODEL", "local-model")
        self.enable_thinking = os.getenv(
            "LM_STUDIO_ENABLE_THINKING", "false"
        ).lower() in {"1", "true", "yes"}
        self.last_usage: dict[str, Any] | None = None
        self.last_run_metrics: list[CallMetrics] = []

        from openai import OpenAI

        self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def extract_json(
        self,
        raw_text: str,
        system_prompt: str,
        few_shot_examples: Sequence[FewShotExample] = (),
        debug_output_path: Path | None = None,
        step_name: str = "extraction",
    ) -> dict[str, Any]:
        """Extract a JSON object while enforcing the output schema."""
        schema = build_extraction_schema()
        system_prompt = (
            f"{system_prompt}\n\n"
            "INTERNAL-REASONING: Fuelle das erste JSON-Feld _gedankengang "
            "mit einer ausfuehrlichen Klartextanalyse. Nenne zuerst konkrete "
            "Belege, danach jede Checkbox-Entscheidung, dann die logische "
            "Zuordnung zu den Datenfeldern und zuletzt Unsicherheiten. "
            "Schreibe kein zweites fertiges Ergebnis ausserhalb des Schemas. "
            "Das Feld bleibt Teil des validen JSON.\n"
            "VERBINDLICHES JSON-SCHEMA:\n"
            f"{json.dumps(schema, ensure_ascii=False, indent=2)}"
        )
        messages = self._build_messages(
            raw_text, system_prompt, few_shot_examples
        )
        response, content = self._complete(
            messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "packaging_instruction_extraction",
                    "strict": True,
                    "schema": schema,
                },
            },
            step_name=step_name,
        )

        if debug_output_path is not None:
            debug_output_path.write_text(
                f"# LLM-Ausgabe\n\n{content}\n", encoding="utf-8"
            )

        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Die LLM-Antwort ist kein JSON-Objekt.")
        return parsed

    def _build_messages(
        self,
        raw_text: str,
        system_prompt: str,
        few_shot_examples: Sequence[FewShotExample],
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
        ]
        for example_input, example_output in few_shot_examples:
            messages.extend(
                [
                    {"role": "user", "content": example_input},
                    {"role": "assistant", "content": example_output},
                ]
            )
        messages.append({"role": "user", "content": raw_text})
        return messages

    def _complete(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        step_name: str = "call",
    ) -> tuple[Any, str]:
        request_options: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if response_format is not None:
            request_options["response_format"] = response_format
        if not self.enable_thinking:
            request_options["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": False}
            }

        started = time.perf_counter()
        response = self._client.chat.completions.create(**request_options)
        duration = time.perf_counter() - started
        usage = getattr(response, "usage", None)
        self.last_usage = (
            usage.model_dump()
            if usage is not None and hasattr(usage, "model_dump")
            else dict(usage) if usage is not None else None
        )
        self.last_run_metrics.append(
            CallMetrics(
                step=step_name,
                duration_seconds=duration,
                usage=self.last_usage or {},
            )
        )
        choice = response.choices[0]
        message = choice.message
        content = message.content or ""
        if not content:
            finish_reason = getattr(choice, "finish_reason", "unbekannt")
            message_fields = sorted(getattr(message, "model_fields_set", set()))
            raise ValueError(
                "Das LLM hat kein `message.content` zurückgegeben "
                f"(finish_reason={finish_reason}, "
                f"message_fields={message_fields})."
            )
        return response, content


def run_extraction(
    doc: str,
    prompt_strategy: str,
    reasoning_mode: str,
    *,
    client: LlmClient | None = None,
    debug_output_dir: Path | None = None,
) -> ExtractionRun:
    """Run one Internal-CoT strategy combination for one document."""
    if reasoning_mode != "Internal-CoT":
        raise ValueError("reasoning_mode muss 'Internal-CoT' sein.")
    llm_client = client or LlmClient()
    llm_client.last_run_metrics = []
    if debug_output_dir is not None:
        debug_output_dir.mkdir(parents=True, exist_ok=True)

    result = llm_client.extract_json(
        doc,
        prompt_strategy,
        debug_output_path=(
            debug_output_dir / "llm_output.md"
            if debug_output_dir is not None
            else None
        ),
        step_name="extraction",
    )
    return ExtractionRun(result=result, calls=list(llm_client.last_run_metrics))