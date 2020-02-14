"""For use with pytest-readme pytest plugin"""

print("Running conftest.py", flush=True)
from pytest_readme import setup

setup()
