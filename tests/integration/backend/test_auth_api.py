"""Integration tests for authentication endpoints."""

PASSWORD = "TestPass123"


class TestLogin:
    """Login contract and error handling."""

    def test_login_success(self, client):
        response = client.post("/api/auth/login", json={"username": "admin", "password": PASSWORD})
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["code"] == 200
        assert payload["data"]["token"]
        assert payload["data"]["user"]["username"] == "admin"
        assert "password_hash" not in payload["data"]["user"]

    def test_login_wrong_password(self, client):
        response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
        assert response.status_code == 401
        assert response.get_json()["code"] == 401

    def test_login_missing_fields(self, client):
        response = client.post("/api/auth/login", json={"username": "admin"})
        assert response.status_code == 400

    def test_login_unknown_user(self, client):
        response = client.post("/api/auth/login", json={"username": "ghost", "password": "wrong"})
        assert response.status_code == 401


class TestProfileAndLogout:
    """Profile access and token revocation."""

    def test_profile_requires_token(self, client):
        response = client.get("/api/auth/profile")
        assert response.status_code == 401

    def test_profile_success(self, client, auth_headers):
        response = client.get("/api/auth/profile", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()["data"]["username"] == "admin"

    def test_logout_invalidates_token(self, client, auth_headers):
        logout = client.post("/api/auth/logout", headers=auth_headers)
        assert logout.status_code == 200
        profile = client.get("/api/auth/profile", headers=auth_headers)
        assert profile.status_code == 401
        assert "失效" in profile.get_json()["message"]

    def test_change_password_rejects_wrong_old_password(self, client, auth_headers):
        response = client.post(
            "/api/auth/change-password",
            headers=auth_headers,
            json={"old_password": "wrong", "new_password": "NewPass123"},
        )
        assert response.status_code == 401

    def test_change_password_strength(self, client, auth_headers):
        response = client.post(
            "/api/auth/change-password",
            headers=auth_headers,
            json={"old_password": PASSWORD, "new_password": "short"},
        )
        assert response.status_code == 400
