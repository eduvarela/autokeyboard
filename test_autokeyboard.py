import unittest

from autokeyboard import parse_key_combo, parse_non_negative_int


class ParseKeyComboTests(unittest.TestCase):
    def test_accepts_single_letter(self) -> None:
        self.assertEqual(parse_key_combo("a"), [0x41])

    def test_accepts_combo(self) -> None:
        self.assertEqual(parse_key_combo("ctrl+shift+s"), [0x11, 0x10, 0x53])

    def test_rejects_unknown_key(self) -> None:
        with self.assertRaises(ValueError):
            parse_key_combo("tecla_inexistente")


class ParseNumberTests(unittest.TestCase):
    def test_accepts_positive_number(self) -> None:
        self.assertEqual(parse_non_negative_int("250", "Intervalo"), 250)

    def test_rejects_negative_number(self) -> None:
        with self.assertRaises(ValueError):
            parse_non_negative_int("-1", "Intervalo")


if __name__ == "__main__":
    unittest.main()
