#!/usr/bin/env python
# encoding: utf-8
from unittest import mock

import pybreaker

from falcon.testing import TestCase

from simulation import api_client
from simulation.default_settings import DEFAULT_SETTINGS
from simulation.jittery_retry import RetryWithFullJitter
from simulation.settings import SettingsResource
from simulation.redis_helpers import redis_client
from simulation.settings_helpers import get_client_settings
from . import (
    mock_200_response,
    mock_connection_error,
    mock_runtime_error,
    mock_timeout
)

redis = redis_client()


class FakeApiClient(api_client.ApiClient):
    url = "http://example.com"
    circuit_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)


class TestApiClient(TestCase):
    def setUp(self):
        super().setUp()
        self.client = FakeApiClient()
        self.api.add_route('/settings', SettingsResource())
        redis.flushdb()

    def tearDown(self):
        self.client.circuit_breaker.close()

    def test_with_max_retries(self):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(retries=True)
        client = FakeApiClient(settings, max_retries=1)
        max_retries = client.adapters['http://example.com'].max_retries
        expected_max_retries = 1
        assert expected_max_retries == max_retries.total

    def test_uses_jittery_retry(self):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(retries=True)
        client = FakeApiClient(settings, max_retries=1)
        max_retries = client.adapters['http://example.com'].max_retries
        assert isinstance(max_retries, RetryWithFullJitter)

    @mock.patch('requests.Session.get', side_effect=mock_connection_error)
    def test_uses_circuit_breaker(self, mock_get):
        assert self.client.circuit_breaker.fail_counter == 0
        self.client.get()
        assert self.client.circuit_breaker.fail_counter == 1

    @mock.patch('requests.Session.get', side_effect=mock_200_response)
    def test_get_uses_default_timeout(self, mock_get):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeout=None)
        FakeApiClient(settings).get()
        mock_get.assert_called_with('http://example.com', timeout=1)

    @mock.patch('requests.Session.get', side_effect=mock_200_response)
    def test_get_uses_provided_timeout(self, mock_get):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeout=5)
        FakeApiClient(settings).get()
        mock_get.assert_called_with('http://example.com', timeout=5)

    @mock.patch('requests.Session.post', side_effect=mock_200_response)
    def test_post_uses_default_timeout(self, mock_post):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeout=None)
        FakeApiClient(settings).post()
        mock_post.assert_called_with('http://example.com', None, None,
                                     timeout=1)

    @mock.patch('requests.Session.post', side_effect=mock_200_response)
    def test_post_uses_provided_timeout(self, mock_post):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeout=5)
        FakeApiClient(settings).post()
        mock_post.assert_called_with('http://example.com', None, None,
                                     timeout=5)

    @mock.patch('requests.Session.delete', side_effect=mock_200_response)
    def test_delete_uses_default_timeout(self, mock_post):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeout=None)
        FakeApiClient(settings).delete()
        mock_post.assert_called_with('http://example.com', timeout=1)

    @mock.patch('requests.Session.delete', side_effect=mock_200_response)
    def test_delete_uses_provided_timeout(self, mock_post):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeout=5)
        FakeApiClient(settings).delete()
        mock_post.assert_called_with('http://example.com', timeout=5)

    @mock.patch('requests.Session.get', side_effect=mock_200_response)
    def test_timeouts_changed_by_settings(self, mock_get):
        self.simulate_put('/settings', body='{"timeout": 10}')
        settings = get_client_settings()
        FakeApiClient(settings).get()
        mock_get.assert_called_with('http://example.com', timeout=10)
