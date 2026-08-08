# -*- coding: utf-8 -*-
"""Compile / syntax checks for all axiom_pos sources."""
from __future__ import annotations

import ast
import compileall
import pathlib
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
errors: list[str] = []


def ok(msg: str) -> None:
    print(f"OK:   {msg}")


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL: {msg}")


def main() -> int:
    print("== Python compileall ==")
    if compileall.compile_dir(str(ROOT), quiet=1, force=True):
        ok("compileall")
    else:
        fail("compileall")

    print("\n== Python AST ==")
    for p in sorted(ROOT.rglob("*.py")):
        rel = p.relative_to(ROOT)
        try:
            ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
            ok(f"py {rel}")
        except SyntaxError as e:
            fail(f"py {rel}: {e}")

    print("\n== Manifest literal_eval ==")
    try:
        manifest = ast.literal_eval((ROOT / "__manifest__.py").read_text(encoding="utf-8"))
        assert isinstance(manifest, dict)
        ok("__manifest__.py literal_eval")
        for key in ("depends", "data", "assets"):
            if key in manifest:
                ok(f"manifest has {key}")
    except Exception as e:
        fail(f"__manifest__.py: {e}")

    print("\n== XML parse ==")
    for p in sorted(ROOT.rglob("*.xml")):
        rel = p.relative_to(ROOT)
        try:
            ET.parse(p)
            ok(f"xml {rel}")
        except Exception as e:
            fail(f"xml {rel}: {e}")

    print("\n== JS node --check (ESM) ==")
    node = shutil.which("node")
    js_files = sorted(ROOT.rglob("*.js"))
    if not node:
        print("SKIP: node not available")
    else:
        for p in js_files:
            rel = p.relative_to(ROOT)
            # Odoo POS assets use ESM import/export; check via stdin as module.
            source = p.read_text(encoding="utf-8")
            r = subprocess.run(
                [node, "--input-type=module", "--check"],
                input=source,
                capture_output=True,
                text=True,
            )
            if r.returncode == 0:
                ok(f"js {rel}")
            else:
                fail(f"js {rel}: {r.stderr.strip() or r.stdout.strip()}")

    print("\n== SCSS presence / basic sanity ==")
    for p in sorted(ROOT.rglob("*.scss")):
        rel = p.relative_to(ROOT)
        text = p.read_text(encoding="utf-8")
        if text.strip() and "{" in text and "}" in text:
            ok(f"scss {rel}")
        else:
            fail(f"scss {rel}: empty or unbalanced")

    print("\n== Addons path check ==")
    conf_target = pathlib.Path("/home/kane/odoo-18/odoo-source/odoo/cloudnest-addons")
    actual = pathlib.Path("/home/kane/odoo-18/cloudnest-addons")
    ok(f"workspace exists={actual.is_dir()}")
    if conf_target.exists():
        if conf_target.is_symlink():
            ok(f"odoo.conf path is symlink -> {conf_target.readlink()}")
        else:
            has_mod = (conf_target / "axiom_pos").is_dir()
            if has_mod:
                ok("odoo.conf cloudnest-addons path contains axiom_pos")
            else:
                fail("odoo.conf cloudnest-addons path exists but missing axiom_pos")
    else:
        fail(
            "odoo.conf addons_path points to "
            f"{conf_target} which does not exist "
            f"(workspace is {actual})"
        )

    print("\n== Required feature markers ==")
    markers = {
        "models/pos_config.py": [
            "axiom_theme_bg_color",
            "axiom_theme_text_color",
            "axiom_price_bg_color",
            "axiom_price_text_color",
            "axiom_price_alignment",
            "axiom_price_font_size",
            "axiom_paid_reprint_access",
            "20px",
        ],
        "models/res_users.py": [
            "axiom_can_reprint_paid",
            "group_reprint_paid_orders",
        ],
        "security/axiom_pos_security.xml": [
            "group_reprint_paid_orders",
            "group_enable_draft_printing",
            "group_show_product_price",
        ],
        "views/res_config_settings_views.xml": [
            "pos_axiom_paid_reprint_access",
            "pos_axiom_draft_receipt_design_id",
            "pos_axiom_theme_bg_color",
            "pos_axiom_price_alignment",
            'widget="color"',
        ],
        "static/src/app/store/pos_store.js": [
            "axiom_paid_reprint_access",
            "axiom_draft_design_receipt",
            "axiomPrintOrder",
            "axiomApplyScreenTheme",
            "isBill = true",
            "webPrintFallback",
            "OrderReceipt",
            "printReceipt",
        ],
        "static/src/app/screens/receipt_screen/receipt/order_receipt.js": [
            "AxiomDraftReceiptTemplate",
            "axiom_draft_design_receipt",
            "static props",
        ],
        "static/src/app/navbar/navbar.xml": ["fa-print"],
        "static/src/app/screens/ticket_screen/ticket_screen.xml": [
            'name="print"',
            "fa-print",
        ],
        "static/src/app/generic_components/product_card/product_card.xml": [
            "axiomPriceStyleString",
            "axiomPricePositionClass",
        ],
    }
    for rel, needles in markers.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle in text:
                ok(f"{rel} contains {needle!r}")
            else:
                fail(f"{rel} missing {needle!r}")

    print("\n" + ("=" * 40))
    if errors:
        print(f"{len(errors)} failure(s)")
        for e in errors:
            print(f" - {e}")
        return 1
    print("All compilation / syntax checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
