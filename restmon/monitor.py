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
import time
import inspect
from .abc import BaseMonitor
from typing import Callable, Optional

__all__ = ('Monitor',)

VALID_EVENTS: tuple = ('change', 'request', 'no_change')


class Monitor(BaseMonitor):
    def __init__(self, url: str,
                 rate: float,
                 headers=None,
                 body=None,
                 method: str = 'get'):
        if not isinstance(headers, dict):
            headers: dict = {}
        if not isinstance(body, dict):
            body: dict = {}
        self._rate: float = rate
        self.url: str = url
        self._headers: dict = headers
        self._matrix: dict = {}
        self.body: dict = body
        self.method: str = method
        self.last_res: Optional[requests.Response] = None

    @staticmethod
    def _are_different(res1: requests.Response, res2: requests.Response) -> bool:
        return any((res1.json() != res2.json(),
                    res1.status_code != res2.status_code,
                    res1.content != res2.content,
                    res1.text != res2.text))

    def __run(self) -> None:
        while True:
            if c := self._matrix.get('request', None):
                c()
            if 'change' in self._matrix:
                res: requests.Response = requests.request(method=self.method,
                                                          url=self.url,
                                                          headers=self._headers,
                                                          json=self.body)
                if self.last_res is None:
                    self._matrix['change'](res, res)
                else:
                    if self._are_different(res, self.last_res):
                        self._matrix['change'](self.last_res, res)
                    elif c := self._matrix.get('no_change', None):
                        c()
                self.last_res: requests.Response = res
            time.sleep(self._rate)

    def listener(self, event=None) -> Callable:
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
            if to_assign not in VALID_EVENTS:
                raise RuntimeError(f'{to_assign} is not a valid event to listen for')
            elif to_assign == 'change' and (p := len(inspect.signature(actual).parameters)) != 2:
                raise RuntimeError(f'Expected change callback to take in 2 parameters, got {p}')
            self._matrix[to_assign]: Callable = actual
            return func

        return decorator

    def start(self) -> None:
        self.__run()
