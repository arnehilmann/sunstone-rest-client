#!/usr/bin/env python
from mock import patch, Mock
import unittest

import sunstone_rest_client
import sunstone_rest_client.util


class LoginTests(unittest.TestCase):
    def test_init(self):
        sunstone_rest_client.RestClient("http://foobar:4711")

    @patch('requests.session', Mock())
    @patch('sunstone_rest_client.find_csrftoken', Mock(return_value="12345"))
    def test_login(self):
        sunstone_rest_client.RestClient("http://foobar:4711").login("user", "passwd")

    @patch('requests.session', Mock())
    @patch('sunstone_rest_client.find_csrftoken', Mock(return_value=None))
    def test_failed_login(self):
        client = sunstone_rest_client.RestClient("http://foobar:4711").login("user", "passwd")
        self.assertRaises(Exception, client._login)

    def test_find_csrf_token(self):
        html = """<httml><bla></bla><script>tadahh</script><script>var csrftoken='foo';</script></html>"""
        token = sunstone_rest_client.find_csrftoken(html)
        self.assertEquals(token, "foo")

    def test_null_handler(self):
        nh = sunstone_rest_client.util.NullHandler()
        nh.emit("dummy")


if __name__ == "__main__":
    unittest.main()
