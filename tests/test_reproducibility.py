from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReproducibilityTests(unittest.TestCase):
    def test_regeneration_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "certificate.json"
            subprocess.run(
                [sys.executable, "scripts/bcw_yagzhev_certificate.py", "--write-artifact", str(generated)],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(generated.read_bytes(), (ROOT / "artifacts/bcw-yagzhev-dim79.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
