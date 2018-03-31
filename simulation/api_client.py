#!/usr/bin/env python
# encoding: utf-8
import logging
import pybreaker
import requests
import statsd

from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout
from urllib.parse import urlparse

from .jittery_retry import RetryWithFullJitter
from .redis_helpers import redis_client
from .settings import OUTAGES_KEY
from .settings_helpers import get_client_settings

log = logging.getLogger(__name__)
metrics = statsd.StatsClient('telegraf')
redis = redis_client()


class ApiClient(requests.Session):
    """A base class for API clients.
    
    Following the API Gateway pattern, this class collects common error-
    handling code useful to API clients, and guards connections with a 
    circuit breaker that will open after five failures.

    For the purposes of an outage simulation, this class also provides
    a way for the Settings API to change the operation of all sub-classes
    at run-time.
    """
    def __init__(self, settings=None, timeout=1, max_retries=3):
        super().__init__()

        if not settings:
            settings = get_client_settings()

        self.settings = settings
        self.timeout = timeout

        if not getattr(self, 'circuit_breaker', None):
            self.circuit_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)

        if self.settings['retries']:
            if max_retries:
                adapter = HTTPAdapter(max_retries=RetryWithFullJitter(total=max_retries))
                self.mount(self.url, adapter)

        if self.settings['timeout']:
            self.settings['timeout'] = int(self.settings['timeout'])

    @property
    def url(self):
        raise NotImplementedError

    def _request(self, method, url, *args, **kwargs):
        use_circuit_breakers = self.settings['circuit_breakers']
        path = urlparse(url).path
        simulate_outage = path in redis.smembers(OUTAGES_KEY)
        kwargs['timeout'] = self.settings['timeout'] or kwargs.get('timeout') or self.timeout
        result = None

        if simulate_outage:
            def erroring_method(*args, **kwargs):
                raise ConnectionError
            method = erroring_method

        try:
            if use_circuit_breakers:
                result = self.circuit_breaker.call(method, url, *args, **kwargs)
            else:
                result = method(url, *args, **kwargs)
        except ConnectionError:
            log.error('Connection error connecting to %s', self.url)
            metrics.incr('{}.connection_error'.format(path))
        except Timeout:
            log.error('Timeout connecting to %s', self.url)
            metrics.incr('{}.timeout'.format(path))
        except pybreaker.CircuitBreakerError as e:
            log.error('Circuit breaker error: %s', e)
            metrics.incr('circuitbreaker.{}_breaker_open'.format(path))
        except Exception:
            log.exception('Unexpected error connecting to: %s', self.url)
            metrics.incr('{}.error'.format(path))

        return result

    def get(self, **kwargs):
        return self._request(super().get, self.url, **kwargs)

    def post(self, data=None, json=None, **kwargs):
        return self._request(super().post, self.url, data, json, **kwargs)

    def delete(self, **kwargs):
        return self._request(super().delete, self.url, **kwargs)
