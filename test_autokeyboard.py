import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import autokeyboard
from autokeyboard import (
    DEFAULT_LANGUAGE,
    DEFAULT_TRANSLATIONS,
    detect_system_language,
    load_app_strings,
    parse_key_combo,
    parse_non_negative_int,
    sleep_interruptible,
    tr,
)


class ParseKeyComboTests(unittest.TestCase):
    def setUp(self) -> None:
        load_app_strings(DEFAULT_LANGUAGE)

    def test_accepts_single_letter(self) -> None:
        self.assertEqual(parse_key_combo("a"), [0x41])

    def test_accepts_combo(self) -> None:
        self.assertEqual(parse_key_combo("ctrl+shift+s"), [0x11, 0x10, 0x53])

    def test_accepts_aliases_and_whitespace(self) -> None:
        self.assertEqual(parse_key_combo(" Ctrl + Esc "), [0x11, 0x1B])

    def test_rejects_unknown_key(self) -> None:
        with self.assertRaises(ValueError):
            parse_key_combo("tecla_inexistente")

    def test_rejects_empty_combo(self) -> None:
        with self.assertRaises(ValueError):
            parse_key_combo("   ")


class ParseNumberTests(unittest.TestCase):
    def setUp(self) -> None:
        load_app_strings(DEFAULT_LANGUAGE)

    def test_accepts_positive_number(self) -> None:
        self.assertEqual(parse_non_negative_int("250", "Intervalo"), 250)

    def test_accepts_zero(self) -> None:
        self.assertEqual(parse_non_negative_int("0", "Intervalo"), 0)

    def test_rejects_negative_number(self) -> None:
        with self.assertRaises(ValueError):
            parse_non_negative_int("-1", "Intervalo")

    def test_rejects_invalid_number(self) -> None:
        with self.assertRaises(ValueError):
            parse_non_negative_int("abc", "Intervalo")


class AppStringsTests(unittest.TestCase):
    def tearDown(self) -> None:
        load_app_strings(DEFAULT_LANGUAGE)

    def test_loads_english_strings(self) -> None:
        load_app_strings("en")
        self.assertEqual(tr("labels.button_start"), "START")
        self.assertEqual(tr("labels.metric_cycle"), "CYCLE TIME")

    def test_unknown_language_falls_back_to_default(self) -> None:
        load_app_strings("es")
        self.assertEqual(autokeyboard.CURRENT_LANGUAGE, DEFAULT_LANGUAGE)
        self.assertEqual(
            tr("labels.button_start"),
            DEFAULT_TRANSLATIONS[DEFAULT_LANGUAGE]["labels"]["button_start"],
        )

    def test_custom_strings_file_overrides_and_formats(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            strings_path = Path(temp_dir) / "strings.json"
            strings_path.write_text(
                json.dumps(
                    {
                        "en": {
                            "labels": {
                                "button_start": "LAUNCH",
                            },
                            "status": {
                                "language_changed": "Language switched to {language_name}.",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(autokeyboard, "STRINGS_PATH", strings_path):
                load_app_strings("en")

            self.assertEqual(tr("labels.button_start"), "LAUNCH")
            self.assertEqual(
                tr("status.language_changed", language_name="English"),
                "Language switched to English.",
            )

    def test_missing_translation_path_returns_key(self) -> None:
        load_app_strings("en")
        self.assertEqual(tr("labels.path.that.does.not.exist"), "labels.path.that.does.not.exist")


class SleepInterruptibleTests(unittest.TestCase):
    def test_returns_false_when_event_is_already_set(self) -> None:
        stop_event = threading.Event()
        stop_event.set()
        self.assertFalse(sleep_interruptible(0.2, stop_event))

    def test_returns_true_when_sleep_completes(self) -> None:
        stop_event = threading.Event()
        self.assertTrue(sleep_interruptible(0.0, stop_event))


class DetectSystemLanguageTests(unittest.TestCase):
    def test_returns_portuguese_for_portuguese_windows_locale(self) -> None:
        mocked_windll = type(
            "MockWindll",
            (),
            {"kernel32": type("Kernel32", (), {"GetUserDefaultUILanguage": staticmethod(lambda: 1046)})()},
        )()
        with patch.object(autokeyboard.ctypes, "windll", mocked_windll, create=True):
            with patch.object(autokeyboard.locale, "getlocale", return_value=("pt_BR", "cp1252")):
                with patch.object(autokeyboard.locale, "getdefaultlocale", return_value=("pt_BR", "cp1252"), create=True):
                    self.assertEqual(detect_system_language(), "pt-BR")

    def test_returns_english_when_system_is_not_portuguese(self) -> None:
        mocked_windll = type(
            "MockWindll",
            (),
            {"kernel32": type("Kernel32", (), {"GetUserDefaultUILanguage": staticmethod(lambda: 1033)})()},
        )()
        with patch.object(autokeyboard.ctypes, "windll", mocked_windll, create=True):
            with patch.object(autokeyboard.locale, "getlocale", return_value=("en_US", "cp1252")):
                with patch.object(autokeyboard.locale, "getdefaultlocale", return_value=("en_US", "cp1252"), create=True):
                    self.assertEqual(detect_system_language(), "en")


if __name__ == "__main__":
    unittest.main()
