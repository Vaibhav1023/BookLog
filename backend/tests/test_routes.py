import sys, os, json, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tests.conftest import make_app


class TestBookRoutes(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.client = self.app.test_client()
        # Register and get token
        resp = self.client.post(
            "/api/auth/register",
            data=json.dumps({"email": "test@example.com", "password": "password123"}),
            content_type="application/json",
        )
        self.token = resp.get_json()["token"]

    def _auth(self):
        return {"Authorization": f"Bearer {self.token}"}

    def _post_book(self, data=None):
        data = data or {"title": "Dune", "author": "Herbert", "status": "want_to_read"}
        return self.client.post(
            "/api/books",
            data=json.dumps(data),
            content_type="application/json",
            headers=self._auth(),
        )

    # ── Auth protection ───────────────────────────────────────────

    def test_list_without_token_returns_401(self):
        resp = self.client.get("/api/books")
        self.assertEqual(resp.status_code, 401)

    def test_create_without_token_returns_401(self):
        resp = self.client.post("/api/books", data=json.dumps({}), content_type="application/json")
        self.assertEqual(resp.status_code, 401)

    # ── CRUD ──────────────────────────────────────────────────────

    def test_create_book_returns_201(self):
        resp = self._post_book()
        self.assertEqual(resp.status_code, 201)
        self.assertIsNotNone(resp.get_json()["id"])

    def test_list_books_returns_200(self):
        self._post_book()
        resp = self.client.get("/api/books", headers=self._auth())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 1)

    def test_get_book_returns_200(self):
        created = self._post_book().get_json()
        resp = self.client.get(f"/api/books/{created['id']}", headers=self._auth())
        self.assertEqual(resp.status_code, 200)

    def test_get_missing_book_returns_404(self):
        resp = self.client.get("/api/books/9999", headers=self._auth())
        self.assertEqual(resp.status_code, 404)

    def test_update_book_notes(self):
        created = self._post_book().get_json()
        resp = self.client.patch(
            f"/api/books/{created['id']}",
            data=json.dumps({"notes": "Great"}),
            content_type="application/json",
            headers=self._auth(),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["notes"], "Great")

    def test_mark_finished_sets_date(self):
        created = self._post_book().get_json()
        resp = self.client.patch(
            f"/api/books/{created['id']}",
            data=json.dumps({"status": "finished"}),
            content_type="application/json",
            headers=self._auth(),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.get_json()["date_finished"])

    def test_delete_book_returns_204(self):
        created = self._post_book().get_json()
        resp = self.client.delete(f"/api/books/{created['id']}", headers=self._auth())
        self.assertEqual(resp.status_code, 204)

    def test_delete_then_get_returns_404(self):
        created = self._post_book().get_json()
        self.client.delete(f"/api/books/{created['id']}", headers=self._auth())
        resp = self.client.get(f"/api/books/{created['id']}", headers=self._auth())
        self.assertEqual(resp.status_code, 404)

    # ── Validation ────────────────────────────────────────────────

    def test_create_missing_title_returns_400(self):
        resp = self._post_book({"author": "X", "status": "reading"})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("errors", resp.get_json())

    def test_create_rating_on_want_to_read_returns_400(self):
        resp = self._post_book({"title": "X", "author": "Y", "status": "want_to_read", "rating": 5})
        self.assertEqual(resp.status_code, 400)

    def test_create_duplicate_isbn_returns_409(self):
        self._post_book({"title": "A", "author": "X", "status": "reading", "isbn": "9780756404079"})
        resp = self._post_book({"title": "B", "author": "Y", "status": "reading", "isbn": "9780756404079"})
        self.assertEqual(resp.status_code, 409)

    # ── Data isolation ────────────────────────────────────────────

    def test_user2_cannot_see_user1_books(self):
        self._post_book()
        # Register second user
        resp2 = self.client.post(
            "/api/auth/register",
            data=json.dumps({"email": "other@example.com", "password": "password123"}),
            content_type="application/json",
        )
        token2 = resp2.get_json()["token"]
        books = self.client.get("/api/books", headers={"Authorization": f"Bearer {token2}"}).get_json()
        self.assertEqual(len(books), 0)

    # ── Stats ─────────────────────────────────────────────────────

    def test_stats_returns_200(self):
        resp = self.client.get("/api/books/stats", headers=self._auth())
        self.assertEqual(resp.status_code, 200)
        self.assertIn("total", resp.get_json())

    # ── Filter ────────────────────────────────────────────────────

    def test_filter_by_status(self):
        self._post_book({"title": "A", "author": "X", "status": "reading"})
        self._post_book({"title": "B", "author": "Y", "status": "finished"})
        resp = self.client.get("/api/books?status=reading", headers=self._auth())
        books = resp.get_json()
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]["status"], "reading")


if __name__ == "__main__":
    unittest.main()
