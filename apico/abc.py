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

import abc
from typing import Callable

__all__ = ('BaseMonitor',)


class BaseMonitor(metaclass=abc.ABCMeta):
    __event_names__: tuple = ()

    __slots__ = ('_rate', 'url',
                 '_headers', '_matrix',
                 'body', 'method',
                 'last_res')

    @abc.abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def listener(self, event: str = None) -> Callable:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'<{self.__class__.__qualname__} url=%s>' % self.url

    def __float__(self) -> float:
        return self._rate
