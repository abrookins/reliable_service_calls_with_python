#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase, mock
from requests.exceptions import ConnectionError, Timeout

import apiclient
from jittery_retry import JitteryRetry


def mock_200_response(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse([1, 2, 3], 200)


def mock_connection_error(*args, **kwargs):
    raise ConnectionError()


def mock_timeout(*args, **kwargs):
    raise Timeout()


def mock_runtime_error(*args, **kwargs):
    raise RuntimeError()


class TestApiClient(TestCase):
    def setUp(self):
        self.client = apiclient.ApiClient('recommendations')

    def tearDown(self):
        self.client.circuit_breaker.close()

    def test_default_max_retries(self):
        max_retries = self.client.adapters['http://recommendations:8002/recommendations'].max_retries
        expected_max_retries = 1
        assert expected_max_retries == max_retries.total

    def test_uses_jittery_retry(self):
        max_retries = self.client.adapters['http://recommendations:8002/recommendations'].max_retries
        assert isinstance(max_retries, JitteryRetry)

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
        apiclient.ApiClient('recommendations').get()
        mock_get.assert_called_with('http://recommendations:8002/recommendations', timeout=1)

    @mock.patch('requests.Session.get', side_effect=mock_200_response)
    def test_get_uses_provided_timeout(self, mock_get):
        apiclient.ApiClient('recommendations', timeout=5).get()
        mock_get.assert_called_with('http://recommendations:8002/recommendations', timeout=5)

    @mock.patch('requests.Session.post', side_effect=mock_200_response)
    def test_post_uses_default_timeout(self, mock_post):
        apiclient.ApiClient('recommendations').post()
        mock_post.assert_called_with('http://recommendations:8002/recommendations', timeout=1)

    @mock.patch('requests.Session.post', side_effect=mock_200_response)
    def test_post_uses_provided_timeout(self, mock_post):
        apiclient.ApiClient('recommendations', timeout=5).post()
        mock_post.assert_called_with('http://recommendations:8002/recommendations', timeout=5)

    @mock.patch('requests.Session.delete', side_effect=mock_200_response)
    def test_delete_uses_default_timeout(self, mock_post):
        apiclient.ApiClient('recommendations').delete()
        mock_post.assert_called_with('http://recommendations:8002/recommendations', timeout=1)

    @mock.patch('requests.Session.delete', side_effect=mock_200_response)
    def test_delete_uses_provided_timeout(self, mock_post):
        apiclient.ApiClient('recommendations', timeout=5).delete()
        mock_post.assert_called_with('http://recommendations:8002/recommendations', timeout=5)
