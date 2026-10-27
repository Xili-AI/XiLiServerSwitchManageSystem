"""Import services from the previous Node.js portal.

Usage (from src/backend):
    python scripts/import_legacy_services.py
"""
import json
from pathlib import Path

from server import app
from app.extensions import db
from models.service import Service
from services.gateway_service import GatewayService
from utils.base_utils.validation_util import normalize_service_payload

LEGACY_FILE = Path(__file__).resolve().parents[3] / "docker" / "legacy" / "portal-data" / "services.json"


def main() -> int:
    """Import legacy service records while preserving existing slugs."""
    if not LEGACY_FILE.exists():
        print(f"未找到旧数据文件: {LEGACY_FILE}")
        return 1

    payload = json.loads(LEGACY_FILE.read_text(encoding="utf-8"))
    records = payload.get("services", payload if isinstance(payload, list) else [])
    with app.app_context():
        imported = 0
        for record in records:
            if Service.query.filter_by(slug=record.get("slug")).first() is not None:
                continue
            normalized = normalize_service_payload(
                {
                    "name": record.get("name"),
                    "slug": record.get("slug"),
                    "target_url": record.get("target") or record.get("target_url"),
                    "description": record.get("description", ""),
                    "color": record.get("color", "#5fd3f3"),
                    "icon": record.get("icon", "server"),
                    "mode": record.get("mode", "auto"),
                    "is_enabled": record.get("enabled", True),
                    "sort_order": record.get("sort_order", 0),
                }
            )
            db.session.add(Service(**normalized))
            imported += 1
        db.session.commit()
        GatewayService.sync_safe()
        print(f"已导入 {imported} 个服务")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
