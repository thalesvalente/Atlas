"""Strict JSON and shared validation for the local binding contracts."""

from dataclasses import dataclass
from hashlib import sha256
import json
import re
import unicodedata

MAX_DOCUMENT_BYTES = 128 * 1024 * 1024
DTO_KINDS = ("record", "node", "relation", "table", "row", "asset", "collection")
DIGEST = re.compile(r"[0-9a-f]{64}")
TOKEN = re.compile(r"[a-z][a-z0-9_-]{0,63}")
RESERVED = re.compile(r"(?i)(CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|(?:COM|LPT)[0-9¹²³])")


class Rejected(ValueError):
    """An error code safe to print without disclosing paths or document contents."""


def require(condition, code):
    if not condition:
        raise Rejected(code)


def fields(value, required, optional, code):
    require(isinstance(value, dict), code)
    keys = value.keys()
    require(set(required) <= keys <= set(required) | set(optional), code)
    return value


def text(value, limit):
    return (type(value) is str and 0 < len(value) <= limit
            and all(not 0xD800 <= ord(char) <= 0xDFFF for char in value))


def digest(value):
    return type(value) is str and DIGEST.fullmatch(value) is not None


def token(value):
    return type(value) is str and TOKEN.fullmatch(value) is not None


def relative_path(value):
    require(text(value, 4095) and unicodedata.is_normalized("NFC", value), "INVALID_RELATIVE_PATH")
    components = tuple(value.split("/"))
    for part in components:
        require(
            part and len(part.encode("utf-8")) <= 255 and part[-1] not in " ."
            and not RESERVED.fullmatch(part.split(".", 1)[0].rstrip(" "))
            and not any(c in '\\:<>|?*"' or unicodedata.category(c) in {"Cc", "Cf"} for c in part),
            "INVALID_RELATIVE_PATH",
        )
    return components


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "DUPLICATE_JSON_KEY")
        obj[key] = value
    return obj


def reject_constant(_):
    raise Rejected("INVALID_JSON")


def decode_document(raw):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                          parse_constant=reject_constant)
    except Rejected:
        raise
    except (ValueError, RecursionError):
        raise Rejected("INVALID_JSON") from None


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def lexical_sha(raw):
    try:
        return sha256(raw.encode("utf-8")).hexdigest()
    except UnicodeError:
        raise Rejected("INVALID_DTO_JSON") from None


@dataclass(frozen=True)
class Source:
    id: str
    revision: str
    metadata_sha256: str

    @classmethod
    def read(cls, value, *, plan=False):
        fields(value, ("id", "revision", "metadata_sha256"), ("name",) if plan else (),
               "INVALID_SOURCE")
        require(text(value["id"], 1024) and text(value["revision"], 1024)
                and digest(value["metadata_sha256"]), "INVALID_SOURCE")
        return cls(value["id"], value["revision"], value["metadata_sha256"])

    @property
    def snapshot_key(self):
        return compact(["atlas-snapshot-selection/1", [True, self.id],
                        [True, self.revision], [True, self.metadata_sha256]])


@dataclass(frozen=True)
class Identity:
    uid: str
    kind: str
    source_key: str | None
    raw_sha256: str
    table_rows_sha256: str | None
