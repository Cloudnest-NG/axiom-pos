# -*- coding: utf-8 -*-
"""Smoke checks for axiom_pos theme + paid-reprint lock."""
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)
        print(f"FAIL: {msg}")
    else:
        print(f"OK:   {msg}")


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


# --- Backend files exist ---
for rel in [
    "models/pos_config.py",
    "models/res_config_settings.py",
    "models/res_users.py",
    "views/res_config_settings_views.xml",
    "security/axiom_pos_security.xml",
    "static/src/app/store/pos_store.js",
    "static/src/app/navbar/navbar.xml",
    "static/src/app/navbar/navbar.js",
    "static/src/app/generic_components/product_card/product_card.xml",
    "static/src/app/generic_components/product_card/product_card.js",
    "static/src/app/screens/ticket_screen/ticket_screen.xml",
    "static/src/app/screens/ticket_screen/ticket_screen.js",
    "static/src/app/axiom_pos_theme.scss",
]:
    check((ROOT / rel).exists(), f"file exists {rel}")

# --- pos.config fields ---
pos_config = read("models/pos_config.py")
for field in [
    "axiom_theme_bg_color",
    "axiom_theme_text_color",
    "axiom_price_bg_color",
    "axiom_price_text_color",
    "axiom_price_alignment",
    "axiom_price_font_size",
    "axiom_paid_reprint_access",
]:
    check(field in pos_config, f"pos.config has {field}")

check("default='20px'" in pos_config or 'default="20px"' in pos_config, "price font size default 20px")
check("'top_right'" in pos_config and "'middle'" in pos_config and "'bottom_left'" in pos_config,
      "price alignment options include corners/middle")

# --- settings related ---
settings = read("models/res_config_settings.py")
check("pos_axiom_paid_reprint_access" in settings, "settings has paid reprint access")
check("pos_axiom_theme_bg_color" in settings, "settings has theme bg")
check("pos_axiom_price_alignment" in settings, "settings has price alignment")
check("pos_axiom_draft_receipt_design_id" in settings, "settings has draft receipt design")

view = read("views/res_config_settings_views.xml")
check('id="axiom_paid_reprint_access"' in view, "settings view exposes paid reprint access")
check('id="axiom_draft_receipt_template"' in view, "settings view exposes draft receipt design")
check("pos_axiom_draft_receipt_design_id" in view, "settings view has design many2one")
check("pos_bills_and_receipts_section" in view, "reprint setting under Bills & Receipts")
check("widget=\"color\"" in view, "color widgets for theme/price")
check("pos_axiom_price_font_size" in view, "font size editable in settings")

# --- security group ---
sec = read("security/axiom_pos_security.xml")
check("group_reprint_paid_orders" in sec, "Reprint Paid Orders group exists")
check("group_enable_draft_printing" in sec, "draft printing group exists")
check("group_show_product_price" in sec, "show price group exists")

# --- users rights ---
users = read("models/res_users.py")
check("axiom_can_reprint_paid" in users, "user field axiom_can_reprint_paid")
check("group_reprint_paid_orders" in users, "user rights use reprint group")
check("axiom_can_print" not in users or "axiom_can_reprint_paid" in users,
      "legacy axiom_can_print replaced/migrated")

# --- frontend print/theme ---
store = read("static/src/app/store/pos_store.js")
check("axiom_paid_reprint_access" in store, "frontend respects paid reprint access")
check("axiom_draft_design_receipt" in store, "frontend loads draft XML design")
check("axiomPrintOrder" in store, "unified print helper")
check("isBill = true" in store or "data.isBill = true" in store, "draft uses isBill")
check("printReceipt({ order })" in store or "printReceipt({ order: order })" in store
      or "return this.printReceipt({ order })" in store, "paid uses standard printReceipt")
check("axiomApplyScreenTheme" in store, "theme applied from config")

navbar_xml = read("static/src/app/navbar/navbar.xml")
check("fa-print" in navbar_xml, "print icon in POS header")

ticket_xml = read("static/src/app/screens/ticket_screen/ticket_screen.xml")
check("axiom-order-print-button" in ticket_xml or "fa-print" in ticket_xml,
      "print icon in order list")
check("name=\"print\"" in ticket_xml, "print column next to trash")

card_xml = read("static/src/app/generic_components/product_card/product_card.xml")
check("axiomPricePositionClass" in card_xml and "axiomPriceStyleString" in card_xml,
      "product card price styled from config")

scss = read("static/src/app/axiom_pos_theme.scss")
for align in [
    "top_left", "top_center", "top_right",
    "middle_left", "middle", "middle_right",
    "bottom_left", "bottom_center", "bottom_right",
]:
    check(f"axiom-price-{align}" in scss, f"scss alignment {align}")

# --- syntax check python ---
for rel in ["models/pos_config.py", "models/res_config_settings.py", "models/res_users.py", "__manifest__.py"]:
    try:
        ast.parse(read(rel))
        check(True, f"python syntax {rel}")
    except SyntaxError as e:
        check(False, f"python syntax {rel}: {e}")

# --- manifest ---
manifest = ast.literal_eval(read("__manifest__.py"))
check("views/res_config_settings_views.xml" in manifest.get("data", []), "manifest loads settings view")
check("security/axiom_pos_security.xml" in manifest.get("data", []), "manifest loads security")

if errors:
    print(f"\n{len(errors)} failure(s)")
    sys.exit(1)
print("\nAll smoke checks passed.")
