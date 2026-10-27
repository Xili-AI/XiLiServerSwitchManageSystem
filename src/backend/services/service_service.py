"""Service registry business logic."""
import logging
from datetime import datetime
from typing import List, Optional

from flask import current_app

from app.errors import ConflictError, NotFoundError, ValidationError
from app.extensions import db
from models.service import Service
from models.user import User
from services.audit_service import AuditService
from services.gateway_service import GatewayService
from services.settings_service import SettingsService
from utils.base_utils.url_util import build_path_url, build_public_url
from utils.base_utils.validation_util import normalize_service_payload
from utils.gateway_util.health_util import probe_http

logger = logging.getLogger(__name__)


def build_service_payload(service: Service, settings: dict) -> dict:
    """Attach computed public URLs to a serialized service."""
    payload = service.to_dict()
    if service.mode == "origin":
        # Direct-origin mode: no gateway route, the card links to the upstream.
        payload["public_url"] = service.target_url
        payload["path_url"] = service.target_url
        return payload
    payload["public_url"] = build_public_url(
        service.slug,
        settings.get("base_domain", ""),
        settings.get("public_scheme", "http"),
        settings.get("public_port", ""),
    )
    payload["path_url"] = build_path_url(service.slug)
    return payload


def local_port_map(services: List[Service], base_port: int) -> dict:
    """Assign one stable loopback port per enabled service, in display order.

    The same assignment is exposed to the wstunnel client, so a service can be
    reached as http://127.0.0.1:<port>/ with the application running at its own
    origin root (no path rewriting at all).
    """
    mapping = {}
    index = 0
    for service in services:
        if not service.is_enabled:
            continue
        mapping[service.id] = base_port + index
        index += 1
    return mapping


def build_stats(services: List[Service]) -> dict:
    """Compute dashboard counters for enabled services."""
    total = len(services)
    enabled_services = [service for service in services if service.is_enabled]
    online = len([service for service in enabled_services if service.is_online is True])
    offline = len([service for service in enabled_services if service.is_online is False])
    unknown = len(enabled_services) - online - offline
    latencies = [
        service.latency_ms
        for service in enabled_services
        if service.is_online and service.latency_ms is not None
    ]
    average_latency = int(sum(latencies) / len(latencies)) if latencies else None
    return {
        "total": total,
        "enabled": len(enabled_services),
        "online": online,
        "offline": offline,
        "unknown": unknown,
        "average_latency_ms": average_latency,
    }


