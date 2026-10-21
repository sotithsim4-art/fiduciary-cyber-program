import json
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import app
import fiduciary_cyber

ROOT = Path(__file__).resolve().parent


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.make_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def url(self, path):
        return f"http://127.0.0.1:{self.port}{path}"

    def post(self, path, payload):
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.url(path),
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def test_page_opens_with_the_disclaimer(self):
        with urllib.request.urlopen(self.url("/")) as response:
            html = response.read().decode("utf-8")
            status = response.status
        self.assertEqual(status, 200)
        self.assertIn("Fiduciary Cyber Program", html)
        self.assertIn(fiduciary_cyber.DISCLAIMER, html)

    def test_questions_match_the_checklist(self):
        with urllib.request.urlopen(self.url("/api/questions")) as response:
            payload = json.load(response)
        keys = [item["key"] for section in payload["sections"] for item in section["questions"]]
        expected = [key for section in fiduciary_cyber.SECTIONS for key, _prompt in section["questions"]]
        self.assertEqual(keys, expected)
        self.assertEqual(payload["disclaimer"], fiduciary_cyber.DISCLAIMER)

    def test_assess_uses_the_same_score(self):
        answers = {
            key: "yes"
            for section in fiduciary_cyber.SECTIONS
            for key, _prompt in section["questions"]
        }
        answers["backups"] = "partial"
        answers["not-a-question"] = "yes"
        body = self.post("/api/assess", {"answers": answers})
        self.assertEqual(body["result"]["earned"], 14.5)
        self.assertEqual(body["result"]["percent"], 97)
        self.assertEqual(body["result"]["gaps"], [])
        self.assertIn("not legal advice", body["report"])

    def test_bad_json_is_rejected(self):
        request = urllib.request.Request(
            self.url("/api/assess"),
            data=b"nope",
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(request)
        self.assertEqual(raised.exception.code, 400)
        raised.exception.close()

    def test_save_writes_the_report_and_leaves_no_other_file(self):
        target = ROOT / "cyber-program-report.txt"
        existed = target.exists()
        previous = target.read_text(encoding="utf-8") if existed else None
        try:
            body = self.post("/api/save", {"answers": {"policy": "no"}})
            self.assertEqual(body["saved"], "cyber-program-report.txt")
            saved = target.read_text(encoding="utf-8")
            self.assertIn("The firm has a written information security policy", saved)
            self.assertIn("not legal advice", saved)
            self.assertTrue(saved.endswith("\n"))
        finally:
            if existed:
                target.write_text(previous, encoding="utf-8")
            elif target.exists():
                target.unlink()
