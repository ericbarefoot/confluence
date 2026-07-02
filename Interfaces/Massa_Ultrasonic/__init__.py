# 1. Pull functions to the top level for easier importing
from .job_config import job_configuration

# 2. Define package-level metadata
__version__ = "1.0.0"
__author__ = "Christopher Milliren"

# 3. Control wildcard (*) imports
# __all__ = ["massa"]