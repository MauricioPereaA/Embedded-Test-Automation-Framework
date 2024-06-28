# -*- coding: utf-8 -*-
__version__: str = "2023.05.19"

# SET GLOBAL VARIABLES FROM ENVIRONMENT AND ARGS.
import os
import platform

SPHINX_DOC_MODE = os.environ.get("SPHINX_DOC_MODE", "0") in (1, "1")
cache = platform.uname()
PLATFORM = cache.system
HOST_NODE = cache.node
VERSION = cache.version
import DTAF.devices
import DTAF.interfaces
import DTAF.factory
