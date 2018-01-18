#!/usr/bin/env python
# encoding: utf-8
import os

from apiclient import ApiClient


class MetricsClient(ApiClient):
    def __init__(self):
        super().__init__('metrics')

    def get(self, *args, **kwargs):
        if os.environ['TESTING']:
            return
        super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if os.environ['TESTING']:
            return
        super().post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if os.environ['TESTING']:
            return
        super().delete(*args, **kwargs)
