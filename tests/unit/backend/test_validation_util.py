"""Unit tests for input validation."""
import pytest

from app.errors import ValidationError
from utils.base_utils.validation_util import (
    normalize_base_domain,
    normalize_entry_path,
    normalize_service_payload,
    normalize_target_url,
    validate_password_strength,
)


class TestTargetUrl:
    """Target URL normalisation."""

    def test_adds_http_scheme(self):
        assert normalize_target_url("localhost:8080") == "http://localhost:8080"

    def test_accepts_https(self):
        assert normalize_target_url("https://internal.example:9443") == "https://internal.example:9443"

    def test_rejects_path(self):
        with pytest.raises(ValidationError, match="不支持路径前缀"):
            normalize_target_url("http://localhost:8080/admin")

    def test_rejects_query(self):
        with pytest.raises(ValidationError, match="查询参数"):
            normalize_target_url("http://localhost:8080?token=x")

    def test_rejects_unsupported_scheme(self):
        with pytest.raises(ValidationError, match="只支持"):
            normalize_target_url("file:///etc/passwd")


class TestServicePayload:
    """Service payload validation."""

    def test_normalizes_payload(self, service_payload):
        result = normalize_service_payload(service_payload)
        assert result["slug"] == "demo-service"
        assert result["target_url"] == "http://127.0.0.1:1"
        assert result["mode"] == "auto"

    def test_rejects_reserved_slug(self, service_payload):
        service_payload["slug"] = "api"
        with pytest.raises(ValidationError, match="保留字"):
            normalize_service_payload(service_payload)

    def test_maps_legacy_host_mode(self, service_payload):
        service_payload["mode"] = "host"
        result = normalize_service_payload(service_payload)
        assert result["mode"] == "subdomain"

    def test_rejects_invalid_color(self, service_payload):
        service_payload["color"] = "blue"
        with pytest.raises(ValidationError, match="颜色"):
            normalize_service_payload(service_payload)

    def test_normalizes_entry_path(self, service_payload):
        service_payload["entry_path"] = "/dashboard"
        result = normalize_service_payload(service_payload)
        assert result["entry_path"] == "/dashboard"

    def test_rejects_entry_path_without_leading_slash(self):
        with pytest.raises(ValidationError, match="入口路径"):
            normalize_entry_path("dashboard")

    def test_rejects_entry_path_with_query(self):
        with pytest.raises(ValidationError, match="入口路径"):
            normalize_entry_path("/dashboard?x=1")


class TestSettingsAndPassword:
    """Settings and password validation."""

    def test_normalizes_base_domain(self):
        assert normalize_base_domain("*.Example.com.") == "example.com"

    def test_rejects_domain_with_protocol(self):
        with pytest.raises(ValidationError, match="协议"):
            normalize_base_domain("https://example.com")

    def test_rejects_ip_as_base_domain(self):
        with pytest.raises(ValidationError, match="不能是 IP"):
            normalize_base_domain("192.168.1.12")

    def test_password_strength(self):
        assert validate_password_strength("Password123") == "Password123"

    def test_rejects_short_password(self):
        with pytest.raises(ValidationError, match="8"):
            validate_password_strength("Ab1")

    def test_rejects_letters_only(self):
        with pytest.raises(ValidationError, match="字母和数字"):
            validate_password_strength("PasswordOnly")
