import unittest

from project import aggregate, normalize_answer, run, SPEC


class ConsensusTests(unittest.TestCase):
    def test_fraction_and_decimal_agree(self):
        self.assertEqual(normalize_answer("1500/2"), normalize_answer("750.0"))

    def test_invalid_and_division_zero(self):
        self.assertIsNone(normalize_answer("5 件"))
        self.assertIsNone(normalize_answer("5/0"))

    def test_tie_abstains(self):
        result = aggregate(["FINAL: 1", "FINAL: 2", "FINAL: 1", "FINAL: 2"])
        self.assertFalse(result["accepted"])

    def test_invalid_responses_lower_share(self):
        result = aggregate(["FINAL: 1", "FINAL: 1", "FINAL: 1", "invalid", "invalid", "invalid"])
        self.assertFalse(result["accepted"])

    def test_demo_rejects_unrelated_question(self):
        class LocalClient:
            enabled = False
        with self.assertRaises(ValueError):
            run({"text": "另一个问题"}, LocalClient())


if __name__ == "__main__":
    unittest.main()
