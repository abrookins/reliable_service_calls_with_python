#!/usr/bin/env python
# encoding: utf-8
import requests
from requests.adapters import HTTPAdapter

urls = {
    'authentication': 'http://authentication:8000/authenticate',
    'recommendations': 'http://recommendations:8002/recommendations',
    'popular': 'http://popular:8003/popular_items'
}


class ApiClient(requests.Session):
    def __init__(self, service, max_retries=3):
        super().__init__()
        self.url = urls[service]
        self.mount(self.url, HTTPAdapter(max_retries=max_retries))

    def get(self, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 1
        return super().get(self.url, **kwargs)

    def post(self, data=None, json=None, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 1
        return super().post(self.url, data, json, **kwargs)

    def delete(self, url, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 1
        return super().delete(self.url, **kwargs)
