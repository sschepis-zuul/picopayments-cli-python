# coding: utf-8
# Copyright (c) 2016 Fabian Barkhau <f483@storj.io>
# License: MIT (see LICENSE file)


import json
import requests
from requests.auth import HTTPBasicAuth
from . import auth
from . import err


def http_call(url, method, params={}, username=None,
              password=None, verify_ssl_cert=True):
    payload = {"method": method, "params": params, "jsonrpc": "2.0", "id": 0}
    kwargs = {
        "url": url,
        "headers": {'content-type': 'application/json'},
        "data": json.dumps(payload),
        "verify": verify_ssl_cert,
    }
    if username and password:
        kwargs["auth"] = HTTPBasicAuth(username, password)
    response = requests.post(**kwargs).json()
    if "result" not in response:
        raise err.RpcCallFailed(payload, response)
    return response["result"]


def auth_http_call(url, method, params={}, username=None, password=None,
                   verify_ssl_cert=True, auth_wif=None):

    if auth_wif:
        params = auth.sign_json(params, auth_wif)

    result = http_call(
        url, method, params=params, username=username,
        password=password, verify_ssl_cert=verify_ssl_cert
    )

    if auth_wif:
        auth.verify_json(result)

    return result


class API(object):

    def __init__(self, url, auth_wif=None, username=None,
                 password=None, verify_ssl_cert=True):
        self.url = url
        self.auth_wif = auth_wif
        self.username = username
        self.password = password
        self.verify_ssl_cert = verify_ssl_cert

    def __getattribute__(self, name):
        props = ["url", "auth_wif", "username", "password", "verify_ssl_cert"]
        auth_methods = ["mph_request", "mph_deposit", "mph_sync"]

        if name in props:
            return object.__getattribute__(self, name)

        def wrapper(**kwargs):
            return auth_http_call(
                url=self.url, method=name, params=kwargs,
                auth_wif=self.auth_wif if name in auth_methods else None,
                verify_ssl_cert=self.verify_ssl_cert,
                username=self.username, password=self.password,
            )
        return wrapper
