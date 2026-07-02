# 1. Pull functions to the top level for easier importing
from .mqtt_broker import broker

# 2. Define package-level metadata
__version__ = "1.0.0"
__author__ = "Christopher Milliren"

# 3. Control wildcard (*) imports
# __all__ = ["massa"]