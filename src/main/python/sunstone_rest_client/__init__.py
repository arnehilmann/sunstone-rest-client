#!/usr/bin/env python
from __future__ import print_function
import json
import logging
import re
import time

import requests
from bs4 import BeautifulSoup

try:
    from logging import NullHandler
except ImportError:
    from sunstone_rest_client.util import NullHandler


class LoginFailedException(Exception):
    pass


class NotFoundException(Exception):
    pass


class ReplyException(Exception):
    pass


logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


class RestClient(object):
    vm_details = {"/log": "vm_log", "": "VM"}

    def __init__(self, url, verify=True, use_cache=True, disable_urllib3_warnings=True, simple_logging=False):
        self.url = url.rstrip("/")
        self.username = None
        self.password = None
        self.csrftoken = None
        self.client_opts = {}
        self.verify = verify
        self.use_cache = use_cache
        self.failed_login = False

        self.cache = {}
        self.session = None

        if disable_urllib3_warnings:
            logger.debug("disabling urllib3 warning of requests packages")
            requests.packages.urllib3.disable_warnings()

        if simple_logging:
            logger.setLevel(logging.DEBUG)
            sh = logging.StreamHandler()
            sh.setLevel(logging.DEBUG)
            sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(sh)

    def login(self, username, password, **kwargs):
        self.username = username
        self.password = password
        logger.debug("login url: %s" % self.url)
        logger.debug("login username: %s" % self.username)
        self.failed_login = False
        return self

    def _login(self):
        if self.failed_login:
            raise LoginFailedException("login failed too often, giving up here...")
        for i in range(10):
            self.session = requests.session()  # TODO is it really necessary to start a new session on every iteration?
            try:
                login = self.session.post(self.url + "/login", auth=(self.username, self.password))
                if not login.ok:
                    self.failed_login = True
                    raise LoginFailedException("login failed too often, giving up here...")
            except Exception as e:
                logger.debug("%s: retrying" % str(e))
                time.sleep(.2)
                continue

            logger.debug("sunstone session cookie: %s" % self.session.cookies.get("sunstone"))
            time.sleep(.2)

            root = self.session.get(self.url, headers={'Referer': self.url})

            if self.session.cookies.get("one-user"):
                break
            time.sleep(.2)

        if not self.session.cookies.get("one-user"):
            raise LoginFailedException("credentials supposedly okay, but authorization handshake failed repeatedly")

        self.csrftoken = find_csrftoken(root.content)
        if not self.csrftoken:
            raise LoginFailedException("no csrftoken found in %s" % self.url)

        self.client_opts["csrftoken"] = self.csrftoken

        for i in range(5):
            try:
                logger.debug("checking session, fetching random vm details, awaiting status != 401 (Unauthorized)")
                self.get_vm_detail(333333, "log")
                break
            except NotFoundException:
                break
            except Exception as e:
                if i == 10:
                    raise LoginFailedException("login and csrftoken okay, but still not authorized, giving up!", e)
                logger.debug(e)
                time.sleep(.2)

        return self

    def _fetch(self, endpoint=""):
        endpoint = endpoint if endpoint.startswith("/") else "/" + endpoint
        if endpoint in self.cache:
            return self.cache[endpoint]
        if not self.csrftoken:
            self._login()
        reply = self.session.get(self.url + endpoint, params=self.client_opts)
        if not reply.ok:
            if reply.status_code == 404:
                raise NotFoundException(endpoint)
            raise ReplyException("unable to fetch %s: %i %s" % (endpoint, reply.status_code, reply.reason), reply)

        reply_json = reply.json()
        if self.use_cache:
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

    def get_vm_detail(self, id, detail=None):
        if detail:
            detail = detail if detail.startswith("/") else "/" + detail
        detail = detail if detail else ""
        toplevel = RestClient.vm_details.get(detail)
        if toplevel:
            return self._fetch("/vm/%s%s" % (id, detail)).get(toplevel)
        return self._fetch("/vm/%s%s" % (id, detail))

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
        action = {"action": {"perform": perform, "params": params}, "csrftoken": self.csrftoken}
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
    logging.basicConfig(level=logging.DEBUG)
    client = RestClient("http://localhost:9869").login("oneadmin", "opennebula")
    print(client.get_vm_detail(38))
    print(client.get_vm_detail(38, "log"))
