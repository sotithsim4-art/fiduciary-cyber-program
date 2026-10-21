import unittest

import fiduciary_cyber


def all_answers(value):
    answers = {}
    for section in fiduciary_cyber.SECTIONS:
        for key, _prompt in section["questions"]:
            answers[key] = value
    return answers


class FiduciaryCyberTests(unittest.TestCase):
    def test_complete_program_has_no_gaps(self):
        result = fiduciary_cyber.assess(all_answers("yes"))
        self.assertEqual(result["percent"], 100)
        self.assertEqual(result["gaps"], [])

    def test_missing_answers_are_gaps(self):
        result = fiduciary_cyber.assess({})
        self.assertEqual(result["percent"], 0)
        self.assertEqual(result["possible"], 15)
        self.assertIn("The firm has a written information security policy", result["gaps"])

    def test_partial_is_half_and_not_a_gap(self):
        answers = all_answers("yes")
        answers["backups"] = "partial"
        result = fiduciary_cyber.assess(answers)
        self.assertEqual(result["earned"], 14.5)
        self.assertEqual(result["gaps"], [])
        self.assertEqual(len(result["partials"]), 1)

    def test_report_includes_the_limit(self):
        report = fiduciary_cyber.format_report(fiduciary_cyber.assess(all_answers("no")))
        self.assertIn("not legal advice", report)
        self.assertIn("Gaps:", report)


if __name__ == "__main__":
    unittest.main()
