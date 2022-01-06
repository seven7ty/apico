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
from .abc import BaseMonitor
from typing import Optional, Callable

__all__ = ('Monitor',)


class Monitor(BaseMonitor):
    __event_names__: tuple = ('change', 'request', 'no_change')

    def __init__(self, url: str,
                 rate: float,
                 headers: Optional[dict] = None,
                 body: Optional[dict] = None,
                 method: str = 'get'):
        if not isinstance(headers, dict):
            headers: dict = {}
        if not isinstance(body, dict):
            body: dict = {}
        self.rate: float = rate
        self.url: str = url
        self.headers: dict = headers
        self._matrix: dict = {}
        self.body: dict = body
        self.method: str = method
        self.last_response: Optional[requests.Response] = None

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
                res: requests.Response = requests.request(method=self.method,
                                                          url=self.url,
                                                          headers=self.headers,
                                                          json=self.body)
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
