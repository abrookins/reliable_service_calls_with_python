#!/usr/bin/env python
# encoding: utf-8
import pybreaker
import requests
from requests.adapters import HTTPAdapter
import statsd


c = statsd.StatsClient('graphite', 2003)

urls = {
    'authentication': 'http://authentication:8000/authenticate',
    'recommendations': 'http://recommendations:8002/recommendations',
    'popular': 'http://popular:8003/popular_items'
}

circuit_breakers = {
   'authentication': pybreaker.CircuitBreaker(fail_max=1, reset_timeout=30),
   'recommendations': pybreaker.CircuitBreaker(fail_max=1, reset_timeout=30),
   'popular': pybreaker.CircuitBreaker(fail_max=1, reset_timeout=30)
}


class ApiClient(requests.Session):
    def __init__(self, service, max_retries=3, timeout=1):
        super().__init__()
        self.service = service
        self.circuit_breaker = circuit_breakers[service]
        self.url = urls[service]
        self.timeout = timeout
        self.mount(self.url, HTTPAdapter(max_retries=max_retries))

    def _request(self, method, *args, **kwargs):
        result = None

        try:
            request = self.circuit_breaker.call(method, self.url, **kwargs)
        except ConnectionError:
            c.incr('circuitbreaker.{}.connection_error'.format(self.service))
        except pybreaker.CircuitBreakerError:
            c.incr('circuitbreaker.{}.breaker_open'.format(self.service))
        except Exception:
            c.incr('circuitbreaker.{}.error'.format(self.service))
        else:
            if request.status_code == requests.codes.ok:
                result = request

        return result

    def get(self, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        self._request(super().get, **kwargs)

    def post(self, data=None, json=None, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return self._request(super().post, self.url, data, json, **kwargs)

    def delete(self, url, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return self._request(super().delete, self.url, **kwargs)
