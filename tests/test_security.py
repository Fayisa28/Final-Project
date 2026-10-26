"""Security tests for the Job Hunter Africa server (no API key or internet needed).
Run:  python3 -m unittest discover -s tests -v"""
import importlib.util, json, os, sys, tempfile, threading, time, unittest, urllib.request, urllib.error, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("PORT", "8199")
os.environ["OWNER_EMAIL"] = "owner@test.example"; os.environ["OWNER_PASSWORD"] = "Owner12345"
spec = importlib.util.spec_from_file_location("srv", ROOT / "jobhunter_server.py")
srv = importlib.util.module_from_spec(spec); spec.loader.exec_module(srv)

PORT = 8199
server = srv.ThreadingHTTPServer(("127.0.0.1", PORT), srv.Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
time.sleep(0.3)

def call(path, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=data, method="POST" if body is not None else "GET",
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=10) as r: return r.status, json.loads(r.read() or b"{}"), r.headers
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read() or b"{}"), e.headers
        except Exception: return e.code, {}, e.headers

class Security(unittest.TestCase):
    def test_passwords_are_hashed(self):
        h = srv.hash_pw("Secret123")
        self.assertNotIn("Secret123", h); self.assertTrue(srv.check_pw("Secret123", h)); self.assertFalse(srv.check_pw("wrong", h))

    def test_cannot_sign_up_as_admin(self):
        st, d, _ = call("/api/auth/signup", {"role": "admin", "email": "sneaky@test.example", "password": "Abc12345"})
        self.assertEqual(st, 200)
        self.assertEqual(srv.USERS["sneaky@test.example"]["role"], "seeker")

    def test_weak_password_rejected(self):
        st, d, _ = call("/api/auth/signup", {"email": "weak@test.example", "password": "123"})
        self.assertEqual(st, 400)

    def test_wrong_code_rejected_and_code_expires_after_5_tries(self):
        call("/api/auth/signup", {"email": "codes@test.example", "password": "Abc12345"})
        for _ in range(5): self.assertEqual(call("/api/auth/verify", {"email": "codes@test.example", "code": "000000"})[0], 400)
        self.assertEqual(srv.check_code("codes@test.example", "000000", "signup"), "expired")

    def test_lockout_after_5_failed_logins(self):
        for _ in range(5): call("/api/auth/login", {"email": "owner@test.example", "password": "nope99999", "role": "admin"})
        st, d, _ = call("/api/auth/login", {"email": "owner@test.example", "password": "Owner12345", "role": "admin"})
        self.assertEqual(st, 429); srv.FAILS.clear()

    def test_private_files_never_served(self):
        for p in ["/.env", "/data/users.json", "/logs/fayisa_runs.jsonl", "/jobhunter_server.py"]:
            self.assertEqual(call(p)[0], 404, p)

    def test_cross_site_requests_blocked(self):
        st, d, _ = call("/api/auth/login", {"email": "x@test.example", "password": "x"}, {"Origin": "http://evil.example"})
        self.assertEqual(st, 403)

    def test_session_cookie_is_httponly(self):
        email = f"cookie-{uuid.uuid4().hex[:8]}@test.example"
        call("/api/auth/signup", {"email": email, "password": "Abc12345"})
        code = "123456"; srv.CODES[email]["h"] = srv.hash_code(code)
        st, d, h = call("/api/auth/verify", {"email": email, "code": code})
        self.assertEqual(st, 200); self.assertIn("HttpOnly", h.get("Set-Cookie", ""))

if __name__ == "__main__":
    unittest.main(verbosity=2)
