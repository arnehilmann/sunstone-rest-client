# sunstone-rest-client

[![Build Status](https://travis-ci.org/arnehilmann/sunstone-rest-client.svg?branch=master)](https://travis-ci.org/arnehilmann/sunstone-rest-client)
[![Coverage Status](https://coveralls.io/repos/github/arnehilmann/sunstone-rest-client/badge.svg?branch=master)](https://coveralls.io/github/arnehilmann/sunstone-rest-client?branch=master)

A minimal ReST client for sunstone, the web ui of opennebula

## Usage

```python
from sunstone_rest_client import RestClient

client = RestClient("https://<sunstone-uri>").login("user", "passwd")
print client.fetch_vms()

client.instatiate(0, "my-new-vm")

# client.delete_vm(0)
```
