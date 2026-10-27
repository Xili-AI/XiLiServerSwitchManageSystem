"""Input validation for API payloads."""
import ipaddress
import re
from typing import Optional
from urllib.parse import urlsplit

from app.errors import ValidationError
from utils.base_utils.slug_util import RESERVED_SLUGS, is_valid_slug, slugify

COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
ICON_PATTERN = re.compile(r"^[a-z0-9-]{1,32}$")
DOMAIN_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?$")
WEAK_PASSWORDS = {"12345678", "password", "admin123", "changeme", "qwerty123"}
SERVICE_MODES = {"auto", "subdomain", "path", "origin"}
LEGACY_MODE_MAP = {"host": "subdomain"}


def require_text(data: dict, key: str, label: str, max_length: int, min_length: int = 1) -> str:
    """Read, trim and validate a required string field."""
    value = str(data.get(key, "") or "").strip()
    if len(value) < min_length:
        raise ValidationError(f"{label}不能为空")
    if len(value) > max_length:
        raise ValidationError(f"{label}最多 {max_length} 个字符")
    return value


def optional_text(data: dict, key: str, label: str, max_length: int) -> str:
    """Read and validate an optional string field."""
    value = str(data.get(key, "") or "").strip()
    if len(value) > max_length:
        raise ValidationError(f"{label}最多 {max_length} 个字符")
    return value


def normalize_target_url(value: str) -> str:
    """Validate an internal HTTP target and return its origin."""
    text = str(value or "").strip()
    if not text:
        raise ValidationError("目标地址不能为空")
    if not re.match(r"^[a-z][a-z0-9+.-]*://", text, re.IGNORECASE):
        text = f"http://{text}"
    parsed = urlsplit(text)
    if parsed.scheme not in {"http", "https"}:
        raise ValidationError("目标地址只支持 http:// 或 https://")
    if not parsed.hostname:
        raise ValidationError("目标地址缺少主机名")
    if parsed.username or parsed.password:
        raise ValidationError("目标地址不能包含用户名或密码")
    if parsed.query or parsed.fragment:
        raise ValidationError("目标地址不能包含查询参数或锚点")
    if parsed.path not in {"", "/"}:
        raise ValidationError("目标地址只填写协议、主机和端口，不支持路径前缀")
    try:
        port = parsed.port
    except ValueError as error:
        raise ValidationError("目标端口不合法") from error
    if port is not None and not 1 <= port <= 65535:
        raise ValidationError("目标端口必须在 1-65535 之间")
    return f"{parsed.scheme}://{parsed.netloc}"


def normalize_entry_path(value) -> str:
    """Validate an optional browser landing path for a service UI."""
    text = str(value or "").strip()
    if not text or text == "/":
        return ""
    if not text.startswith("/") or text.startswith("//"):
        raise ValidationError("入口路径必须以单个 / 开头")
    if "?" in text or "#" in text or any(character.isspace() for character in text):
        raise ValidationError("入口路径不能包含查询参数、锚点或空格")
    if len(text) > 200:
        raise ValidationError("入口路径最多 200 个字符")
    return text


