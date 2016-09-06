#!/usr/bin/env python
# encoding: utf-8
import logging
import pybreaker
import requests
import statsd
import sys

from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout

from jittery_retry import JitteryRetry


c = statsd.StatsClient('graphite', 8125)
log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


urls = {
    'authentication': 'http://authentication:8000/authenticate',
    'recommendations': 'http://recommendations:8002/recommendations',
    'popular': 'http://popular:8003/popular_items'
}

circuit_breakers = {
   'authentication': pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30),
   'recommendations': pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30),
   'popular': pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)
}


class ApiClient(requests.Session):
    def __init__(self, service, max_retries=1, timeout=1):
        super().__init__()
        self.service = service
        self.circuit_breaker = circuit_breakers[service]
        self.url = urls[service]
        self.timeout = timeout

        adapter = HTTPAdapter(max_retries=JitteryRetry(total=max_retries))
        self.mount(self.url, adapter)

    def _request(self, method, *args, **kwargs):
        result = None

        try:
            result = self.circuit_breaker.call(method, self.url, **kwargs)
        except ConnectionError:
            log.error('Connection error when trying {}'.format(self.url))
            c.incr('circuitbreaker.{}.connection_error'.format(self.service))
        except Timeout:
            log.error('Timeout when trying {}'.format(self.url))
            c.incr('circuitbreaker.{}.timeout'.format(self.service))
        except pybreaker.CircuitBreakerError as e:
            log.error(e)
            c.incr('circuitbreaker.{}.breaker_open'.format(self.service))
        except Exception:
            log.exception('Unexpected error connecting to: {}'.format(self.url))
            c.incr('circuitbreaker.{}.error'.format(self.service))

        return result

    def get(self, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return self._request(super().get, **kwargs)

    def post(self, data=None, json=None, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return self._request(super().post, self.url, data, json, **kwargs)

    def delete(self, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return self._request(super().delete, self.url, **kwargs)
