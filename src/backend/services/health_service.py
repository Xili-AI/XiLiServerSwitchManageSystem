"""Background health checks for registered services."""
import logging
import threading
from datetime import datetime

from app.extensions import db
from models.service import Service
from services.settings_service import SettingsService
from utils.gateway_util.health_util import probe_http

logger = logging.getLogger(__name__)

WORKER_STARTED = False
STOP_EVENT = threading.Event()
WORKER_LOCK = threading.Lock()


def update_service_status(service: Service, result: dict) -> bool:
    """Apply a probe result and return whether the online state changed."""
    previous = service.is_online
    service.is_online = result["is_online"]
    service.latency_ms = result["latency_ms"]
    service.last_error = result["last_error"]
    service.last_checked_at = datetime.utcnow()
    return previous != service.is_online


def check_all_services(app) -> None:
    """Probe every enabled service and persist the results."""
    with app.app_context():
        settings = SettingsService.get_settings()
        services = Service.query.filter_by(is_enabled=True).all()
        verify_tls = not settings.get("skip_tls_verify", False)
        timeout_seconds = app.config["HEALTH_TIMEOUT_SECONDS"]
        changed = False
        for service in services:
            result = probe_http(service.target_url, timeout_seconds, verify_tls)
            if update_service_status(service, result):
                changed = True
                logger.info(
                    "服务 %s 状态变为 %s", service.slug, "在线" if result["is_online"] else "离线"
                )
        db.session.commit()
        if changed:
            logger.debug("健康检查完成，状态有变化")
        db.session.remove()


def worker_loop(app) -> None:
    """Run the periodic health-check loop until the process exits."""
    app.logger.info("健康检查后台线程已启动")
    while not STOP_EVENT.is_set():
        try:
            check_all_services(app)
        except Exception as error:
            app.logger.exception("健康检查执行失败: %s", error)
        try:
            with app.app_context():
                interval = SettingsService.get_settings().get("health_interval", 20)
        except Exception:
            interval = 20
        STOP_EVENT.wait(max(5, int(interval)))


class HealthService:
    """Start and inspect the health-check worker."""

    @classmethod
    def start_worker(cls, app) -> None:
        """Start exactly one background worker per process."""
        global WORKER_STARTED

        with WORKER_LOCK:
            if WORKER_STARTED:
                return
            WORKER_STARTED = True
        STOP_EVENT.clear()
        thread = threading.Thread(
            target=worker_loop,
            args=(app,),
            name="serverswitchmanagesystem-health-worker",
            daemon=True,
        )
        thread.start()

    @classmethod
    def check_now(cls, app) -> None:
        """Run one synchronous check cycle (used by tests and scripts)."""
        check_all_services(app)
