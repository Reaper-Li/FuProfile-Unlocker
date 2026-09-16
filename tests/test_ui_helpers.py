from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fuprofile_unlocker.app import (
    dropped_paths,
    interactive_cursor,
    scroll_units,
    unpack_touchpad_delta,
)


class ScrollTests(unittest.TestCase):
    def test_dropped_paths_preserve_spaces_and_multiple_files(self) -> None:
        parsed = dropped_paths(
            "ignored Tcl list",
            lambda _value: (r"C:\Photos\Canon sample.CR3", r"D:\RAW\Nikon.NEF"),
        )
        self.assertEqual(
            parsed,
            (Path(r"C:\Photos\Canon sample.CR3"), Path(r"D:\RAW\Nikon.NEF")),
        )

    def test_cursor_name_is_valid_for_each_desktop_platform(self) -> None:
        with patch("fuprofile_unlocker.app.platform.system", return_value="Windows"):
            self.assertEqual(interactive_cursor(), "hand2")
        with patch("fuprofile_unlocker.app.platform.system", return_value="Darwin"):
            self.assertEqual(interactive_cursor(), "pointinghand")

    def test_small_trackpad_delta_never_rounds_to_zero(self) -> None:
        self.assertEqual(scroll_units(1), -1)
        self.assertEqual(scroll_units(-1), 1)

    def test_mouse_wheel_delta_has_direction_and_magnitude(self) -> None:
        self.assertEqual(scroll_units(120), -2)
        self.assertEqual(scroll_units(-120), 2)
        self.assertEqual(scroll_units(0), 0)

    def test_touchpad_delta_unpacks_both_signed_axes(self) -> None:
        self.assertEqual(unpack_touchpad_delta((2 << 16) | 0xFFF9), (2, -7))
        signed_packed = ((0xFFFD << 16) | 5) - (1 << 32)
        self.assertEqual(unpack_touchpad_delta(signed_packed), (-3, 5))


if __name__ == "__main__":
    unittest.main()
