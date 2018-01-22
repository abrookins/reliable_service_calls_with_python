#!/usr/bin/env python
# encoding: utf-8


class MockResponse:
    """A helper for mocking `request` library responses."""
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


