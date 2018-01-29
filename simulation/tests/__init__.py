#!/usr/bin/env python
# encoding: utf-8
from requests import Timeout


def mock_200_response(*args, **kwargs):
    return MockResponse([1, 2, 3], 200)


def mock_connection_error(*args, **kwargs):
    raise ConnectionError()


def mock_timeout(*args, **kwargs):
    raise Timeout()


def mock_runtime_error(*args, **kwargs):
    raise RuntimeError()


class MockResponse:
    """A helper for mocking `request` library responses."""
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


