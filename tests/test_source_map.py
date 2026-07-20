import json
from pathlib import Path
import unittest
from scripts.verify_bcw_yagzhev_artifact import determinant_3, jacobian, parse_point, parse_polynomial, Poly
ROOT = Path(__file__).resolve().parents[1]
class SourceMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "artifacts/bcw-yagzhev-dim79.json").read_text(encoding="utf-8"))
    def test_source_determinant_and_collision(self):
        source = self.data["source_map"]
        components = [parse_polynomial(record, 3, "source") for record in source["components"]]
        self.assertEqual(determinant_3(jacobian(components)), Poly.constant(3, -2))
        target = parse_point(source["common_value"], 3, "target")
        points = [parse_point(point, 3, "point") for point in source["collision_points"]]
        self.assertEqual(len(set(map(tuple, points))), 3)
        for point in points: self.assertEqual([component.evaluate(point) for component in components], target)
if __name__ == "__main__": unittest.main()