def normalize_service_payload(data: dict) -> dict:
    """Validate and normalize a service create/update payload."""
    name = require_text(data, "name", "服务名称", 80)
    slug_value = str(data.get("slug", "") or "").strip().lower()
    if not slug_value:
        slug_value = slugify(name)
    if not slug_value:
        raise ValidationError("请填写服务标识")
    if not is_valid_slug(slug_value):
        raise ValidationError("服务标识只能包含小写字母、数字和中划线，长度 1-32 位")
    if slug_value in RESERVED_SLUGS:
        raise ValidationError(f"服务标识 {slug_value} 是系统保留字")

    mode = str(data.get("mode", "auto") or "auto").strip().lower()
    mode = LEGACY_MODE_MAP.get(mode, mode)
    if mode not in SERVICE_MODES:
        raise ValidationError("访问模式只能是 auto、subdomain、path 或 origin")

    color = str(data.get("color", "#5fd3f3") or "#5fd3f3").strip()
    if not COLOR_PATTERN.match(color):
        raise ValidationError("颜色必须是 #RRGGBB 格式")

    icon = str(data.get("icon", "server") or "server").strip().lower()
    if not ICON_PATTERN.match(icon):
        raise ValidationError("服务图标格式不正确")

    enabled = data.get("is_enabled", True)
    if not isinstance(enabled, bool):
        enabled = str(enabled).lower() in {"1", "true", "yes", "on"}

    strip_prefix = data.get("strip_prefix", True)
    if not isinstance(strip_prefix, bool):
        strip_prefix = str(strip_prefix).lower() in {"1", "true", "yes", "on"}

    sort_order = data.get("sort_order", 0)
    try:
        sort_order = int(sort_order)
    except (TypeError, ValueError):
        sort_order = 0

    return {
        "name": name,
        "slug": slug_value,
        "target_url": normalize_target_url(data.get("target_url") or data.get("target") or ""),
        "entry_path": normalize_entry_path(data.get("entry_path", "")),
        "strip_prefix": strip_prefix,
        "description": optional_text(data, "description", "服务描述", 200),
        "color": color.lower(),
        "icon": icon,
        "mode": mode,
        "is_enabled": enabled,
        "sort_order": sort_order,
    }


def normalize_base_domain(value: str) -> str:
    """Normalize a public base domain without scheme or port."""
    text = str(value or "").strip().lower()
    text = text.replace("*.", "")
    text = text.strip(".")
    if not text:
        return ""
    if text.startswith("http://") or text.startswith("https://"):
        raise ValidationError("主域名不要填写协议")
    if "/" in text or ":" in text or " " in text:
        raise ValidationError("主域名只填写域名，不要带路径或端口")
    if len(text) > 253 or not DOMAIN_PATTERN.match(text):
        raise ValidationError("主域名格式不正确")
    try:
        ipaddress.ip_address(text)
    except ValueError:
        return text
    raise ValidationError("主域名不能是 IP，请填真实域名，或留空使用 localhost")


def normalize_settings_payload(data: dict) -> dict:
    """Validate the editable gateway settings."""
    result = {}
    if "base_domain" in data:
        result["base_domain"] = normalize_base_domain(data.get("base_domain"))
    if "public_scheme" in data:
        scheme = str(data.get("public_scheme", "") or "").strip().lower()
        if scheme not in {"http", "https"}:
            raise ValidationError("公网协议只能是 http 或 https")
        result["public_scheme"] = scheme
    if "public_port" in data:
        port = str(data.get("public_port", "") or "").strip()
        if port:
            if not port.isdigit() or not 1 <= int(port) <= 65535:
                raise ValidationError("公网端口必须是 1-65535 的数字")
        result["public_port"] = port
    if "health_interval" in data:
        try:
            interval = int(data.get("health_interval"))
        except (TypeError, ValueError) as error:
            raise ValidationError("健康检查间隔必须是数字") from error
        if not 5 <= interval <= 3600:
            raise ValidationError("健康检查间隔必须在 5-3600 秒之间")
        result["health_interval"] = interval
    if "skip_tls_verify" in data:
        value = data.get("skip_tls_verify")
        if not isinstance(value, bool):
            value = str(value).lower() in {"1", "true", "yes", "on"}
        result["skip_tls_verify"] = value
    if "site_name" in data:
        result["site_name"] = require_text(data, "site_name", "站点名称", 60)
    return result


def validate_password_strength(password: Optional[str]) -> str:
    """Validate a password for the administrator account."""
    value = str(password or "")
    if len(value) < 8:
        raise ValidationError("密码至少需要 8 个字符")
    if len(value) > 128:
        raise ValidationError("密码最多 128 个字符")
    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        raise ValidationError("密码必须同时包含字母和数字")
    if value.lower() in WEAK_PASSWORDS:
        raise ValidationError("密码过于常见，请更换")
    return value
