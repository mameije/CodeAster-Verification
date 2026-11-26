"""Python stdlib tests: run `python3 -m unittest discover -s registry`."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from theory.brush_1975 import critical_value, discrete_minimum


PARAMS = {"D": 1.016, "H": 0.508, "t": 0.00508,
          "E": 68947.57293168, "nu": 0.3}
MODELS = json.loads((Path(__file__).parent / "theory/models.json").read_text())["models"]


class TheoryTests(unittest.TestCase):
    def test_c01_equation_544(self):
        minimum = discrete_minimum("C01", PARAMS, MODELS["C01"]["search_limits"])
        self.assertEqual((minimum["m"], minimum["n"]), (1, 8))
        self.assertAlmostEqual(minimum["value"], 730.64142655247, places=6)
        self.assertEqual(minimum["unit"], "kPa")

    def test_c02_equation_550(self):
        minimum = discrete_minimum("C02", PARAMS, MODELS["C02"]["search_limits"])
        self.assertEqual((minimum["m"], minimum["n"]), (3, 9))
        self.assertAlmostEqual(minimum["value"], 417.35431552768, places=6)
        self.assertEqual(minimum["unit"], "MPa")

    def test_material_scaling_and_bounds(self):
        other = {**PARAMS, "E": PARAMS["E"] * 2}
        for case in ("C01", "C02"):
            first = discrete_minimum(case, PARAMS, MODELS[case]["search_limits"])
            second = discrete_minimum(case, other, MODELS[case]["search_limits"])
            self.assertAlmostEqual(second["value"], 2 * first["value"], places=7)
        with self.assertRaisesRegex(ValueError, "upper search boundary"):
            discrete_minimum("C01", PARAMS,
                             {"m_min": 1, "m_max": 1, "n_min": 1, "n_max": 2})
        with self.assertRaises(ValueError):
            critical_value("C01", PARAMS, 1, 0)

    def test_archived_c02_v1_end_to_end(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            reg = root / "registry"; reg.mkdir()
            theory = reg / "theory"; theory.mkdir()
            for source, dest in (
                (Path(__file__).parent / "compare.py", reg / "compare.py"),
                (Path(__file__).parent / "theory/brush_1975.py", theory / "brush_1975.py"),
                (Path(__file__).parent / "theory/models.json", theory / "models.json"),
            ):
                dest.write_bytes(source.read_bytes())
            (reg / "cases.json").write_text(json.dumps({"schema_version": 1, "cases": [{
                "id": "C02", "primary_reference": {"unit": "MPa"},
                "result_column": "critical_stress_MPa", "output_to_reference_factor": 1,
            }]}))
            run_id = "C02-20260101T000000Z-abcdef"
            folder = root / "archive/C02" / run_id
            snap = folder / "snapshot"
            (snap / "inputs").mkdir(parents=True)
            mesh = snap / "results/M01"; mesh.mkdir(parents=True)
            (snap / "inputs/parameters.json").write_text(json.dumps(PARAMS))
            (mesh / "case.json").write_text(json.dumps({**PARAMS, "nominal_size_m": .15}))
            with (mesh / "C02_LBA_results.csv").open("w", newline="") as f:
                writer = csv.writer(f); writer.writerow(["load_factor", "critical_stress_MPa"])
                writer.writerow([419.9126627196923, 419.9126627196923])
            hashes = {}
            for path in snap.rglob("*"):
                if path.is_file():
                    hashes[path.relative_to(snap).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
            (folder / "manifest.json").write_text(json.dumps({
                "schema_version": 1, "run_id": run_id, "case_id": "C02",
                "captured_utc": "2026-01-01T00:00:00+00:00", "note": "synthetic test",
                "results": [{"mesh": "M01", "nominal_size_m": .15, "elements": 63,
                             "nodes": 294, "critical_value": 419.9126627196923, "unit": "MPa"}],
                "sha256": hashes,
            }))
            def command():
                return subprocess.run([sys.executable, str(reg / "compare.py"), "--run", run_id],
                                      capture_output=True, text=True)
            result = command()
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            with (reg / "comparisons.csv").open(newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["m"], "3")
            self.assertEqual(rows[0]["n"], "9")
            self.assertEqual(rows[0]["unit"], "MPa")
            self.assertTrue((root / "archive/comparisons" / run_id / "report.md").exists())
            self.assertEqual((mesh / "C02_LBA_results.csv").read_bytes(),
                             b"load_factor,critical_stress_MPa\r\n419.9126627196923,419.9126627196923\r\n")
            (mesh / "C02_LBA_results.csv").write_text("tampered")
            result = command()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("altered archived file", result.stderr)


if __name__ == "__main__":
    unittest.main()
