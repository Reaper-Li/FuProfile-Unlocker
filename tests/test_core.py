from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fuprofile_unlocker.core import (
    RawIdentity,
    camera_install_directory,
    compatible_model,
    is_fujifilm,
    normalized,
    _profile_model_from_filename,
    profile_model_aliases,
    safe_name,
)


class IdentityTests(unittest.TestCase):
    def test_normalized_removes_vendor_punctuation(self) -> None:
        self.assertEqual(normalized("NIKON Z 6_2"), "nikonz62")

    def test_adobe_prefix_is_compatible(self) -> None:
        self.assertTrue(compatible_model("ILCE-7M4", "Sony ILCE-7M4"))
        self.assertTrue(compatible_model("GFX100 II", "Fujifilm GFX 100 II"))

    def test_different_models_are_not_compatible(self) -> None:
        self.assertFalse(compatible_model("ILCE-7M3", "Sony ILCE-7M4"))

    def test_model_match_does_not_accept_an_unrelated_suffix(self) -> None:
        self.assertFalse(compatible_model("Olympus E-1", "Fujifilm X-E1"))
        self.assertFalse(compatible_model("Olympus TG-5", "Canon PowerShot G5"))

    def test_explicit_regional_alias_is_compatible(self) -> None:
        self.assertEqual(
            profile_model_aliases("Canon EOS R5m2"),
            ("Canon EOS R5m2", "Canon EOS R5 Mark II"),
        )
        self.assertTrue(compatible_model("Canon EOS R5m2", "Canon EOS R5 Mark II"))
        self.assertTrue(compatible_model("DC-TZ95", "Panasonic DC-ZS80"))
        self.assertTrue(compatible_model("DC-FZ45", "Panasonic DC-FZ80"))
        self.assertFalse(compatible_model("DC-FZ45", "Panasonic DMC-FZ40"))

    def test_unrelated_model_is_not_resolved_by_aliases(self) -> None:
        self.assertFalse(compatible_model("Canon EOS R5", "Canon EOS R5 Mark II"))

    def test_adobe_standard_filename_variants_are_parsed(self) -> None:
        self.assertEqual(
            _profile_model_from_filename(Path("Leica D-Lux 7 Adobe_Standard.dcp")),
            "Leica D-Lux 7",
        )
        self.assertEqual(
            _profile_model_from_filename(Path("Canon EOS R Adobe Standard v2.dcp")),
            "Canon EOS R",
        )
        self.assertEqual(
            _profile_model_from_filename(Path("Canon EOS R Adobe_Standard_v2.dcp")),
            "Canon EOS R",
        )

    def test_fujifilm_raw_is_reserved_for_native_profiles(self) -> None:
        self.assertTrue(is_fujifilm("FUJIFILM"))
        self.assertFalse(is_fujifilm("Canon"))

    def test_profile_filename_is_safe(self) -> None:
        self.assertEqual(safe_name("Camera FUJIFILM PROVIA / Standard"), "Camera FUJIFILM PROVIA _ Standard")

    def test_each_camera_gets_an_isolated_install_directory(self) -> None:
        root = Path("profiles")
        canon = camera_install_directory(root, RawIdentity("Canon", "Canon EOS R", "CR3"))
        sony = camera_install_directory(root, RawIdentity("SONY", "ILCE-7M4", "ARW"))
        self.assertEqual(canon, Path("profiles/Canon EOS R"))
        self.assertEqual(sony, Path("profiles/ILCE-7M4"))
        self.assertNotEqual(canon, sony)


if __name__ == "__main__":
    unittest.main()
