#!/usr/bin/env python
# encoding: utf-8
from unittest import mock
from falcon.testing import TestCase

from simulation import api_client
from simulation.default_settings import DEFAULT_SETTINGS
from simulation.jittery_retry import RetryWithFullJitter
from simulation.settings import SettingsResource
from simulation.redis_helpers import redis_client
from . import (
    mock_200_response,
    mock_connection_error,
    mock_runtime_error,
    mock_timeout
)

redis = redis_client()


class TestApiClient(TestCase):
    def setUp(self):
        super().setUp()
        self.client = api_client.ApiClient('recommendations')
        self.api.add_route('/settings', SettingsResource())
        redis.flushdb()

    def tearDown(self):
        self.client.circuit_breaker.close()

    def test_with_max_retries(self):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(retries=True)
        client = api_client.ApiClient('recommendations', settings, max_retries=1)
        max_retries = client.adapters['http://recommendations:8002/recommendations'].max_retries
        expected_max_retries = 1
        assert expected_max_retries == max_retries.total

    def test_uses_jittery_retry(self):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(retries=True)
        client = api_client.ApiClient('recommendations', settings, max_retries=1)
        max_retries = client.adapters['http://recommendations:8002/recommendations'].max_retries
        assert isinstance(max_retries, RetryWithFullJitter)

    @mock.patch('requests.Session.get', side_effect=mock_connection_error)
    def test_circuit_breaker_tracks_connection_error(self, mock_get):
        assert self.client.circuit_breaker.fail_counter == 0
        self.client.get()
        assert self.client.circuit_breaker.fail_counter == 1

    @mock.patch('requests.Session.get', side_effect=mock_timeout)
    def test_circuit_breaker_tracks_timeout(self, mock_get):
        assert self.client.circuit_breaker.fail_counter == 0
        self.client.get()
        assert self.client.circuit_breaker.fail_counter == 1
        self.client.circuit_breaker.close()

    @mock.patch('requests.Session.get', side_effect=mock_runtime_error)
    def test_circuit_breaker_tracks_unexpected_error(self, mock_get):
        assert self.client.circuit_breaker.fail_counter == 0
        self.client.get()
        assert self.client.circuit_breaker.fail_counter == 1
        self.client.circuit_breaker.close()

    @mock.patch('requests.Session.get', side_effect=mock_timeout)
    def test_opens_circuit_breaker_after_reaching_max_error_count(self, mock_get):
        assert self.client.circuit_breaker.fail_counter == 0
        assert self.client.circuit_breaker.current_state == 'closed'
        assert self.client.circuit_breaker.fail_max == 5

        for x in range(5):
            self.client.get()

        assert self.client.circuit_breaker.fail_counter == 5
        assert self.client.circuit_breaker.current_state == 'open'
        self.client.circuit_breaker.close()

    @mock.patch('requests.Session.get', side_effect=mock_200_response)
    def test_get_uses_default_timeout(self, mock_get):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeouts=True)
        api_client.ApiClient('recommendations', settings).get()
        mock_get.assert_called_with('http://recommendations:8002/recommendations', timeout=1)

    @mock.patch('requests.Session.get', side_effect=mock_200_response)
    def test_get_uses_provided_timeout(self, mock_get):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeouts=True)
        api_client.ApiClient('recommendations', settings, timeout=5).get()
        mock_get.assert_called_with('http://recommendations:8002/recommendations', timeout=5)

    @mock.patch('requests.Session.post', side_effect=mock_200_response)
    def test_post_uses_default_timeout(self, mock_post):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeouts=True)
        api_client.ApiClient('recommendations', settings).post()
        mock_post.assert_called_with('http://recommendations:8002/recommendations', None, None,
                                     timeout=1)

    @mock.patch('requests.Session.post', side_effect=mock_200_response)
    def test_post_uses_provided_timeout(self, mock_post):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeouts=True)
        api_client.ApiClient('recommendations', settings, timeout=5).post()
        mock_post.assert_called_with('http://recommendations:8002/recommendations', None, None,
                                     timeout=5)

    @mock.patch('requests.Session.delete', side_effect=mock_200_response)
    def test_delete_uses_default_timeout(self, mock_post):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeouts=True)
        api_client.ApiClient('recommendations', settings).delete()
        mock_post.assert_called_with('http://recommendations:8002/recommendations', timeout=1)

    @mock.patch('requests.Session.delete', side_effect=mock_200_response)
    def test_delete_uses_provided_timeout(self, mock_post):
        settings = DEFAULT_SETTINGS.copy()
        settings.update(timeouts=True)
        api_client.ApiClient('recommendations', settings, timeout=5).delete()
        mock_post.assert_called_with('http://recommendations:8002/recommendations', timeout=5)

    @mock.patch('requests.Session.get', side_effect=mock_200_response)
    def test_timeouts_disabled_by_settings(self, mock_get):
        self.simulate_put('/settings', body='{"timeouts": false}')
        api_client.ApiClient('recommendations').get()
        mock_get.assert_called_with('http://recommendations:8002/recommendations', timeout=0)
