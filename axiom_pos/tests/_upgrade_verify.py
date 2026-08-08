# -*- coding: utf-8 -*-
"""Upgrade/install axiom_pos and verify POS assets + groups."""
import sys

def main(env):
    Mod = env["ir.module.module"]
    mod = Mod.search([("name", "=", "axiom_pos")], limit=1)
    print("module_found", bool(mod), "state", mod.state if mod else None, "version", mod.latest_version if mod else None)

    if not mod:
        print("ERROR: axiom_pos not in addons path for this DB")
        return

    if mod.state != "installed":
        print("Installing axiom_pos...")
        mod.button_immediate_install()
    else:
        print("Upgrading axiom_pos...")
        mod.button_immediate_upgrade()

    env.cr.commit()
    mod.invalidate_recordset()
    print("after state", mod.state, "version", mod.latest_version)

    assets = env["ir.asset"].search([("path", "ilike", "axiom_pos")])
    print("ir.asset count", len(assets))
    for a in assets:
        print("ASSET", a.bundle, a.path)

    # Also check attachments for compiled bundles mentioning axiom
    Att = env["ir.attachment"]
    att = Att.search([("name", "ilike", "point_of_sale.assets_prod%"), ("url", "ilike", "/web/assets/%")], limit=5)
    print("prod asset attachments", len(att))

    for xmlid in [
        "axiom_pos.group_show_product_price",
        "axiom_pos.group_enable_draft_printing",
        "axiom_pos.group_reprint_paid_orders",
    ]:
        g = env.ref(xmlid, raise_if_not_found=False)
        print("group", xmlid, "exists", bool(g), "users", len(g.users) if g else 0)

    admin = env.ref("base.user_admin")
    print(
        "admin has show_price",
        admin.has_group("axiom_pos.group_show_product_price"),
        "draft",
        admin.has_group("axiom_pos.group_enable_draft_printing"),
        "reprint",
        admin.has_group("axiom_pos.group_reprint_paid_orders"),
    )

    # clear assets cache
    env["ir.attachment"].sudo().search([
        ("url", "=like", "/web/assets/%"),
        ("name", "ilike", "point_of_sale%"),
    ]).unlink()
    env.cr.commit()
    print("cleared POS web asset attachments")

    Config = env["pos.config"].search([], limit=1)
    if Config:
        print(
            "sample config",
            Config.name,
            "price_align",
            Config.axiom_price_alignment,
            "font",
            Config.axiom_price_font_size,
            "reprint",
            Config.axiom_paid_reprint_access,
        )

if __name__ == "__main__":
    # used via odoo shell: exec(open(...).read()); main(env)
    pass
