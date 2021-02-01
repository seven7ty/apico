import abc
from typing import Callable


class BaseMonitor(metaclass=abc.ABCMeta):
    __slots__ = ('_rate', '_url', '_headers', '_matrix', 'body', 'method', 'last_payload')

    @abc.abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def listener(self, event=None) -> Callable:
        raise NotImplementedError
