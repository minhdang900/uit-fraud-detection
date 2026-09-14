"""Intentionally empty.

Its presence is the mechanism, not its contents: pytest inserts the directory
containing the rootdir conftest into `sys.path`, which is what lets `tests/`
do `from fraud_cost import ...` without an installed package or a path hack in
every test file.

Deleting this file breaks the whole suite with "ModuleNotFoundError:
fraud_cost" -- so it is kept, and documented, rather than tidied away as an
empty file.
"""
