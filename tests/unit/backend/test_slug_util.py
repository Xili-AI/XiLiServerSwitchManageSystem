"""Unit tests for slug helpers."""
from utils.base_utils.slug_util import is_valid_slug, slugify


class TestSlugify:
    """Slug generation behaviour."""

    def test_normal_text(self):
        assert slugify("Hello World!") == "hello-world"

    def test_chinese_text_has_no_ascii_slug(self):
        assert slugify("服务管理") == ""

    def test_trims_separators(self):
        assert slugify("-Hello---World-") == "hello-world"


class TestSlugValidation:
    """Slug contract used by public URLs."""

    def test_valid_slug(self):
        assert is_valid_slug("portainer") is True

    def test_single_character(self):
        assert is_valid_slug("a") is True

    def test_rejects_uppercase(self):
        assert is_valid_slug("Portainer") is False

    def test_rejects_leading_hyphen(self):
        assert is_valid_slug("-portainer") is False

    def test_rejects_empty(self):
        assert is_valid_slug("") is False
