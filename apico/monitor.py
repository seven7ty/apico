# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2021 Paul Przybyszewski (wulf)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests
import inspect
import time
from typing import Optional, Callable, Union, IO
from requests.cookies import RequestsCookieJar

__all__ = ('Monitor',)


class Monitor:
    __event_names__: tuple = ('change', 'request', 'no_change')

    def __init__(self,
                 url: str,
                 rate: float,
                 method: str = 'GET',
                 params: Optional[Union[dict, bytes]] = None,
                 data: Optional[Union[dict, list[tuple], bytes, IO]] = None,
                 headers: Optional[dict] = None,
                 cookies: Optional[Union[dict, RequestsCookieJar]] = None,
                 files: Optional[dict[str, IO]] = None,
                 auth: Optional[Union[tuple, Callable]] = None,
                 timeout: Union[int, float] = None,
                 allow_redirects: bool = True,
                 proxies=None,
                 hooks=None,
                 stream: bool = False,
                 verify: Optional[Union[bool, str]] = True,
                 cert: Optional[Union[str, tuple[str, str]]] = None,
                 json: Optional[dict] = None):
        """
        Initializes a new instance of the Monitor class with the specified request parameters.

        :param rate: The rate at which the monitor should run (interval)
        :param method: method for the new :class:`Request` object.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query
            string for the :class:`Request`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the
            :class:`Request`.
        :param headers: (optional) Dictionary of HTTP Headers to send with the
            :class:`Request`.
        :param cookies: (optional) Dict or CookieJar object to send with the
            :class:`Request`.
        :param files: (optional) Dictionary of ``'filename': file-like-objects``
            for multipart encoding upload.
        :param auth: (optional) Auth tuple or callable to enable
            Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param allow_redirects: (optional) Set to True by default.
        :type allow_redirects: bool
        :param proxies: (optional) Dictionary mapping protocol or protocol and
            hostname to the URL of the proxy.
        :param stream: (optional) whether to immediately download the response
            content. Defaults to ``False``.
        :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``. When set to
            ``False``, requests will accept any TLS certificate presented by
            the server, and will ignore hostname mismatches and/or expired
            certificates, which will make your application vulnerable to
            man-in-the-middle (MitM) attacks. Setting verify to ``False``
            may be useful during local development or testing.
        :param cert: (optional) if String, path to ssl client cert file (.pem).
            If Tuple, ('cert', 'key') pair.
        """

        # Monitor properties
        self.rate: float = rate
        self.url: str = url
        self.last_response: Optional[requests.Response] = None
        self._matrix: dict = {}

        # Session stuff
        self.session: requests.Session = requests.session()

        # Request properties
        self.method: str = method
        self.cookies: Optional[Union[dict, RequestsCookieJar]] = cookies
        self.params: Optional[Union[dict, bytes]] = params
        self.data: Optional[Union[dict, list[tuple], bytes, IO]] = data
        self.headers: Optional[dict] = headers
        self.files: Optional[dict[str, IO]] = files
        self.auth: Optional[Union[tuple, Callable]] = auth
        self.hooks: Optional[dict] = hooks
        self.json: Optional[dict] = json
        self.timeout: Union[int, float] = timeout
        self.allow_redirects: bool = allow_redirects
        self.proxies: Optional[dict] = proxies
        self.stream: bool = stream
        self.verify: Optional[Union[bool, str]] = verify
        self.cert: Optional[Union[str, tuple[str, str]]] = cert

    @staticmethod
    def _are_different(res1: requests.Response, res2: requests.Response) -> bool:
        return any((res1.json() != res2.json(),
                    res1.status_code != res2.status_code,
                    res1.content != res2.content,
                    res1.text != res2.text))

    def __run(self) -> None:
        while True:
            if callback := self._matrix.get('request', None):
                callback()
            if 'change' in self._matrix:
                res: requests.Response = self.session.request(
                    method=self.method,
                    url=self.url,
                    params=self.params,
                    data=self.data,
                    headers=self.headers,
                    cookies=self.cookies,
                    files=self.files,
                    auth=self.auth,
                    hooks=self.hooks,
                    json=self.json,
                    proxies=self.proxies,
                    stream=self.stream,
                    verify=self.verify,
                    cert=self.cert,
                    timeout=self.timeout,
                    allow_redirects=self.allow_redirects
                )
                if self.last_response is None:
                    self._matrix['change'](res, res)
                else:
                    if self._are_different(res, self.last_response):
                        self._matrix['change'](self.last_response, res)
                    elif callback := self._matrix.get('no_change', None):
                        callback()
                self.last_response: requests.Response = res
            time.sleep(self.rate)

    def listener(self, event: str = None) -> Callable:
        """
        Register a new listener for the given event.
        Valid event names are 'change', 'request' and 'no_change'.
        'request' is called **before** every request is made (no params).
        'change' is called when the response changes (2 params - old, new).
        'no_change' is called when the response is the same as before ()

        :param event: The event name.
        :return: A registered callback function
        """

        if event is not None and not isinstance(event, str):
            raise TypeError(
                'Monitor.listener expected str but received {0.__class__.__name__!r} instead.'.format(event))

        def decorator(func: Callable) -> Callable:
            actual: Callable = func
            if isinstance(actual, staticmethod):
                actual: Callable = actual.__func__
            if inspect.iscoroutinefunction(actual):
                raise TypeError('Listener cannot be a coroutine function.')
            to_assign: str = str(event or actual.__name__).lower().replace('on_', '', 1)
            if to_assign not in self.__event_names__:
                raise RuntimeError(f'{to_assign} is not a valid event to listen for')
            elif to_assign == 'change' and (p := len(inspect.signature(actual).parameters)) != 2:
                raise RuntimeError(f'Expected change callback to take in 2 parameters, got {p}')
            self._matrix[to_assign] = actual
            return func

        return decorator

    def start(self) -> None:
        self.__run()
