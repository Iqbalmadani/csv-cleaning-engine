import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from core.canonical_model import CanonicalTable
from core.schema_engine import load_schema
from core.transformer import transform


class SchemaLoadingTests(unittest.TestCase):
    def test_missing_explicit_schema_raises_file_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "missing.json"

            with self.assertRaises(FileNotFoundError):
                load_schema(str(missing_path))

    def test_schema_must_be_a_json_object(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            schema_path = Path(temp_dir) / "schema.json"
            schema_path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "JSON object"):
                load_schema(str(schema_path))


class CaseInsensitiveTransformationTests(unittest.TestCase):
    def test_schema_column_case_insensitive_match_is_transformed(self):
        table = CanonicalTable(
            columns=["Email"],
            rows=[{"Email": "USER@EXAMPLE.COM"}],
        )

        result = transform(table, {"email": {"type": "email"}})

        self.assertEqual(result.rows[0]["Email"], "user@example.com")

    def test_empty_schema_works_and_preserves_missing_values(self):
        table = CanonicalTable(
            columns=["Name"],
            rows=[{"Name": "  Sample User  "}, {"Name": None}],
        )

        result = transform(table, {})

        self.assertEqual(result.rows[0]["Name"], "Sample User")
        self.assertTrue(pd.isna(result.rows[1]["Name"]))

    def test_text_and_email_transforms_preserve_missing_values(self):
        table = CanonicalTable(
            columns=["Name", "Email"],
            rows=[
                {"Name": None, "Email": None},
                {"Name": "  Sample User  ", "Email": "USER@EXAMPLE.COM"},
            ],
        )

        result = transform(
            table,
            {"Name": {"type": "text"}, "Email": {"type": "email"}},
        )

        self.assertTrue(pd.isna(result.rows[0]["Name"]))
        self.assertTrue(pd.isna(result.rows[0]["Email"]))
        self.assertEqual(result.rows[1]["Name"], "Sample User")
        self.assertEqual(result.rows[1]["Email"], "user@example.com")


if __name__ == "__main__":
    unittest.main()
