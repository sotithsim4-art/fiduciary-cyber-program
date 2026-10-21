"""Local window for the fiduciary cyber program checklist."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import fiduciary_cyber

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765
REPORT_NAME = "cyber-program-report.txt"
MAX_BODY = 100_000

FILES = {
    "/": ("app.html", "text/html; charset=utf-8"),
    "/index.html": ("app.html", "text/html; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
}

QUESTION_KEYS = {
    key
    for section in fiduciary_cyber.SECTIONS
    for key, _prompt in section["questions"]
}


def questions_payload():
    return {
        "title": "Fiduciary Cyber Program",
        "disclaimer": fiduciary_cyber.DISCLAIMER,
        "sections": [
            {
                "title": section["title"],
                "questions": [
                    {"key": key, "prompt": prompt}
                    for key, prompt in section["questions"]
                ],
            }
            for section in fiduciary_cyber.SECTIONS
        ],
    }


def clean_answers(payload):
    if not isinstance(payload, dict):
        return {}
    raw = payload.get("answers")
    if not isinstance(raw, dict):
        return {}
    answers = {}
    for key, value in raw.items():
        if key in QUESTION_KEYS and isinstance(value, str):
            answers[key] = value
    return answers


def score(answers):
    result = fiduciary_cyber.assess(answers)
    report = fiduciary_cyber.format_report(result)
    return result, report


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _send(self, code, body, content_type):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            return None
        if length < 0 or length > MAX_BODY:
            return None
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            return None
        if not isinstance(payload, dict):
            return None
        return payload

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/questions":
            self._send(200, json.dumps(questions_payload()), "application/json")
            return
        item = FILES.get(path)
        if item is None:
            self._send(404, "Not found", "text/plain; charset=utf-8")
            return
        name, content_type = item
        self._send(200, (ROOT / name).read_bytes(), content_type)

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/api/assess", "/api/save"):
            self._send(404, "Not found", "text/plain; charset=utf-8")
            return
        payload = self._read_json()
        if payload is None:
            self._send(400, json.dumps({"error": "Send the answers as JSON."}), "application/json")
            return
        result, report = score(clean_answers(payload))
        if path == "/api/assess":
            self._send(200, json.dumps({"result": result, "report": report}), "application/json")
            return
        target = ROOT / REPORT_NAME
        try:
            target.write_text(report + "\n", encoding="utf-8")
        except OSError:
            self._send(500, json.dumps({"error": "Could not save the report."}), "application/json")
            return
        self._send(
            200,
            json.dumps({"saved": REPORT_NAME, "result": result, "report": report}),
            "application/json",
        )


def make_server(host=HOST, port=PORT):
    return ThreadingHTTPServer((host, port), Handler)


def main():
    server = make_server()
    print("Fiduciary Cyber Program is open at http://%s:%s" % (HOST, PORT))
    print("Close this window to quit the app.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nClosed.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
