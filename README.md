# sunstone-rest-client

[![Build Status](https://travis-ci.org/arnehilmann/sunstone-rest-client.svg?branch=master)](https://travis-ci.org/arnehilmann/sunstone-rest-client)
[![Coverage Status](https://coveralls.io/repos/github/arnehilmann/sunstone-rest-client/badge.svg?branch=master)](https://coveralls.io/github/arnehilmann/sunstone-rest-client?branch=master)
[pypi](https://pypi.python.org/pypi/sunstone-rest-client)

A minimal ReST client for [sunstone](http://docs.opennebula.org/4.14/administration/sunstone_gui/sunstone.html),
the web ui of [opennebula](http://opennebula.org/tryout/sandboxvirtualbox/)

## Usage

```python
from sunstone_rest_client import RestClient

client = RestClient("https://<sunstone-uri>").login("user", "passwd")
print client.fetch_vms()

client.instantiate(0, "my-new-vm")  # instantiates template id 0

# client.delete_vm(0)
```
