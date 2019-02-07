"""For use with pytest-readme pytest plugin"""

import sys

collect_ignore = ["setup.py"]
if sys.version_info < (3, 5):
    collect_ignore.append("tests/test_async.py")
    collect_ignore.append("test_readme.py")
    collect_ignore.append("trustpilot/async_client.py")

from pytest_readme import setup
setup()
