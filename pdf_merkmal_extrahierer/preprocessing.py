"""Pre-process extracted layout elements for the LLM input."""

from __future__ import annotations

import re
import json


def merge_layout_to_markdown(layout_elements: list) -> str:
    """Merge indexed text and checkbox elements into readable Markdown text."""
    sorted_elements = sorted(layout_elements, key=lambda element: element["index"])
    output_lines: list[str] = []
    current_line: list[str] = []
    current_file: str | None = None
    current_page: object | None = None
    current_line_top: float | None = None
    current_line_bottom: float | None = None

    def flush_line() -> None:
        if current_line:
            output_lines.append(" ".join(current_line))
            current_line.clear()

    for element in sorted_elements:
        file_name = element.get("file")
        page_number = element.get("page")
        if file_name != current_file:
            flush_line()
            if isinstance(file_name, str) and file_name:
                output_lines.append(f"=== DOKUMENT: {file_name} ===")
            current_file = file_name if isinstance(file_name, str) else None
            current_page = None
            current_line_top = None
            current_line_bottom = None
        if page_number != current_page:
            flush_line()
            if page_number is not None:
                output_lines.append(f"--- SEITE {page_number} ---")
            current_page = page_number
            current_line_top = None
            current_line_bottom = None

        bbox = element.get("bbox")
        if (
            current_line
            and isinstance(bbox, list)
            and len(bbox) >= 4
            and current_line_bottom is not None
            and float(bbox[1]) > current_line_bottom + 1.5
        ):
            flush_line()
            current_line_top = None
            current_line_bottom = None

        element_type = element.get("type")

        if element_type in {"text", "ocr-word", "table"}:
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
            current_line.append(value)
            if isinstance(bbox, list) and len(bbox) >= 4:
                top = float(bbox[1])
                bottom = float(bbox[3])
                current_line_top = top if current_line_top is None else min(current_line_top, top)
                current_line_bottom = (
                    bottom
                    if current_line_bottom is None
                    else max(current_line_bottom, bottom)
                )

    flush_line()
    return "\n".join(output_lines)


def layout_to_spatial_format(layout_elements: list) -> str:
    """Convert layout elements to compact, grouped JSON with spatial data."""
    grouped_elements: dict[tuple[object, object], list[dict[str, object]]] = {}

    for element in sorted(layout_elements, key=lambda item: item.get("index", 0)):
        element_type = element.get("type")
        if element_type in {"text", "ocr-word", "table"}:
            text = element.get("text", "")
            if not isinstance(text, str):
                continue
            text = re.sub(r"\s+", " ", text).strip()
        elif element_type == "checkbox":
            state = element.get("state")
            if state == "checked":
                text = "[X]"
            elif state == "unchecked":
                text = "[ ]"
            else:
                continue
        else:
            continue

        bbox = element.get("bbox")
        if not text or not isinstance(bbox, list) or len(bbox) < 4:
            continue
        try:
            rounded_bbox = [round(float(value), 1) for value in bbox[:4]]
        except (TypeError, ValueError):
            continue

        group_key = (element.get("file"), element.get("page"))
        grouped_elements.setdefault(group_key, []).append(
            {"text": text, "bbox": rounded_bbox}
        )

    spatial_groups = [
        {"file": file_name, "page": page_number, "elements": elements}
        for (file_name, page_number), elements in grouped_elements.items()
    ]
    return json.dumps(spatial_groups, ensure_ascii=False, indent=2)