#!/usr/bin/env python
from mock import patch, Mock
import unittest

import sunstone_rest_client


class LoginTests(unittest.TestCase):
    def test_init(self):
        sunstone_rest_client.RestClient("http://foobar:4711")

    @patch('requests.session', Mock())
    @patch('sunstone_rest_client.find_csrftoken', Mock(return_value="12345"))
    def test_login(self):
        sunstone_rest_client.RestClient("http://foobar:4711").login("user", "passwd")

if __name__ == "__main__":
    unittest.main()
