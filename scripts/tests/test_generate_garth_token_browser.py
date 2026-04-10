import unittest

from scripts.garmin.generate_garth_token_browser import requires_manual_takeover


class FakeLocator:
    def __init__(self, visible=True, text=""):
        self._visible = visible
        self._text = text
        self.first = self

    def count(self):
        return 1

    def is_visible(self):
        return self._visible

    def inner_text(self):
        return self._text


class MissingLocator:
    first = None

    def count(self):
        return 0


class FakePage:
    def __init__(self, url="", content="", body_text="", locators=None):
        self.url = url
        self._content = content
        self._body_text = body_text
        self._locators = locators or {}

    def content(self):
        return self._content

    def locator(self, selector):
        if selector == "body":
            return FakeLocator(text=self._body_text)
        return self._locators.get(selector, MissingLocator())


class RequiresManualTakeoverTest(unittest.TestCase):
    def test_ignores_hidden_verify_text_before_login_form_renders(self):
        page = FakePage(
            url="https://sso.garmin.com/sso/embed",
            content="<html><script>const verifyToken = true;</script></html>",
            body_text="Sign in to Garmin Connect",
        )

        self.assertFalse(requires_manual_takeover(page))

    def test_detects_visible_verification_prompt(self):
        page = FakePage(
            url="https://sso.garmin.com/sso/challenge",
            body_text="Enter the verification code we sent to your email.",
        )

        self.assertTrue(requires_manual_takeover(page))


if __name__ == "__main__":
    unittest.main()
