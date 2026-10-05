"""Workbench domain services（Phase 2 / v1.3 增 Entity + Coverage）。

职责：artifact schema → domain query result。
Web/API 不得自己理解 artifact 格式，也不得直接读 legacy 数据。

读取范围（硬约束，见 store.py）：registry/ · artifacts/active/ · residuals/ · evidence/ · state/
禁止：legacy boards · historical artifacts · 391KB 日志 · raw package · LOCATOR DB

v1.3：列表查询统一走分页（services/query.py），默认不返回全量。
"""
from .item_service import ItemService  # noqa: F401
from .fashion_service import FashionService  # noqa: F401
from .weapon_skin_service import WeaponSkinService  # noqa: F401
from .lottery_service import LotteryService  # noqa: F401
from .status_service import StatusService  # noqa: F401
from .entity_service import EntityService, KINDS  # noqa: F401
from .coverage_service import CoverageService  # noqa: F401
from .query import PAGE_SIZE_MAX, PAGE_SIZE_DEFAULT, norm_page, page_meta  # noqa: F401
