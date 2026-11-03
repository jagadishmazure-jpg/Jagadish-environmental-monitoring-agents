"""Brand/name guard: blocklist stored as SHA-256 hashes, never plain
names. ``check_text`` returns True when a blocked token is present.
The blocklist must be non-empty (test-pinned). The fictional operator
name Sorrelmere Environmental is not blocked.
"""

from __future__ import annotations

import hashlib
import re

# SHA-256 of lower-cased blocked tokens (behaviour is pinned by tests
# via the anchor token below, not by naming blocked organisations).
_BLOCKLIST_HASHES = frozenset(
    {
        "2803e1e76b7437515c8b9bdad4de0de1ecac8058ab5e5cdb60d2f86ec3d3f08e",
        "9a48c783765d5c58418f5defd8453f8bbf116ed0a0416ad1f60baee56474beda",
        "d092031c396b4199dc3d5fe3b838e1befcfd9b912ee0fa169b92509a819c62d9",
        # Test anchor: hash of the fictional token "fablefield", so the
        # mechanism can be tested without any real name in plain text.
        "cc793ca269709a6b494aedcb2e2d3c628938d309d30cdbe2518517da9804a2f7",
    }
)

_TOKEN = re.compile(r"[a-z0-9]+")


def blocklist_size() -> int:
    return len(_BLOCKLIST_HASHES)


def check_text(text: str) -> bool:
    """True if any token in ``text`` hashes to a blocked token."""
    for token in _TOKEN.findall(text.lower()):
        if hashlib.sha256(token.encode()).hexdigest() in _BLOCKLIST_HASHES:
            return True
    return False
