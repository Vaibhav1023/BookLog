import sys, os, json, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tests.conftest import make_app


class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.client = self.app.test_client()

    def _post(self, path, data):
        return self.client.post(path, data=json.dumps(data), content_type="application/json")

    def _register(self, email="test@example.com", password="password123", name="Test"):
        return self._post("/api/auth/register", {"email": email, "password": password, "name": name})

    # ── Register ──────────────────────────────────────────────────

    def test_register_returns_201_with_token(self):
        resp = self._register()
        self.assertEqual(resp.status_code, 201)
        body = resp.get_json()
        self.assertIn("token", body)
        self.assertIn("user", body)
        self.assertEqual(body["user"]["email"], "test@example.com")

    def test_register_duplicate_email_returns_409(self):
        self._register()
        resp = self._register()
        self.assertEqual(resp.status_code, 409)

    def test_register_invalid_email_returns_400(self):
        resp = self._post("/api/auth/register", {"email": "notanemail", "password": "password123"})
        self.assertEqual(resp.status_code, 400)

    def test_register_short_password_returns_400(self):
        resp = self._post("/api/auth/register", {"email": "a@b.com", "password": "short"})
        self.assertEqual(resp.status_code, 400)

    def test_register_missing_fields_returns_400(self):
        resp = self._post("/api/auth/register", {})
        self.assertEqual(resp.status_code, 400)

    # ── Login ─────────────────────────────────────────────────────

    def test_login_returns_200_with_token(self):
        self._register()
        resp = self._post("/api/auth/login", {"email": "test@example.com", "password": "password123"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("token", resp.get_json())

    def test_login_wrong_password_returns_401(self):
        self._register()
        resp = self._post("/api/auth/login", {"email": "test@example.com", "password": "wrongpass"})
        self.assertEqual(resp.status_code, 401)

    def test_login_unknown_email_returns_401(self):
        resp = self._post("/api/auth/login", {"email": "nobody@example.com", "password": "password123"})
        self.assertEqual(resp.status_code, 401)

    def test_login_case_insensitive_email(self):
        self._register(email="User@Example.COM")
        resp = self._post("/api/auth/login", {"email": "user@example.com", "password": "password123"})
        self.assertEqual(resp.status_code, 200)

    # ── Me ────────────────────────────────────────────────────────

    def test_me_with_valid_token_returns_user(self):
        token = self._register().get_json()["token"]
        resp = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)

    def test_me_without_token_returns_401(self):
        resp = self.client.get("/api/auth/me")
        self.assertEqual(resp.status_code, 401)

    def test_me_with_bad_token_returns_401(self):
        resp = self.client.get("/api/auth/me", headers={"Authorization": "Bearer bad.token.here"})
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
