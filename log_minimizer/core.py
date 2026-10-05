"""Fresh fixed-schema projection; unknown fields never reach the sink."""

import json
import re

from .admission import LabError, MAX_OUTPUT, parse


FIELDS = frozenset({"event_id", "event_type", "outcome", "severity", "service", "context"})


def project(value):
    """Internal native-JSON tree projection; does not mutate its input."""
    if type(value) is not dict or type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise LabError("schema.invalid")
    events = value.get("events")
    if type(events) is not list:
        raise LabError("schema.invalid")
    projected, identifiers = [], set()
    dropped = len(set(value) - {"schema_version", "events"})
    for event in events:
        if type(event) is not dict:
            raise LabError("schema.invalid")
        identifier = event.get("event_id")
        if type(identifier) is not str or re.fullmatch(r"lab-event-[0-9]{4}", identifier) is None:
            raise LabError("schema.invalid")
        if identifier in identifiers:
            raise LabError("schema.invalid")
        identifiers.add(identifier)
        clean = {"event_id": identifier}
        for field, choices in (("event_type", {"authentication"}), ("outcome", {"success", "failure"}),
                               ("severity", {"low", "medium"}), ("service", {"sshd", "lab-api"})):
            item = event.get(field)
            if type(item) is not str or item not in choices:
                raise LabError("schema.invalid")
            clean[field] = item
        if "context" in event:
            context = event["context"]
            if type(context) is not dict:
                raise LabError("schema.invalid")
            dropped += len(set(context) - {"elapsed_ms"})
            if "elapsed_ms" in context:
                elapsed = context["elapsed_ms"]
                if type(elapsed) is not int or not 0 <= elapsed <= 60000:
                    raise LabError("schema.invalid")
                clean["context"] = {"elapsed_ms": elapsed}
        dropped += len(set(event) - FIELDS)
        projected.append(clean)
    return {"status": "minimized", "policy": "synthetic-v1", "schema_version": 1,
            "events": projected, "event_count": len(projected), "dropped_fields": dropped}


def minimize(raw: bytes) -> dict:
    """Validate an entire synthetic batch before returning any projected events."""
    return project(parse(raw))


def render(report: dict) -> str:
    """ASCII output, capped before emission; report is a trusted native result."""
    encoder = json.JSONEncoder(ensure_ascii=True, allow_nan=False, separators=(",", ":"))
    chunks, size = [], 1
    for chunk in encoder.iterencode(report):
        size += len(chunk)
        if size > MAX_OUTPUT:
            raise LabError("output.error")
        chunks.append(chunk)
    return "".join(chunks) + "\n"
