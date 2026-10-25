"""Bugs found by the edge-case tests; details in docs/TEST-PROTOCOL.md.

Every marker is a strict xfail: the suite stays green while a bug is open, and the
test turns red as soon as the bug is fixed, as a reminder to remove the marker.
"""

import pytest


def known_bug(bug_id: str, summary: str) -> pytest.MarkDecorator:
    return pytest.mark.xfail(strict=True, reason=f"{bug_id}: {summary}")


AMOUNT_OVERFLOW = known_bug("BUG-1", "amounts beyond the database integer range are not rejected")
ID_OVERFLOW = known_bug("BUG-2", "path IDs beyond the database integer range cause HTTP 500")
BOOLEAN_AS_NUMBER = known_bug("BUG-3", "JSON true is accepted as the integer 1")
INVISIBLE_NAMES = known_bug("BUG-4", "names with invisible or control characters are accepted")
UNICODE_DUPLICATES = known_bug("BUG-5", "the same name in another Unicode form is no duplicate")
