import sys, os, tempfile, unittest
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.database import init_db
from app.repositories.book_repository import BookRepository
from app.repositories.user_repository import UserRepository
from app.services.book_service import BookService, BookNotFoundError, BookRuleViolation
from app.services.auth_service import AuthService, AuthError


def make_services():
    tmp = tempfile.mktemp(suffix=".db")
    init_db(tmp)
    user_repo = UserRepository(db_path=tmp)
    book_repo = BookRepository(db_path=tmp)
    return AuthService(user_repo), BookService(book_repo), user_repo


BOOK = {"title": "Dune", "author": "Frank Herbert", "status": "want_to_read"}


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.auth, self.books, self.user_repo = make_services()

    def test_register_returns_user_and_token(self):
        user, token = self.auth.register("a@b.com", "password123")
        self.assertIsNotNone(user.id)
        self.assertIsNotNone(token)

    def test_register_duplicate_raises_auth_error(self):
        self.auth.register("a@b.com", "password123")
        with self.assertRaises(AuthError):
            self.auth.register("a@b.com", "password123")

    def test_login_valid_credentials(self):
        self.auth.register("a@b.com", "password123")
        user, token = self.auth.login("a@b.com", "password123")
        self.assertIsNotNone(token)

    def test_login_wrong_password_raises(self):
        self.auth.register("a@b.com", "password123")
        with self.assertRaises(AuthError):
            self.auth.login("a@b.com", "wrongpass")

    def test_login_unknown_email_raises(self):
        with self.assertRaises(AuthError):
            self.auth.login("nobody@b.com", "password123")


class TestBookService(unittest.TestCase):
    def setUp(self):
        self.auth, self.svc, self.user_repo = make_services()
        user, _ = self.auth.register("user@example.com", "password123")
        self.user_id = user.id

    def test_add_book_sets_today_date(self):
        book = self.svc.add_book(self.user_id, BOOK)
        self.assertEqual(book.date_added, date.today())
        self.assertEqual(book.user_id, self.user_id)

    def test_finished_book_gets_date_finished(self):
        book = self.svc.add_book(self.user_id, {**BOOK, "status": "finished"})
        self.assertEqual(book.date_finished, date.today())

    def test_rating_on_finished_accepted(self):
        book = self.svc.add_book(self.user_id, {**BOOK, "status": "finished", "rating": 4})
        self.assertEqual(book.rating, 4)

    def test_rating_on_reading_raises_rule_violation(self):
        with self.assertRaises(BookRuleViolation):
            self.svc.add_book(self.user_id, {**BOOK, "status": "reading", "rating": 3})

    def test_rating_on_want_to_read_raises_rule_violation(self):
        with self.assertRaises(BookRuleViolation):
            self.svc.add_book(self.user_id, {**BOOK, "rating": 5})

    def test_duplicate_isbn_raises_value_error(self):
        isbn = "9780756404079"
        self.svc.add_book(self.user_id, {**BOOK, "isbn": isbn})
        with self.assertRaises(ValueError):
            self.svc.add_book(self.user_id, {**BOOK, "title": "Other", "isbn": isbn})

    def test_two_books_without_isbn_allowed(self):
        b1 = self.svc.add_book(self.user_id, BOOK)
        b2 = self.svc.add_book(self.user_id, {**BOOK, "title": "Other"})
        self.assertNotEqual(b1.id, b2.id)

    def test_get_book_not_found_raises(self):
        with self.assertRaises(BookNotFoundError):
            self.svc.get_book(999, self.user_id)

    def test_user_cannot_access_other_users_book(self):
        user2, _ = self.auth.register("other@example.com", "password123")
        book = self.svc.add_book(self.user_id, BOOK)
        with self.assertRaises(BookNotFoundError):
            self.svc.get_book(book.id, user2.id)

    def test_update_clears_rating_on_non_ratable_status(self):
        book = self.svc.add_book(self.user_id, {**BOOK, "status": "finished", "rating": 5})
        updated = self.svc.update_book(book.id, self.user_id, {"status": "want_to_read"})
        self.assertIsNone(updated.rating)

    def test_update_auto_sets_date_finished(self):
        book = self.svc.add_book(self.user_id, BOOK)
        updated = self.svc.update_book(book.id, self.user_id, {"status": "finished"})
        self.assertEqual(updated.date_finished, date.today())

    def test_delete_removes_book(self):
        book = self.svc.add_book(self.user_id, BOOK)
        self.svc.delete_book(book.id, self.user_id)
        with self.assertRaises(BookNotFoundError):
            self.svc.get_book(book.id, self.user_id)

    def test_delete_missing_raises(self):
        with self.assertRaises(BookNotFoundError):
            self.svc.delete_book(999, self.user_id)

    def test_stats_correct(self):
        self.svc.add_book(self.user_id, {**BOOK, "status": "finished", "rating": 4, "page_count": 300})
        self.svc.add_book(self.user_id, {**BOOK, "title": "B", "status": "reading", "page_count": 200})
        stats = self.svc.get_stats(self.user_id)
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["finished"], 1)
        self.assertEqual(stats["total_pages"], 500)

    def test_stats_isolated_per_user(self):
        user2, _ = self.auth.register("other@example.com", "password123")
        self.svc.add_book(self.user_id, BOOK)
        stats = self.svc.get_stats(user2.id)
        self.assertEqual(stats["total"], 0)


if __name__ == "__main__":
    unittest.main()
