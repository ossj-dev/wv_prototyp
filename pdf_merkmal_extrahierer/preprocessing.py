"""Pre-process extracted layout elements for the LLM input."""

from __future__ import annotations

import re


def merge_layout_to_markdown(layout_elements: list) -> str:
    """Merge indexed text and checkbox elements into readable Markdown text."""
    sorted_elements = sorted(layout_elements, key=lambda element: element["index"])
    merged_parts: list[str] = []

    for element in sorted_elements:
        element_type = element.get("type")

        if element_type == "text":
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