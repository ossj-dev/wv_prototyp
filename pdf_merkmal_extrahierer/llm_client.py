"""OpenAI-compatible client for a local LM Studio server."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Sequence


FewShotExample = tuple[str, str]


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

        from openai import OpenAI

        self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def extract_json(
        self,
        raw_text: str,
        system_prompt: str,
        few_shot_examples: Sequence[FewShotExample] = (),
        debug_output_path: Path | None = None,
    ) -> dict[str, Any]:
        """Extract a JSON object while enforcing the output schema."""
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

        request_options: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        request_options["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "packaging_instruction_extraction",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
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
                                "required": [
                                    "verpackungsebene",
                                    "label_inhalt",
                                ],
                            },
                        },
                    },
                    "required": [
                        "dokumentensprache",
                        "artikelnummer",
                        "labels",
                    ],
                },
            }
        }
        if not self.enable_thinking:
            request_options["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": False}
            }

        response = self._client.chat.completions.create(
            **request_options,
        )
        usage = getattr(response, "usage", None)
        if usage is not None:
            self.last_usage = (
                usage.model_dump()
                if hasattr(usage, "model_dump")
                else dict(usage)
            )
        else:
            self.last_usage = None
        choice = response.choices[0]
        message = choice.message
        content = message.content
        if not content:
            if debug_output_path is not None:
                debug_output_path.write_text(
                    "# LLM-Ausgabe\n\n"
                    "Das Feld `message.content` war leer. Die vollständige "
                    "API-Antwort folgt:\n\n"
                    f"```json\n{response.model_dump_json(indent=2)}\n```\n",
                    encoding="utf-8",
                )
            finish_reason = getattr(choice, "finish_reason", "unbekannt")
            message_fields = sorted(getattr(message, "model_fields_set", set()))
            raise ValueError(
                "Das LLM hat kein `message.content` zurückgegeben "
                f"(finish_reason={finish_reason}, "
                f"message_fields={message_fields}). "
                "Die vollständige API-Antwort wurde in der Debug-Datei gespeichert."
            )

        if debug_output_path is not None:
            debug_output_path.write_text(
                f"# LLM-Ausgabe\n\n{content}\n", encoding="utf-8"
            )

        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Die LLM-Antwort ist kein JSON-Objekt.")
        return parsed