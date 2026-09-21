"""fashion domain builder（包装器 / 状态生成器）。

**不生成假 resolved 主表**：只重新导出 active 的 identity state（已证的语义链 + 未证清单）。
"""
from __future__ import annotations
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / "artifacts" / "active" / "fashion" / "FASHION_IDENTITY_STATE.json"


def main() -> int:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    print(json.dumps({"verified_chain": state["verified_chain"]["status"], "unresolved": list(state["unresolved"])}, ensure_ascii=False, indent=1))
    if state.get("kind") == "identity_state_not_resolved":
        print("OK fashion active = state（未解析主表，按设计）")
        return 0
    print("FAIL fashion active 不得是 resolved 主表")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
