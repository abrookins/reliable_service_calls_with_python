#!/usr/bin/env python
# encoding: utf-8
import logging
import pybreaker
import requests
import statsd

from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout

from .default_settings import DEFAULT_SETTINGS
from .jittery_retry import RetryWithFullJitter

log = logging.getLogger(__name__)
metrics = statsd.StatsClient('telegraf')

urls = {
    'authentication': 'http://authentication:8000/authenticate',
    'recommendations': 'http://recommendations:8002/recommendations',
    'popular': 'http://popular:8003/popular_items',
    'settings': 'http://settings:8004/settings',
}

circuit_breakers = {
    'authentication': pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30),
    'recommendations': pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30),
    'popular': pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30),
    'settings': pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30),
}


class ApiClient(requests.Session):
    def __init__(self, service, settings=None, timeout=1, max_retries=None):
        super().__init__()
        self.settings = settings if settings else DEFAULT_SETTINGS.copy()
        self.service = service
        self.circuit_breaker = circuit_breakers[service]
        self.url = urls[service]
        self.timeout = timeout

        if self.settings['retries']:
            if max_retries:
                adapter = HTTPAdapter(max_retries=RetryWithFullJitter(total=max_retries))
                self.mount(self.url, adapter)

        if self.settings['timeout']:
            self.settings['timeout'] = int(self.settings['timeout'])

    def _request(self, method, *args, **kwargs):
        timeout_from_settings = self.settings['timeout']
        use_circuit_breakers = self.settings['circuit_breakers']
        kwargs['timeout'] = self.settings['timeout'] or kwargs.get('timeout') or self.timeout

        if use_circuit_breakers:
            result = self._request_with_circuit_breaker(method, *args, **kwargs)
        else:
            result = method(*args, **kwargs)

        return result

    def _request_with_circuit_breaker(self, method, *args, **kwargs):
        result = None

        try:
            result = self.circuit_breaker.call(method, *args, **kwargs)
        except ConnectionError:
            log.error('Connection error connecting to %s', self.url)
            metrics.incr('circuitbreaker.{}.connection_error'.format(self.service))
        except Timeout:
            log.error('Timeout connecting to %s', self.url)
            metrics.incr('circuitbreaker.{}.timeout'.format(self.service))
        except pybreaker.CircuitBreakerError as e:
            log.error('Circuit breaker error: %s', e)
            metrics.incr('circuitbreaker.{}.breaker_open'.format(self.service))
        except Exception:
            log.exception('Unexpected error connecting to: %s', self.url)
            metrics.incr('circuitbreaker.{}.error'.format(self.service))

        return result

    def get(self, **kwargs):
        return self._request(super().get, self.url, **kwargs)

    def post(self, data=None, json=None, **kwargs):
        return self._request(super().post, self.url, data, json, **kwargs)

    def delete(self, **kwargs):
        return self._request(super().delete, self.url, **kwargs)