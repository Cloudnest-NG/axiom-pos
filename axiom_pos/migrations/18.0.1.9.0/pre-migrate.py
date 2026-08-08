# -*- coding: utf-8 -*-
"""Convert axiom_lock_paid_reprint boolean -> selection before ORM update."""


def migrate(cr, version):
    cr.execute(
        """
        SELECT data_type
          FROM information_schema.columns
         WHERE table_name = 'pos_config'
           AND column_name = 'axiom_lock_paid_reprint'
        """
    )
    row = cr.fetchone()
    if not row:
        return
    data_type = (row[0] or "").lower()
    if data_type not in ("boolean", "bool"):
        return

    cr.execute(
        """
        ALTER TABLE pos_config
        ADD COLUMN IF NOT EXISTS axiom_paid_reprint_access VARCHAR
        """
    )
    cr.execute(
        """
        UPDATE pos_config
           SET axiom_paid_reprint_access = CASE
                WHEN axiom_lock_paid_reprint IS TRUE THEN 'admin'
                ELSE 'all'
           END
         WHERE axiom_paid_reprint_access IS NULL
        """
    )
    cr.execute("ALTER TABLE pos_config DROP COLUMN axiom_lock_paid_reprint")
