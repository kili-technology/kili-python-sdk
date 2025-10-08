"""Unit tests for payload normalizer."""

from tests.equivalence.normalizer import DiffGenerator, PayloadNormalizer


class TestPayloadNormalizer:
    """Test PayloadNormalizer functionality."""

    def test_normalize_dict_basic(self):
        """Test basic dictionary normalization."""
        data = {"id": "123", "name": "test", "__typename": "Asset"}
        normalized = PayloadNormalizer.normalize(data)

        # __typename should be removed
        assert "__typename" not in normalized
        assert normalized["id"] == "123"
        assert normalized["name"] == "test"

    def test_normalize_nested_dict(self):
        """Test nested dictionary normalization."""
        data = {
            "id": "123",
            "user": {"id": "456", "email": "test@example.com", "__typename": "User"},
        }
        normalized = PayloadNormalizer.normalize(data)

        assert "__typename" not in normalized["user"]
        assert normalized["user"]["id"] == "456"

    def test_normalize_list(self):
        """Test list normalization and sorting."""
        data = [
            {"id": "2", "name": "b"},
            {"id": "1", "name": "a"},
            {"id": "3", "name": "c"},
        ]
        normalized = PayloadNormalizer.normalize(data, sort_lists=True)

        # Should be sorted by id
        assert normalized[0]["id"] == "1"
        assert normalized[1]["id"] == "2"
        assert normalized[2]["id"] == "3"

    def test_normalize_strip_none(self):
        """Test stripping None values."""
        data = {"id": "123", "name": None, "value": "test"}
        normalized = PayloadNormalizer.normalize(data, strip_none=True)

        assert "name" not in normalized
        assert normalized["id"] == "123"
        assert normalized["value"] == "test"

    def test_normalize_for_comparison(self):
        """Test normalize_for_comparison with legacy and v2 responses."""
        legacy = {
            "id": "123",
            "labels": [{"id": "2"}, {"id": "1"}],
            "__typename": "Asset",
        }
        v2 = {
            "id": "123",
            "labels": [{"id": "1"}, {"id": "2"}],
        }

        norm_legacy, norm_v2 = PayloadNormalizer.normalize_for_comparison(legacy, v2)

        # Should be equal after normalization
        assert norm_legacy == norm_v2


class TestDiffGenerator:
    """Test DiffGenerator functionality."""

    def test_generate_diff_equal(self):
        """Test diff generation for equal objects."""
        legacy = {"id": "123", "name": "test"}
        v2 = {"id": "123", "name": "test"}

        diffs = DiffGenerator.generate_diff(legacy, v2)

        assert len(diffs) == 0

    def test_generate_diff_value_mismatch(self):
        """Test diff generation for value mismatch."""
        legacy = {"id": "123", "name": "test"}
        v2 = {"id": "123", "name": "different"}

        diffs = DiffGenerator.generate_diff(legacy, v2)

        assert len(diffs) == 1
        assert "name" in diffs[0]
        assert "Value mismatch" in diffs[0]

    def test_generate_diff_missing_keys(self):
        """Test diff generation for missing keys."""
        legacy = {"id": "123", "name": "test", "extra": "value"}
        v2 = {"id": "123", "name": "test"}

        diffs = DiffGenerator.generate_diff(legacy, v2)

        assert len(diffs) == 1
        assert "only in legacy" in diffs[0].lower()

    def test_generate_diff_type_mismatch(self):
        """Test diff generation for type mismatch."""
        legacy = {"id": "123"}
        v2 = ["123"]

        diffs = DiffGenerator.generate_diff(legacy, v2)

        assert len(diffs) == 1
        assert "Type mismatch" in diffs[0]

    def test_generate_diff_list_length(self):
        """Test diff generation for list length mismatch."""
        legacy = [1, 2, 3]
        v2 = [1, 2]

        diffs = DiffGenerator.generate_diff(legacy, v2)

        assert len(diffs) == 1
        assert "Length mismatch" in diffs[0]

    def test_generate_diff_nested_objects(self):
        """Test diff generation for nested objects."""
        legacy = {
            "id": "123",
            "user": {"id": "456", "name": "Alice"},
        }
        v2 = {
            "id": "123",
            "user": {"id": "456", "name": "Bob"},
        }

        diffs = DiffGenerator.generate_diff(legacy, v2)

        assert len(diffs) == 1
        assert "user.name" in diffs[0]
        assert "Alice" in diffs[0]
        assert "Bob" in diffs[0]
