"""Hash-chained audit log: each entry commits to the previous hash,
so a tampered or deleted middle entry breaks verification."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


def _digest(prev: str, payload: dict) -> str:
    blob = prev + json.dumps(payload, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


@dataclass
class AuditEntry:
    index: int
    prev_hash: str
    entry_hash: str
    payload: dict


class AuditLog:
    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []

    def append(self, payload: dict) -> AuditEntry:
        prev = self.entries[-1].entry_hash if self.entries else "GENESIS"
        entry = AuditEntry(len(self.entries), prev, _digest(prev, payload), payload)
        self.entries.append(entry)
        return entry

    def verify(self) -> bool:
        prev = "GENESIS"
        for entry in self.entries:
            if entry.prev_hash != prev:
                return False
            if entry.entry_hash != _digest(prev, entry.payload):
                return False
            prev = entry.entry_hash
        return True
