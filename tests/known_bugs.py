"""Marker for bugs found by tests but not fixed yet; details in docs/TEST-PROTOCOL.md.

Every marker is a strict xfail: the suite stays green while a bug is open, and the
test turns red as soon as the bug is fixed, as a reminder to remove the marker.
BUG-1 … BUG-5 are fixed, so no marker is in use right now.
"""

import pytest


def known_bug(bug_id: str, summary: str) -> pytest.MarkDecorator:
    return pytest.mark.xfail(strict=True, reason=f"{bug_id}: {summary}")
