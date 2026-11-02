"""Canonical display values for native-view/1, independent of any producer.

Scientific identity is never inferred from an explicitly null native_id.
The consumer independently recomputes these fields from the original JSON.
"""
from __future__ import annotations
import json


def scalar(value):
    return value if isinstance(value, str) else json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def dtype(value):
    if value is None: return "null"
    if isinstance(value, bool): return "boolean"
    if isinstance(value, int): return "integer"
    if isinstance(value, float): return "number"
    if isinstance(value, str): return "string"
    return "array" if isinstance(value, list) else "object"


def entry_values(value, group, kind):
    row = value if isinstance(value, dict) else {"value": value}
    def text(*keys):
        for key in keys:
            item = row.get(key)
            if isinstance(item, str) and item:
                return item
        return None
    if "native_id" in row:
        native_id = None if row["native_id"] is None else scalar(row["native_id"])
    else:
        native_id = scalar(row["id"]) if kind == "record" and row.get("id") is not None else None
    fields = [{"name": str(k), "type": dtype(v), "text": scalar(v)}
              for k, v in row.items() if not isinstance(v, (dict, list))]
    result = {
        "title": text("title", "label", "name", "id", "native_id", "key") or group,
        "native_id": native_id, "source_key": text("key", "id"),
        "parent_key": text("parent_key"), "family": text("family"),
        "status": text("execution_state", "status", "result_state", "result_group"),
        "date": text("started_at", "startTime", "timestamp", "date", "scientific_at"),
        "fields": fields,
    }
    if kind == "row":
        cells = row.get("cells")
        if not isinstance(cells, dict):
            raise ValueError("NATIVE_ROW_CELLS_REQUIRED")
        result["cells"] = {k: {"text": scalar(v), "type": dtype(v)} for k, v in cells.items()}
    return result
