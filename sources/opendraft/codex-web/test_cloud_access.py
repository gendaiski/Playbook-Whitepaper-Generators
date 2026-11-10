"""Offline regression checks for personal-link access; no real secrets used."""
import io
import json
import unittest
from unittest.mock import patch
import cloud_access


class Request:
    def __init__(self, payload):
        raw = json.dumps(payload).encode()
        self.headers = {'Content-Length': str(len(raw))}
        self.rfile = io.BytesIO(raw)
        self.wfile = io.BytesIO()
        self.response_headers = {}
    def send_response(self, status): self.status = status
    def send_header(self, key, value): self.response_headers[key] = value
    def end_headers(self): pass


class PersonalLinkTests(unittest.TestCase):
    def setUp(self):
        self.patch = patch.object(cloud_access, 'ACCESS_TOKEN', 'test-only-placeholder-' * 3)
        self.patch.start()
    def tearDown(self): self.patch.stop()
    def test_private_by_default(self):
        self.assertFalse(cloud_access.authorized({}))
        self.assertFalse(cloud_access.authorized({'Cookie': 'od_session=wrong'}))
    def test_valid_cookie(self):
        self.assertTrue(cloud_access.authorized({'Cookie': 'od_session=' + cloud_access.cookie_value()}))
    def test_local_mode_retained(self):
        with patch.object(cloud_access, 'ACCESS_TOKEN', ''):
            self.assertTrue(cloud_access.authorized({}))
    def test_unlock_cookie_has_required_flags_and_no_secret_in_body(self):
        request = Request({'token': cloud_access.ACCESS_TOKEN})
        cloud_access.unlock(request)
        self.assertEqual(request.status, 200)
        for flag in ['Secure', 'HttpOnly', 'SameSite=Strict']:
            self.assertIn(flag, request.response_headers['Set-Cookie'])
        self.assertNotIn(cloud_access.ACCESS_TOKEN.encode(), request.wfile.getvalue())
    def test_invalid_token_gets_no_cookie(self):
        request = Request({'token': 'wrong'})
        cloud_access.unlock(request)
        self.assertEqual(request.status, 403)
        self.assertNotIn('Set-Cookie', request.response_headers)
    def test_oversized_request_gets_no_cookie(self):
        request = Request({'token': 'x' * 3000})
        cloud_access.unlock(request)
        self.assertEqual(request.status, 403)
        self.assertNotIn('Set-Cookie', request.response_headers)
    def test_non_object_request_is_rejected(self):
        request = Request(['unexpected'])
        cloud_access.unlock(request)
        self.assertEqual(request.status, 403)


if __name__ == '__main__': unittest.main()
