pytest_plugins = [
    "common_amirainvest_com.utils.test.fixtures.database",
    "common_amirainvest_com.utils.test.fixtures.auth",
]

import pathlib

import pytest


def pytest_collection_modifyitems(config, items):
    rootdir = pathlib.Path(config.rootdir)
    for item in items:
        rel_path = pathlib.Path(item.fspath).relative_to(rootdir)
        if "/test/unit/" in str(rel_path):
            mark_name = "unit_test"
        elif "/test/integration/" in str(rel_path):
            mark_name = "integration_test"
        else:
            raise ValueError
        if mark_name:
            mark = getattr(pytest.mark, mark_name)
            item.add_marker(mark)
