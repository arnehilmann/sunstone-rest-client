#!/usr/bin/env python
from __future__ import print_function
import json
import re

import requests
from bs4 import BeautifulSoup


class RestClient(object):
    def __init__(self, url, verify=True):
        self.url = url if url.endswith("/") else url + "/"
        self.csrftoken = None
        self.client_opts = {}
        self.verify = verify
        self.cache = {}
        self.session = None

    def login(self, username, password, **kwargs):
        self.session = requests.session()

        login = self.session.post(self.url + "login",
                                  auth=(username, password),
                                  verify=self.verify)
        if not login.ok:
            raise Exception("cannot login on %s" % self.url)

        root = self.session.get(self.url,
                                headers={'Referer': self.url},
                                verify=self.verify)

        self.csrftoken = find_csrftoken(root.content)
        if not self.csrftoken:
            raise Exception("login successfully, but no csrftoken found in %s" % self.url)

        self.client_opts["csrftoken"] = self.csrftoken

        return self

    def _fetch(self, endpoint=""):
        endpoint = endpoint if endpoint.startswith("/") else "/" + endpoint
        if endpoint in self.cache:
            return self.cache[endpoint]
        reply = self.session.get(self.url + endpoint,
                                 params=self.client_opts,
                                 verify=self.verify)
        if not reply.ok:
            raise Exception("unable to fetch %s: %s" % (endpoint, reply.reason))

        reply_json = reply.json()
        self.cache[endpoint] = reply_json
        return reply_json

    def fetch_vms(self):
        vms = self._fetch("vm")["VM_POOL"]["VM"]
        if isinstance(vms, dict):
            return [vms]
        return vms if vms else []

    def get_vm_by_id(self, id):
        id = str(id)
        for vm in self.fetch_vms():
            if vm["ID"] == id:
                return vm

    def get_multiple_vms_by_name(self, name):
        for vm in self.fetch_vms():
            if vm["NAME"] == name:
                yield vm

    def get_first_vm_by_name(self, name):
        return next(self.get_multiple_vms_by_name(name))

    def fetch_templates(self):
        templates = self._fetch("vmtemplate")["VMTEMPLATE_POOL"]["VMTEMPLATE"]
        if isinstance(templates, dict):
            templates = [templates]
        return templates

    def get_template_by_id(self, id):
        id = str(id)
        for template in self.fetch_templates():
            if template["UID"] == id:
                return template
        return {}

    def get_multiple_templates_by_name(self, name):
        for template in self.fetch_templates():
            if template["NAME"] == name:
                yield template

    def get_first_template_by_name(self, name):
        return next(self.get_multiple_templates_by_name(name))

    def _action(self, endpoint, perform, params):
        action = {"action": {"perform": perform, "params": params},
                  "csrftoken": self.csrftoken}
        reply = self.session.post(self.url + endpoint, data=json.dumps(action))
        return reply

    def instantiate(self, template, vm_name):
        endpoint = "vmtemplate/%s/action" % template["UID"]
        params = {"vm_name": vm_name, "hold": False, "template": template["TEMPLATE"]}
        return self._action(endpoint, "instantiate", params)

    def instantiate_by_name(self, template_name, vm_name):
        template = self.get_first_template_by_name(template_name)
        return self.instantiate(template, vm_name)

    def instantiate_by_id(self, template_id, vm_name):
        template = self.get_template_by_id(template_id)
        return self.instantiate(template, vm_name)

    def delete_vm(self, vm):
        return self.delete_vm_by_id(vm["ID"])

    def delete_multiple_vms_by_name(self, name):
        replies = {}
        for vm in self.get_multiple_vms_by_name(name):
            replies[vm["ID"]] = self.delete_vm(vm)
        return replies

    def delete_vm_by_id(self, vm_id):
        data = "csrftoken=%s" % self.csrftoken
        endpoint = "vm/%s" % vm_id
        reply = self.session.delete(self.url + endpoint,
                                    data=data,
                                    headers={"Content-Type":
                                             "application/x-www-form-urlencoded; charset=UTF-8"})
        return reply

    def fetch_hosts(self):
        hosts = self._fetch("host")["HOST_POOL"]["HOST"]
        if isinstance(hosts, dict):
            return [hosts]
        return hosts if hosts else []


def find_csrftoken(html):
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup.findAll('script'):
        match = re.search('var csrftoken\s*=\s*["\'](.*)["\']\s*;', script.text)
        if match:
            return match.group(1)
    return None


if __name__ == "__main__":
    client = RestClient("http://localhost:9869").login("oneadmin", "opennebula")
    print(client.fetch_hosts())
