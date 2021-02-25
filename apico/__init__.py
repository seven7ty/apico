# -*- coding: utf-8 -*-

"""
RESTful API Monitor
~~~~~~~~~~~~~~~~~~

A tool for monitoring RESTful APIs

:copyright: (c) 2021 wulf
:license: MIT, see LICENSE for more details.
"""

from .monitor import Monitor
from .request import Request
from requests import Response
from collections import namedtuple

__version__ = '1.0.0'
__title__ = 'apico'
__license__ = 'MIT'
__author__ = 'wulf'
__email__ = 'wulf.developer@gmail.com'
__uri__ = "https://github.com/itsmewulf/apico"
__copyright__ = '(c) 2021 %s' % __author__

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=1, minor=0, micro=0, releaselevel='final', serial=0)
