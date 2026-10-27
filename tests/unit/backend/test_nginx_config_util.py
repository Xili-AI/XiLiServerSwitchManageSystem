"""Unit tests for generated Nginx routing snippets."""
from types import SimpleNamespace

from utils.gateway_util.nginx_config_util import build_hosts_config, build_paths_config

SETTINGS = {
    "base_domain": "example.com",
    "public_scheme": "https",
    "skip_tls_verify": False,
}


def make_service(slug="demo", target="http://demo:8080", enabled=True, strip_prefix=True, mode="auto"):
    """Build the minimal service shape used by the config builder."""
    return SimpleNamespace(
        slug=slug,
        target_url=target,
        is_enabled=enabled,
        strip_prefix=strip_prefix,
        mode=mode,
    )


class TestHostsConfig:
    """Host-based routing blocks."""

    def test_contains_server_name_and_upstream(self):
        config = build_hosts_config([make_service()], SETTINGS)
        assert "server_name demo.example.com demo.localhost;" in config
        assert "set $svc_upstream http://demo:8080;" in config
        assert "proxy_set_header X-Forwarded-Proto https;" in config
        assert "proxy_hide_header X-Frame-Options;" in config

    def test_skips_disabled_service(self):
        config = build_hosts_config([make_service(enabled=False)], SETTINGS)
        assert "No enabled services" in config

    def test_https_target_sets_ssl_verification(self):
        config = build_hosts_config([make_service(target="https://demo:8443")], SETTINGS)
        assert "proxy_ssl_server_name on;" in config
        assert "proxy_ssl_verify on;" in config

    def test_wildcard_when_base_domain_empty(self):
        settings = {**SETTINGS, "base_domain": ""}
        config = build_hosts_config([make_service()], settings)
        assert "~^demo\\..+$" in config

    def test_localhost_uses_wildcard_for_tunnel_compatibility(self):
        settings = {**SETTINGS, "base_domain": "localhost"}
        config = build_hosts_config([make_service()], settings)
        assert "~^demo\\..+$" in config


class TestPathsConfig:
    """Path-mode fallback locations."""

    def test_contains_redirect_and_strip(self):
        config = build_paths_config([make_service()], SETTINGS)
        assert "location = /p/demo {" in config
        assert "return 308 /p/demo/;" in config
        assert "location ^~ /p/demo/ {" in config
        assert "rewrite ^/p/demo/(.*)$ /$1 break;" in config
        assert "proxy_redirect ~^(?:https?://[^/]+)?(?!/p/)(/.*)$ /p/demo$1;" in config
        assert "proxy_cookie_path / /p/demo/;" in config
        assert "proxy_set_header X-Forwarded-Prefix /p/demo;" in config
        assert "set $svc_upstream http://demo:8080;" in config

    def test_empty_state_comment(self):
        config = build_paths_config([], SETTINGS)
        assert "No path services" in config

    def test_origin_mode_generates_no_route(self):
        service = make_service(mode="origin")
        assert "No enabled services" in build_hosts_config([service], SETTINGS)
        assert "No path services" in build_paths_config([service], SETTINGS)

    def test_no_strip_keeps_base_path_for_apps_with_base_url(self):
        config = build_paths_config([make_service(strip_prefix=False)], SETTINGS)
        assert "rewrite ^/p/demo/(.*)$" not in config
        assert "proxy_redirect ~^(?:https?://[^/]+)?(?!/p/)(/.*)$" not in config
        assert "proxy_cookie_path / /p/demo/;" not in config
        assert "set $svc_upstream http://demo:8080;" in config
        assert "proxy_pass $svc_upstream;" in config
