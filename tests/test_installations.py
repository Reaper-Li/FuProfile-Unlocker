from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fuprofile_unlocker.installations import scan_installations, uninstall_many


class InstallationTests(unittest.TestCase):
    def test_scan_and_uninstall_managed_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            current = root / "FuProfile Unlocker"
            canon = current / "Canon EOS R"
            canon.mkdir(parents=True)
            for index in range(8):
                (canon / f"Camera FUJIFILM Style {index}.dcp").write_bytes(b"dcp")
            (canon / "manifest.json").write_text(
                json.dumps({"identity": {"make": "Canon", "model": "Canon EOS R"}}),
                encoding="utf-8",
            )

            records = scan_installations(current)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].model, "Canon EOS R")
            self.assertEqual(records[0].profile_count, 8)

            removed = uninstall_many(records, current)
            self.assertEqual(removed, 8)
            self.assertFalse(canon.exists())


if __name__ == "__main__":
    unittest.main()
