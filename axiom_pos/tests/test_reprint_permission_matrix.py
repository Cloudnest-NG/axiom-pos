# -*- coding: utf-8 -*-
"""Permission matrix checks for paid reprint access (pure logic, no Odoo runtime)."""
import sys


def can_reprint_paid(*, access, is_admin=False, has_reprint_group=False):
    """Mirrors PosStore.axiomCashierCanPrint() with selection access."""
    if access == "none":
        return False
    if access == "all":
        return True
    # admin
    return bool(is_admin or has_reprint_group)


def can_print_order(*, finalized, access, is_admin, has_draft):
    if finalized:
        return can_reprint_paid(access=access, is_admin=is_admin)
    return bool(has_draft)


cases = [
    # none: nobody reprints paid
    dict(finalized=True, access="none", is_admin=True, has_draft=True, expect=False),
    dict(finalized=True, access="none", is_admin=False, has_draft=False, expect=False),
    # all: anyone reprints paid
    dict(finalized=True, access="all", is_admin=False, has_draft=False, expect=True),
    # admin: only admins
    dict(finalized=True, access="admin", is_admin=False, has_draft=True, expect=False),
    dict(finalized=True, access="admin", is_admin=True, has_draft=False, expect=True),
    # draft still gated separately
    dict(finalized=False, access="all", is_admin=False, has_draft=False, expect=False),
    dict(finalized=False, access="none", is_admin=True, has_draft=True, expect=True),
]

failed = 0
for i, c in enumerate(cases, 1):
    expect = c.pop("expect")
    got = can_print_order(**c)
    status = "OK" if got == expect else "FAIL"
    if got != expect:
        failed += 1
    print(f"{status}: case {i} {c} -> {got} (expect {expect})")

if failed:
    print(f"\n{failed} permission case(s) failed")
    sys.exit(1)
print("\nAll permission matrix checks passed.")
