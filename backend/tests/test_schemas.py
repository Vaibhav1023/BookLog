import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.schemas.schemas import validate_create_book, validate_update_book, validate_register, validate_login


class TestValidateCreateBook(unittest.TestCase):

    def test_minimal_valid(self):
        clean, errors = validate_create_book({"title": "Dune", "author": "Herbert", "status": "want_to_read"})
        self.assertEqual(errors, [])
        self.assertEqual(clean["title"], "Dune")

    def test_whitespace_stripped(self):
        clean, errors = validate_create_book({"title": "  Dune  ", "author": "  Herbert  ", "status": "reading"})
        self.assertEqual(errors, [])
        self.assertEqual(clean["title"], "Dune")
        self.assertEqual(clean["author"], "Herbert")

    def test_isbn_normalised(self):
        clean, errors = validate_create_book({"title": "X", "author": "Y", "status": "reading", "isbn": "978-0-7564-0407-9"})
        self.assertEqual(errors, [])
        self.assertEqual(clean["isbn"], "9780756404079")

    def test_rating_on_finished_valid(self):
        clean, errors = validate_create_book({"title": "X", "author": "Y", "status": "finished", "rating": 5})
        self.assertEqual(errors, [])

    def test_rating_on_abandoned_valid(self):
        clean, errors = validate_create_book({"title": "X", "author": "Y", "status": "abandoned", "rating": 2})
        self.assertEqual(errors, [])

    def test_rating_on_want_to_read_invalid(self):
        _, errors = validate_create_book({"title": "X", "author": "Y", "status": "want_to_read", "rating": 4})
        self.assertTrue(any("rating" in e.lower() for e in errors))

    def test_rating_on_reading_invalid(self):
        _, errors = validate_create_book({"title": "X", "author": "Y", "status": "reading", "rating": 3})
        self.assertTrue(any("rating" in e.lower() for e in errors))

    def test_rating_out_of_range(self):
        _, errors = validate_create_book({"title": "X", "author": "Y", "status": "finished", "rating": 6})
        self.assertTrue(any("rating" in e.lower() for e in errors))

    def test_missing_title_error(self):
        _, errors = validate_create_book({"author": "Y", "status": "reading"})
        self.assertTrue(any("title" in e.lower() for e in errors))

    def test_missing_author_error(self):
        _, errors = validate_create_book({"title": "X", "status": "reading"})
        self.assertTrue(any("author" in e.lower() for e in errors))

    def test_invalid_status_error(self):
        _, errors = validate_create_book({"title": "X", "author": "Y", "status": "later"})
        self.assertTrue(any("status" in e.lower() for e in errors))

    def test_invalid_isbn_error(self):
        _, errors = validate_create_book({"title": "X", "author": "Y", "status": "reading", "isbn": "123"})
        self.assertTrue(any("isbn" in e.lower() for e in errors))

    def test_zero_page_count_error(self):
        _, errors = validate_create_book({"title": "X", "author": "Y", "status": "reading", "page_count": 0})
        self.assertTrue(any("page_count" in e.lower() for e in errors))

    def test_multiple_errors_returned(self):
        _, errors = validate_create_book({"status": "reading"})
        self.assertGreaterEqual(len(errors), 2)


class TestValidateUpdateBook(unittest.TestCase):

    def test_empty_update_valid(self):
        clean, errors = validate_update_book({})
        self.assertEqual(errors, [])
        self.assertEqual(clean, {})

    def test_partial_update_valid(self):
        clean, errors = validate_update_book({"notes": "Great book"})
        self.assertEqual(errors, [])

    def test_rating_with_valid_status(self):
        clean, errors = validate_update_book({"status": "finished", "rating": 4})
        self.assertEqual(errors, [])

    def test_rating_without_status_rejected(self):
        _, errors = validate_update_book({"rating": 4})
        self.assertTrue(any("rating" in e.lower() for e in errors))


class TestValidateAuth(unittest.TestCase):

    def test_valid_register(self):
        clean, errors = validate_register({"email": "user@example.com", "password": "password123"})
        self.assertEqual(errors, [])
        self.assertEqual(clean["email"], "user@example.com")

    def test_invalid_email(self):
        _, errors = validate_register({"email": "notanemail", "password": "password123"})
        self.assertTrue(any("email" in e.lower() for e in errors))

    def test_short_password(self):
        _, errors = validate_register({"email": "a@b.com", "password": "short"})
        self.assertTrue(any("password" in e.lower() for e in errors))

    def test_email_lowercased(self):
        clean, errors = validate_register({"email": "USER@EXAMPLE.COM", "password": "password123"})
        self.assertEqual(errors, [])
        self.assertEqual(clean["email"], "user@example.com")

    def test_login_missing_password(self):
        _, errors = validate_login({"email": "a@b.com"})
        self.assertTrue(any("password" in e.lower() for e in errors))


if __name__ == "__main__":
    unittest.main()
