import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def test_json_schema(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((ROOT / "artifacts/bcw-yagzhev-certificate.schema.json").read_text(encoding="utf-8"))
        artifact = json.loads((ROOT / "artifacts/bcw-yagzhev-dim79.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(artifact)


if __name__ == "__main__":
    unittest.main()
