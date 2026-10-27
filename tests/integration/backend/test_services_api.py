"""Integration tests for the service registry."""
from pathlib import Path


class TestServiceAuth:
    """All service endpoints require a token."""

    def test_list_requires_token(self, client):
        response = client.get("/api/services")
        assert response.status_code == 401

    def test_create_requires_token(self, client, service_payload):
        response = client.post("/api/services", json=service_payload)
        assert response.status_code == 401


class TestServiceCrud:
    """Create, read, update and delete lifecycle."""

    def test_empty_list(self, client, auth_headers):
        response = client.get("/api/services", headers=auth_headers)
        assert response.status_code == 200
        payload = response.get_json()["data"]
        assert payload["services"] == []
        assert payload["stats"]["total"] == 0

    def test_create_and_list(self, client, auth_headers, service_payload):
        created = client.post("/api/services", headers=auth_headers, json=service_payload)
        assert created.status_code == 201
        body = created.get_json()["data"]
        service = body["service"]
        assert service["slug"] == "demo-service"
        assert service["public_url"] == "http://demo-service.localhost:8080/"
        assert service["path_url"] == "/p/demo-service/"
        assert body["gateway"]["synced"] is True

        listed = client.get("/api/services", headers=auth_headers)
        assert listed.get_json()["data"]["stats"]["total"] == 1

    def test_create_with_entry_path(self, client, auth_headers, service_payload):
        service_payload["entry_path"] = "/dashboard"
        created = client.post("/api/services", headers=auth_headers, json=service_payload)
        assert created.status_code == 201
        assert created.get_json()["data"]["service"]["entry_path"] == "/dashboard"

    def test_duplicate_slug(self, client, auth_headers, service_payload):
        client.post("/api/services", headers=auth_headers, json=service_payload)
        duplicate = client.post("/api/services", headers=auth_headers, json=service_payload)
        assert duplicate.status_code == 409
        assert "已被使用" in duplicate.get_json()["message"]

    def test_invalid_target(self, client, auth_headers, service_payload):
        service_payload["target_url"] = "file:///etc/passwd"
        response = client.post("/api/services", headers=auth_headers, json=service_payload)
        assert response.status_code == 400

    def test_update_service(self, client, auth_headers, service_payload):
        created = client.post("/api/services", headers=auth_headers, json=service_payload)
        service_id = created.get_json()["data"]["service"]["id"]
        service_payload["name"] = "Renamed"
        service_payload["mode"] = "subdomain"
        response = client.put(f"/api/services/{service_id}", headers=auth_headers, json=service_payload)
        assert response.status_code == 200
        updated = response.get_json()["data"]["service"]
        assert updated["name"] == "Renamed"
        assert updated["mode"] == "subdomain"

    def test_check_service(self, client, auth_headers, service_payload):
        created = client.post("/api/services", headers=auth_headers, json=service_payload)
        service_id = created.get_json()["data"]["service"]["id"]
        response = client.post(f"/api/services/{service_id}/check", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()["data"]["service"]["is_online"] is False

    def test_delete_service(self, client, auth_headers, service_payload):
        created = client.post("/api/services", headers=auth_headers, json=service_payload)
        service_id = created.get_json()["data"]["service"]["id"]
        response = client.delete(f"/api/services/{service_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()["data"]["deleted_id"] == service_id
        assert client.get("/api/services", headers=auth_headers).get_json()["data"]["stats"]["total"] == 0

    def test_missing_service_returns_404(self, client, auth_headers):
        response = client.get("/api/services/not-found", headers=auth_headers)
        assert response.status_code == 404

    def test_gateway_files_generated(self, client, auth_headers, service_payload):
        client.post("/api/services", headers=auth_headers, json=service_payload)
        hosts = Path(client.application.config["GATEWAY_HOSTS_FILE"])
        paths = Path(client.application.config["GATEWAY_PATHS_FILE"])
        assert "~^demo-service\\..+$" in hosts.read_text(encoding="utf-8")
        assert "location ^~ /p/demo-service/" in paths.read_text(encoding="utf-8")
