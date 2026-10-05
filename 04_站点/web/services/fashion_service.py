"""Fashion domain service（**不伪造 resolved entity**）。"""
from __future__ import annotations

import json
from typing import Any

from .store import active_path, RESIDUALS


class FashionService:
    domain = "fashion"

    def __init__(self, path=None) -> None:
        self._path = path or active_path("fashion", "FASHION_IDENTITY_STATE.json")

    def state(self) -> dict[str, Any]:
        return json.loads(self._path.read_text(encoding="utf-8"))

    def status(self) -> dict[str, Any]:
        state = self.state()
        return {
            "domain": "fashion",
            "kind": state.get("kind"),
            "verified": state.get("verified_chain"),
            "unresolved": state.get("unresolved"),
            "prohibition": state.get("prohibition"),
            "residual_ref": state.get("residual_ref"),
        }

    def residual(self) -> dict[str, Any]:
        return json.loads((RESIDUALS / "fashion" / "binding_residuals.json").read_text(encoding="utf-8"))