class ServiceService:
    """CRUD and health operations for registered services."""

    @classmethod
    def get_service(cls, service_id: str, viewer: Optional[User] = None) -> Service:
        """Load a service, enforcing per-user grants for non-admins."""
        service = db.session.get(Service, service_id)
        if viewer is not None and not viewer.is_admin:
            if service is None or not service.is_enabled or not viewer.can_access(service.id):
                # Hide existence from users without a grant.
                raise NotFoundError("服务不存在")
        if service is None:
            raise NotFoundError("服务不存在")
        return service

    @classmethod
    def list_services(cls, viewer: Optional[User] = None) -> dict:
        """Return the services visible to ``viewer`` with computed URLs."""
        settings = SettingsService.get_settings()
        services = (
            Service.query.order_by(Service.sort_order.asc(), Service.created_at.asc()).all()
        )
        base_port = current_app.config.get("TUNNEL_LOCAL_PORT_BASE", 18100)
        # Local ports stay stable across users: compute them over the full list.
        port_map = local_port_map(services, base_port)

        if viewer is not None and not viewer.is_admin:
            allowed = set(viewer.service_ids)
            visible = [s for s in services if s.is_enabled and s.id in allowed]
        else:
            visible = services

        payloads = []
        for service in visible:
            payload = build_service_payload(service, settings)
            payload["local_port"] = port_map.get(service.id)
            payloads.append(payload)
        return {
            "services": payloads,
            "stats": build_stats(visible),
            "settings": settings,
        }

    @classmethod
    def create_service(
        cls,
        payload: dict,
        operator: User,
        ip_address: str = "",
    ) -> dict:
        """Register a new service and regenerate the gateway table."""
        normalized = normalize_service_payload(payload)
        if Service.query.filter_by(slug=normalized["slug"]).first() is not None:
            raise ConflictError(f"服务标识 {normalized['slug']} 已被使用")
        if not normalized["sort_order"]:
            max_order = db.session.query(db.func.max(Service.sort_order)).scalar() or 0
            normalized["sort_order"] = int(max_order) + 10

        service = Service(**normalized)
        db.session.add(service)
        AuditService.record(
            action="service.create",
            resource_type="service",
            resource_id=service.id,
            detail=f"name={service.name}, slug={service.slug}",
            user=operator,
            ip_address=ip_address,
        )
        db.session.commit()
        gateway = GatewayService.sync_safe()
        settings = SettingsService.get_settings()
        logger.info("新增服务: %s (%s)", service.name, service.slug)
        return {"service": build_service_payload(service, settings), "gateway": gateway}

    @classmethod
    def update_service(
        cls,
        service_id: str,
        payload: dict,
        operator: User,
        ip_address: str = "",
    ) -> dict:
        """Update a service and regenerate the gateway table."""
        service = cls.get_service(service_id)
        normalized = normalize_service_payload(payload)
        duplicate = Service.query.filter(
            Service.slug == normalized["slug"], Service.id != service.id
        ).first()
        if duplicate is not None:
            raise ConflictError(f"服务标识 {normalized['slug']} 已被使用")

        for key, value in normalized.items():
            setattr(service, key, value)
        AuditService.record(
            action="service.update",
            resource_type="service",
            resource_id=service.id,
            detail=f"name={service.name}, slug={service.slug}",
            user=operator,
            ip_address=ip_address,
        )
        db.session.commit()
        gateway = GatewayService.sync_safe()
        settings = SettingsService.get_settings()
        logger.info("更新服务: %s (%s)", service.name, service.slug)
        return {"service": build_service_payload(service, settings), "gateway": gateway}

    @classmethod
    def delete_service(
        cls,
        service_id: str,
        operator: User,
        ip_address: str = "",
    ) -> dict:
        """Delete a service and regenerate the gateway table."""
        service = cls.get_service(service_id)
        service_name = service.name
        service_slug = service.slug
        db.session.delete(service)
        AuditService.record(
            action="service.delete",
            resource_type="service",
            resource_id=service_id,
            detail=f"name={service_name}, slug={service_slug}",
            user=operator,
            ip_address=ip_address,
        )
        db.session.commit()
        gateway = GatewayService.sync_safe()
        logger.info("删除服务: %s (%s)", service_name, service_slug)
        return {"deleted_id": service_id, "gateway": gateway}

    @classmethod
    def reorder_services(
        cls,
        ordered_ids: List[str],
        operator: User,
        ip_address: str = "",
    ) -> dict:
        """Persist a new display order for services."""
        if not isinstance(ordered_ids, list) or not ordered_ids:
            raise ValidationError("排序列表不能为空")
        for index, service_id in enumerate(ordered_ids):
            service = db.session.get(Service, str(service_id))
            if service is not None:
                service.sort_order = (index + 1) * 10
        AuditService.record(
            action="service.reorder",
            resource_type="service",
            detail=f"count={len(ordered_ids)}",
            user=operator,
            ip_address=ip_address,
        )
        db.session.commit()
        gateway = GatewayService.sync_safe()
        settings = SettingsService.get_settings()
        services = (
            Service.query.order_by(Service.sort_order.asc(), Service.created_at.asc()).all()
        )
        return {
            "services": [build_service_payload(service, settings) for service in services],
            "gateway": gateway,
        }

    @classmethod
    def check_service(
        cls,
        service_id: str,
        operator: Optional[User] = None,
        ip_address: str = "",
    ) -> dict:
        """Run an immediate health probe for one service."""
        service = cls.get_service(service_id)
        settings = SettingsService.get_settings()
        result = probe_http(
            service.target_url,
            timeout_seconds=5,
            verify_tls=not settings.get("skip_tls_verify", False),
        )
        service.is_online = result["is_online"]
        service.latency_ms = result["latency_ms"]
        service.last_error = result["last_error"]
        service.last_checked_at = datetime.utcnow()
        AuditService.record(
            action="service.check",
            resource_type="service",
            resource_id=service.id,
            detail=f"online={result['is_online']}",
            user=operator,
            ip_address=ip_address,
        )
        db.session.commit()
        return {"service": build_service_payload(service, settings)}
