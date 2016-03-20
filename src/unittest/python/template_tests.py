#!/usr/bin/env python
from mock import Mock
import unittest

import sunstone_rest_client


class TemplateTests(unittest.TestCase):

    def test_instantiate(self):
        client = sunstone_rest_client.RestClient("http://foobar:4711")
        client.cache = {"/vm": {"VM_POOL": {"VM": {"NAME": "dummyVM", "ID": "42"}}},
                        "/vmtemplate": {
                            "VMTEMPLATE_POOL": {"VMTEMPLATE": {"NAME": "foo", "UID": "333", "TEMPLATE": "empty"}}}}
        client.session = Mock()
        client.session.post = Mock(return_value="ok")
        result = client.instantiate_by_name("foo", "newVM")
        self.assertEqual(result, "ok")


if __name__ == "__main__":
    unittest.main()
