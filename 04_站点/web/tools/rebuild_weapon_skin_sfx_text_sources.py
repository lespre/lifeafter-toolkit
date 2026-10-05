#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compatibility entrypoint for the current full weapon-skin catalog.

Historically this command emitted only the 20 named SFX labels grouped as nine
parents.  That incomplete shape could overwrite the full catalog, so the
entrypoint now delegates to the 125-parent rebuild.  SFX remain child rows.
"""
from __future__ import annotations

from rebuild_weapon_skin_catalog_current import main


if __name__ == "__main__":
    raise SystemExit(main())
