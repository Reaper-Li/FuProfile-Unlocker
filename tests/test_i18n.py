from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from fuprofile_unlocker.i18n import (
    detect_language,
    normalize_language,
    set_language,
    translate,
)


class InternationalizationTests(unittest.TestCase):
    def tearDown(self) -> None:
        set_language("en")

    def test_normalizes_chinese_locales(self) -> None:
        self.assertEqual(normalize_language("zh_CN"), "zh")
        self.assertEqual(normalize_language("Chinese (Simplified)_China"), "zh")

    def test_non_chinese_locales_use_english(self) -> None:
        self.assertEqual(normalize_language("en_US"), "en")
        self.assertEqual(normalize_language("fr_FR"), "en")
        self.assertEqual(normalize_language(None), "en")

    def test_environment_override_controls_detection(self) -> None:
        with patch.dict(os.environ, {"FUPROFILE_LANGUAGE": "zh-CN"}):
            self.assertEqual(detect_language(), "zh")
        with patch.dict(os.environ, {"FUPROFILE_LANGUAGE": "en"}):
            self.assertEqual(detect_language(), "en")

    def test_exact_translation(self) -> None:
        self.assertEqual(translate("安装配置", "en"), "Create Profiles")
        self.assertEqual(translate("安装配置", "zh"), "安装配置")

    def test_dynamic_translation(self) -> None:
        self.assertEqual(
            translate("正在生成 3/8：Classic Chrome", "en"),
            "Generating 3/8: Classic Chrome",
        )
        self.assertEqual(
            translate("已安装 12 台相机  ·  已选择 2 项", "en"),
            "12 camera(s) installed  ·  2 selected",
        )

    def test_unknown_text_is_preserved(self) -> None:
        self.assertEqual(translate("Canon EOS R5", "en"), "Canon EOS R5")


if __name__ == "__main__":
    unittest.main()
