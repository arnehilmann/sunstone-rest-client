#!/usr/bin/env python
from mock import Mock
import unittest

import sunstone_rest_client


class VmTests(unittest.TestCase):

    def test_fetch_vms(self):
        client = sunstone_rest_client.RestClient("http://foobar:4711")
        client.cache = {"/vm": {"VM_POOL": {"VM": {"NAME": "dummyVM", "ID": "42"}}},
                        "/vmtemplate": {"VMTEMPLATE_POOL": {"VMTEMPLATE": {"NAME": "foo", "UID": "333"}}}}
        result = client.fetch_vms()
        self.assertTrue("NAME" in result[0])

        result = client.get_vm_by_id(42)
        self.assertTrue(result["ID"] == "42")

        result = client.get_first_vm_by_name("dummyVM")
        self.assertTrue(result["ID"] == "42")

        result = client.get_first_template_by_name("foo")
        self.assertTrue(result["UID"] == "333")

        self.assertRaises(StopIteration, client.get_first_vm_by_name, "unknownVM")

    def test_fetch_failed(self):
        client = sunstone_rest_client.RestClient("http://foobar:4711")
        client.session = Mock()
        failed = Attrs(ok=False, reason="oops")
        client.session.get = Mock(return_value=failed)
        self.assertRaises(Exception, client._fetch)

    def test_fetch_successfully(self):
        client = sunstone_rest_client.RestClient("http://foobar:4711")
        client.session = Mock()
        client.csrftoken = "1234"
        successfully = Attrs(ok=True, json=lambda: "tadahh")
        client.session.get = Mock(return_value=successfully)
        response = client._fetch()
        self.assertEqual("tadahh", response)

    def test_delete(self):
        client = sunstone_rest_client.RestClient("http://foobar:4711")
        client.cache = {"/vm": {"VM_POOL": {"VM": {"NAME": "dummyVM", "ID": "42"}}}}
        client.session = Mock()
        client.session.delete = Mock(return_value="ok")
        result = client.delete_multiple_vms_by_name("dummyVM")
        self.assertEqual(result["42"], "ok")


class Attrs(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


if __name__ == "__main__":
    unittest.main()
