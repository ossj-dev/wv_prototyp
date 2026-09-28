"""Pre-process extracted layout elements for the LLM input."""

from __future__ import annotations

import re


def merge_layout_to_markdown(layout_elements: list) -> str:
    """Merge indexed text and checkbox elements into readable Markdown text."""
    sorted_elements = sorted(layout_elements, key=lambda element: element["index"])
    merged_parts: list[str] = []
    current_file: str | None = None
    current_page: object | None = None

    for element in sorted_elements:
        file_name = element.get("file")
        page_number = element.get("page")
        if file_name != current_file:
            if isinstance(file_name, str) and file_name:
                merged_parts.append(f"\n=== DOKUMENT: {file_name} ===")
            current_file = file_name if isinstance(file_name, str) else None
            current_page = None
        if page_number != current_page:
            if page_number is not None:
                merged_parts.append(f"\n--- SEITE {page_number} ---")
            current_page = page_number

        element_type = element.get("type")

        if element_type in {"text", "ocr-word"}:
            value = element.get("text", "")
            if not isinstance(value, str):
                continue
            value = re.sub(r"\s+", " ", value).strip()
        elif element_type == "checkbox":
            state = element.get("state")
            if state == "checked":
                value = "[X]"
            elif state == "unchecked":
                value = "[ ]"
            else:
                continue
        else:
            continue

        if value:
            merged_parts.append(value)

    return " ".join(merged_parts)