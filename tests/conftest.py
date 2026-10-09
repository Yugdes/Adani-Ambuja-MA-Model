import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from model.merger_model import MergerModel  # noqa: E402


@pytest.fixture(scope="session")
def root():
    return ROOT


@pytest.fixture(scope="session")
def model():
    return MergerModel()


@pytest.fixture(scope="session")
def summary(model):
    return model.get_summary()
