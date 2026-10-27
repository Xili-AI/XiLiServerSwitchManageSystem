"""Public health and bootstrap endpoints."""
import hmac
from datetime import datetime

from flask import Blueprint, abort, current_app, request

from models.service import Service
from services.service_service import local_port_map
from services.settings_service import SettingsService
from utils.base_utils.response_util import success

root_bp = Blueprint("root", __name__)


@root_bp.get("/health")
def health():
    """Return a lightweight health payload for probes and the login screen."""
    settings = SettingsService.get_public_settings()
    return success(
        {
            "status": "ok",
            "version": settings["version"],
            "site_name": settings["site_name"],
            "time": datetime.utcnow().isoformat(),
        },
        "服务正常",
    )


@root_bp.get("/public/info")
def public_info():
    """Return non-sensitive product metadata."""
    return success(SettingsService.get_public_settings())


@root_bp.get("/tunnel/endpoints")
def tunnel_endpoints():
    """Return the loopback port map used by the wstunnel client.

    Authenticated with the shared ``TUNNEL_SECRET`` instead of a user JWT: the
    client already holds that secret, and it already grants full access to the
    internal network through the tunnel.
    """
    expected = current_app.config.get("TUNNEL_SECRET", "")
    supplied = request.headers.get("X-Tunnel-Secret", "")
    if not expected or not hmac.compare_digest(supplied, expected):
        abort(403, description="invalid tunnel secret")

    services = (
        Service.query.filter_by(is_enabled=True)
        .order_by(Service.sort_order.asc(), Service.created_at.asc())
        .all()
    )
    base_port = current_app.config.get("TUNNEL_LOCAL_PORT_BASE", 18100)
    port_map = local_port_map(services, base_port)
    return success(
        {
            "local_port_base": base_port,
            "endpoints": [
                {
                    "slug": service.slug,
                    "name": service.name,
                    "mode": service.mode,
                    "target_url": service.target_url,
                    "local_port": port_map[service.id],
                }
                for service in services
            ],
        }
    )
