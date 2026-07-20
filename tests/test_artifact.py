import json
from pathlib import Path
import unittest
from scripts.verify_bcw_yagzhev_artifact import verify_artifact
ROOT = Path(__file__).resolve().parents[1]
class ArtifactTests(unittest.TestCase):
    def test_independent_verifier(self):
        verify_artifact(ROOT / "artifacts/bcw-yagzhev-dim79.json")
    def test_v2_marker_and_dimensions(self):
        data = json.loads((ROOT / "artifacts/bcw-yagzhev-dim79.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "bcw-yagzhev-certificate-v2")
        self.assertEqual(data["dimensions"], {"source": 3, "intermediate": 39, "final": 79})
if __name__ == "__main__": unittest.main()
