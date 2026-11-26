"""Run with: python3 -m unittest discover -s registry -p 'test_*.py'"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from archive_utils import (content_fingerprint, finest_result, is_scientific_file,
                           matching_archive, summary_rows)


def digest(s: bytes):
    return hashlib.sha256(s).hexdigest()


def file_hashes(folder):
    return {p.relative_to(folder).as_posix(): digest(p.read_bytes())
            for p in folder.rglob("*") if p.is_file()}


class ArchiveUtilsTests(unittest.TestCase):
    def test_scientific_paths_and_fingerprints(self):
        main = {"inputs/run.py": digest(b"a"), "results/M01/C02_LBA.med": digest(b"med")}
        with_caches = {**main, "results/M01/__pycache__/run.pyc": digest(b"noise"),
                       "results/M01/.vs-code-aster/mesh_cache/X.obj": digest(b"mesh")}
        self.assertEqual(content_fingerprint(main), content_fingerprint(with_caches))
        self.assertTrue(is_scientific_file("results/M01/C02_LBA.med"))
        self.assertFalse(is_scientific_file("results/M01/.vs-code-aster/mesh_cache/X.obj"))
        self.assertNotEqual(content_fingerprint(main), content_fingerprint({**main, "inputs/run.py": digest(b"b")}))

    def test_legacy_manifest_and_recovery_integrity(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            run = parent / "C02-20261126T123456Z-abcdef"
            snap = run / "snapshot"
            (snap / "inputs").mkdir(parents=True)
            (snap / "results").mkdir()
            (snap / "inputs" / "run.py").write_bytes(b"original")
            (snap / "results" / "case.csv").write_bytes(b"results")
            actual = file_hashes(snap)
            legacy = {**actual, "results/M01/__pycache__/ignored.pyc": digest(b"cache")}
            (run / "manifest.json").write_text(json.dumps({"run_id": run.name, "sha256": legacy}))
            self.assertEqual(matching_archive(parent, actual, file_hashes), run.name)
            (snap / "results" / "case.csv").write_bytes(b"tampered")
            with self.assertRaisesRegex(RuntimeError, "integrity"):
                matching_archive(parent, actual, file_hashes)

    def test_summary_and_finest_mesh(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp)
            run = archive / "C02" / "C02-20260101T120000Z-abc123"
            run.mkdir(parents=True)
            results = [
                {"mesh": "M01", "nominal_size_m": 0.15, "elements": 63,
                 "critical_value": 420, "unit": "MPa", "reference_value": 417,
                 "difference_pct": 0.72},
                {"mesh": "M05", "nominal_size_m": 0.0125, "elements": 10455,
                 "critical_value": 403, "unit": "MPa", "reference_value": 417,
                 "difference_pct": -3.36},
            ]
            self.assertEqual(finest_result(results)["mesh"], "M05")
            (run / "manifest.json").write_text(json.dumps({"run_id": run.name, "case_id": "C02",
                "captured_utc": "2026-11-26T15:59:26+00:00", "note": "First run",
                "case_status_at_capture": "Prepared", "results": results}))
            s = summary_rows(archive, {"C02": {}})
            self.assertEqual(len(s), 1)
            self.assertEqual(s[0]["mesh_count"], 2)
            self.assertEqual(s[0]["finest_mesh"], "M05")
            self.assertEqual(s[0]["note"], "First run")


if __name__ == "__main__":
    unittest.main()
