from six.moves.urllib.parse import urljoin
import re, uuid
import requests
from requests import get
import json
import logging

import espressoApi.espressoExceptions as ex

log = logging.getLogger(__name__)


class EspressoConnect(object):
    _rootUrl = "https://api.myespresso.com"  # prod endpoint

    _login_url = "https://api.myespresso.com/espressoapi/auth/login.html"  # prod endpoint
    _default_timeout = 7  # In seconds

    _routes = {
        "api.access.token": "/espressoapi/services/access/token",

        "api.funds": "/espressoapi/services/limitstmt/{exchange}/{customerId}",

        "api.order.place": "/espressoapi/services/orders",
        "api.order.modify": "/espressoapi/services/orders",
        "api.order.cancel": "/espressoapi/services/orders",

        "api.order.cancelbyid": "/espressoapi/services/cancelOrder/{orderid}",

        "api.order.day": "/espressoapi/services/reports/{customerId}",

        "api.trades": "/espressoapi/services/trades/{customerId}",

        "api.reports.exchange": "/espressoapi/services/reports/{exchange}/{customerId}/{orderId}",
        "api.reports.exchange.trades": "/espressoapi/services/reports/{exchange}/{customerId}/{orderId}/trades",

        "api.holdings": "/espressoapi/services/holdings/{customerId}",

        "api.master": "/espressoapi/services/master/{exchange}",
        "api.mastercsv": "/espressoapi/services/master/csv/{exchange}",

        "api.historical.data": "/espressoapi/services/historical/{exchange}/{scripcode}/{interval}"
    }
    accept = "application/json"

    def __init__(self, api_key=None, state=None, vendor_key=None, access_token=None, refresh_token=None,
                 feed_token=None, userId=None, root=None,
                 debug=False, timeout=None, proxies=None, pool=None, disable_ssl=False, accept=None, userType=None,
                 sourceID=None, Authorization=None, clientPublicIP=None, clientMacAddress=None, clientLocalIP=None,
                 privateKey=None):
        # self.refreshToken = None
        self.debug = debug
        self.api_key = api_key
        self.state = state
        self.vendor_key = vendor_key
        self.session_expiry_hook = None
        self.disable_ssl = disable_ssl
        self.access_token = access_token
        self.proxies = proxies if proxies else {}
        self.root = root or self._rootUrl
        self.timeout = timeout or self._default_timeout
        self.privateKey = api_key
        self.accept = self.accept

        if pool:
            self.reqsession = requests.Session()
            reqadapter = requests.adapters.HTTPAdapter(**pool)
            self.reqsession.mount("https://", reqadapter)
            print("in pool")
        else:
            self.reqsession = requests

        # disable requests SSL warning
        requests.packages.urllib3.disable_warnings()

    # setSessionExpiryHook takes a function as an argument and sets it as the session_expiry_hook attribute of the class instance
    def requestHeaders(self):
        headers = {
            "api-key": self.privateKey,
            "access-token": self.access_token,
            "Content-type": self.accept
        }

        if self.vendor_key:  # Only include "vendor" if it is not None or empty
            headers["vendor-key"] = self.vendor_key

        return headers

    def login_url(self, vendor_key=None):
        """Get the remote login url to which a user should be redirected to initiate the login flow."""
        base_url = "{}?api_key={}".format(self._login_url, self.api_key)
        # vendor_key argument is optional and is used to specify a vendor key in the URL
        if vendor_key:
            base_url += "&vendor_key={}".format(vendor_key)
        else:
            print("No vendor key")
        # state parameter in the URL is set to 12345
        base_url += "&state=12345"
        return base_url

    def _request(self, route, method, parameters=None):
        """Make an HTTP request."""
        params = parameters.copy() if parameters else {}
        uri = self._routes[route].format(**params)
        url = urljoin(self.root, uri)
        # Custom headers
        headers = self.requestHeaders()
        if self.access_token:
            # set authorization header
            auth_header = self.access_token
            headers["Authorization"] = "{}".format(auth_header)
        if self.debug:
            log.debug("Request: {method} {url} {params} {headers}".format(method=method, url=url, params=params,
                                                                          headers=headers))
        try:
            r = requests.request(method,
                                 url,
                                 data=json.dumps(params) if method in ["POST", "PUT"] else None,
                                 params=json.dumps(params) if method in ["GET", "DELETE"] else None,
                                 headers=headers,
                                 verify=not self.disable_ssl,
                                 allow_redirects=True,
                                 timeout=self.timeout,
                                 proxies=self.proxies)
        except Exception as e:
            raise e
        if self.debug:
            log.debug("Response: {code} {content}".format(code=r.status_code, content=r.content))
        # Validate the content type.
        if "json" in headers["Content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))
            except ValueError:
                raise ex.DataException("Couldn't parse the JSON response received from the server: {content}".format(
                    content=r.content))
            # api error
            if data.get("error_type"):
                # Call session hook if its registered and TokenException is raised
                if self.session_expiry_hook and r.status_code == 403 and data["error_type"] == "TokenException":
                    self.session_expiry_hook()
                # native errors
                exp = getattr(ex, data["error_type"], ex.GeneralException)
                raise exp(data["message"], code=r.status_code)
            return data
        elif "csv" in headers["Content-type"]:
            return r.content
        else:
            raise ex.DataException("Unknown Content-type ({content_type}) with response: ({content})".format(
                content_type=headers["Content-type"],
                content=r.content))

    def _deleteRequest(self, route, params=None):
        """Alias for sending a DELETE request."""
        return self._request(route, "DELETE", params)

    def _putRequest(self, route, params=None):
        """Alias for sending a PUT request."""
        return self._request(route, "PUT", params)

    def _postRequest(self, route, params=None):
        """Alias for sending a POST request."""
        return self._request(route, "POST", params)

    def _getRequest(self, route, params=None):
        """Alias for sending a GET request."""
        return self._request(route, "GET", params)

    def generate_session(self, request_token, secret_key):
        import base64
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad, unpad
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from base64 import urlsafe_b64encode, urlsafe_b64decode

        key = secret_key.encode('utf-8')
        iv = base64.b64decode("AAAAAAAAAAAAAAAAAAAAAA==")

        def encryptAPIString(plaintext):
            raw = plaintext.encode('utf-8')
            encryptor = Cipher(algorithms.AES(key), modes.GCM(iv, None, 16), default_backend()).encryptor()
            ciphertext = encryptor.update(raw) + encryptor.finalize()
            return base64UrlEncode(ciphertext + encryptor.tag).decode('utf-8')

        def decryptAPIString(ciphertext):
            enc = base64UrlDecode(ciphertext)[:-16]
            decryptor = Cipher(algorithms.AES(key), modes.GCM(iv), default_backend()).decryptor()
            return decryptor.update(enc)

        def base64UrlEncode(data):
            return urlsafe_b64encode(data).rstrip(b'=')

        def base64UrlDecode(base64Url):
            padding = b'=' * (4 - (len(base64Url) % 4))
            return urlsafe_b64decode(base64Url + padding)

        def decryption_method(key, encrypted_data):
            raw = key.encode('utf-8')
            if len(raw) != 32:
                raise ValueError("Invalid key size.")

            nonce = b'\x00' * 16
            skey_spec = AES.new(raw, AES.MODE_GCM, nonce=nonce)
            encrypted_data = base64.urlsafe_b64decode(encrypted_data)
            ciphertext = encrypted_data[:-16]
            received_mac_tag = encrypted_data[-16:]
            decrypted = skey_spec.decrypt_and_verify(ciphertext, received_mac_tag)
            return decrypted.decode('utf-8')

        def encryption_method(key, non_encrypted_data):
            raw = key.encode('utf-8')
            if len(raw) != 32:
                raise ValueError("Invalid key size.")
            nonce = b'\x00' * 16
            skey_spec = AES.new(raw, AES.MODE_GCM, nonce=nonce)
            ciphertext, mac_tag = skey_spec.encrypt_and_digest(pad(non_encrypted_data.encode('utf-8'), AES.block_size))
            encrypted = ciphertext + mac_tag
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')

        decrypted_code = decryption_method(secret_key, request_token)
        # print(decrypted_code)
        result = decrypted_code.split('|')
        for s in result:
            # print(s)
            s
        manipulated_code = result[1] + '|' + result[0]
        # print(manipulated_code)
        msg = manipulated_code
        encStr = encryptAPIString(msg)
        # print("Ecnrypt :", encStr)
        return encStr

        # The purpose of this method is to obtain an access token from an API endpoint

    def get_access_token(self, api_key, encStr, vendor_key='', state=''):
        url = f"{EspressoConnect._rootUrl}{EspressoConnect._routes['api.access.token']}"
        # print(url)
        headers = {'Content-Type': 'application/json'}
        params = {
            'apiKey': api_key,
            'requestToken': encStr,
            'vendorkey': vendor_key,
            'state': state
        }
        print(params)
        response = self._postRequest("api.access.token", params)
        accessResponse = json.dumps(response)
        return accessResponse

    def funds(self, exchange, customerId):
        fundsResponse = self._getRequest("api.funds", {"exchange": exchange, "customerId": customerId})
        fundsResponseString = json.dumps(fundsResponse)
        return fundsResponseString

    def placeOrder(self, orderparams):
        if isinstance(orderparams, str):
            params = json.loads(orderparams)
        else:
            params = orderparams

        # params = orderparams

        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        orderResponse = self._postRequest("api.order.place", params)
        return orderResponse

    def modifyOrder(self, orderparams):
        params = orderparams

        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        orderResponse = self._postRequest("api.order.modify", params)
        return orderResponse

    def cancelOrder(self, orderparams):
        params = orderparams

        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        orderResponse = self._postRequest("api.order.cancel", params)
        return orderResponse

    def cancelOrderById(self, orderid):
        orderResponse = self._getRequest("api.order.cancelbyid", {"orderid": orderid})
        return orderResponse

    def reports(self, customerId):
        reportsResponse = self._getRequest("api.order.day", {"customerId": customerId})
        return reportsResponse

    def trades(self, customerId):
        tradesResponse = self._getRequest("api.trades", {"customerId": customerId})
        return tradesResponse

    def exchange(self, exchange, customerId, orderId):
        exchangeResponse = self._getRequest("api.reports.exchange",
                                            {"exchange": exchange, "customerId": customerId, "orderId": orderId})
        return exchangeResponse

    def exchangetrades(self, exchange, customerId, orderId):
        exchangetradesResponse = self._getRequest("api.reports.exchange.trades",
                                                  {"exchange": exchange, "customerId": customerId, "orderId": orderId})
        return exchangetradesResponse

    def holdings(self, customerId):
        holdingsResponse = self._getRequest("api.holdings", {"customerId": customerId})
        return holdingsResponse

    def master(self, exchange):
        masterResponse = self._getRequest("api.master", {"exchange": exchange})
        return masterResponse

    def mastercsv(self, exchange):
        url = f"{EspressoConnect._rootUrl}{EspressoConnect._routes['api.mastercsv'].format(exchange=exchange)}"
        # print(url)
        response = requests.get(url)
        return response.text
        # if response.status_code == 200:
        #     return response.text
        # else:
        #     return None

    def historicaldata(self, exchange, scripcode, interval):
        historicaldataResponse = self._getRequest("api.historical.data",
                                                  {"exchange": exchange, "scripcode": scripcode, "interval": interval})
        return historicaldataResponse