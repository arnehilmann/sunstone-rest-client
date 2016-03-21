#!/usr/bin/env python
import unittest

import sunstone_rest_client


class HostTests(unittest.TestCase):

    def test_fetch_hosts(self):
        client = sunstone_rest_client.RestClient("http://foobar:4711")
        client.cache = {"/host": {"HOST_POOL": {"HOST": {"NAME": "dummyHost", "ID": "42"}}}}
        result = client.fetch_hosts()
        self.assertTrue("NAME" in result[0])


if __name__ == "__main__":
    unittest.main()
