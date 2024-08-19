import unittest
from search_script import (
    is_url,
    main_function,
    is_short_url,
) 


class TestShortUrl(unittest.TestCase):

    def test_is_short_url(self):
        print("Testing is_short_url function")
        self.assertTrue(is_short_url("example.com"))
        self.assertTrue(is_short_url("wails.io"))
        self.assertFalse(is_short_url("example"))

    def test_is_url(self):
        print("Testing is_url function")
        self.assertTrue(is_url("https://example.com"))
        self.assertTrue(is_url("http://example.com"))
        self.assertFalse(is_url("http://example"))
        self.assertFalse(is_url("example"))
        self.assertFalse(is_url("example.com"))

    def test_main_function(self):
        print("Testing main_function function")
        self.assertEqual(main_function("example.com"), ("url", "https://example.com"))
        self.assertEqual(main_function("wails.io"), ("url", "https://wails.io"))
        self.assertEqual(
            main_function("https://example.com"), ("url", "https://example.com")
        )
        self.assertEqual(
            main_function("http://example.com"), ("url", "http://example.com")
        )
        self.assertEqual(
            main_function("example"), ("url", "https://www.google.com/search?q=example")
        )
        self.assertEqual(
            main_function("gpt hello"), ("url", "https://chatgpt.com/?q=hello")
        )
        self.assertEqual(main_function("git"), ("url", "https://github.com/"))
        self.assertEqual(main_function("git "), ("git", " "))

        


if __name__ == "__main__":
    unittest.main()
