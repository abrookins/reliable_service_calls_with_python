#!/usr/bin/env python
# encoding: utf-8
import apiclient
import falcon
import redis

from falcon.testing import TestCase, SimpleTestResource
from middleware import FuzzingMiddleware, PermissionsMiddleware
from requests.exceptions import Timeout
from unittest import mock
from . import MockResponse


r = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


class TestFuzzingMiddleware(TestCase):
    def setUp(self):
        super().setUp()
        self.api = falcon.API(middleware=[
            FuzzingMiddleware()
        ])
        self.url = '/recommendations'
        self.api.add_route(self.url, SimpleTestResource())
        r.flushdb()

    @mock.patch('time.sleep')
    def test_when_outage_value_does_not_exist(self, mock_sleep):
        self.simulate_get(self.url)
        assert not mock_sleep.called

    @mock.patch('time.sleep')
    def test_when_outage_value_is_true(self, mock_sleep):
        r.sadd('outages', '/recommendations')
        self.simulate_get(self.url)
        assert mock_sleep.called


def mock_timeout_response(*args, **kwargs):
    raise Timeout()


def mock_401_response(*args, **kwargs):
    return MockResponse({"error": "Authorization failed"}, 401)


def mock_missing_permission_response(*args, **kwargs):
    return MockResponse({'permissions': ['can_have_waffles']}, 200)


def mock_correct_permission_response(*args, **kwargs):
    return MockResponse({'permissions': ['can_have_pancakes']}, 200)


class TestPermissionMiddleware(TestCase):
    def setUp(self):
        super().setUp()
        self.api = falcon.API(middleware=[
            PermissionsMiddleware('can_have_pancakes')
        ])
        self.api.add_route('/', SimpleTestResource())

    def tearDown(self):
        apiclient.circuit_breakers['authentication'].close()

    def test_requires_auth_token(self):
        resp = self.simulate_get('/')
        expected_status_code = 401
        assert expected_status_code == resp.status_code

    @mock.patch('requests.Session.post', side_effect=mock_timeout_response)
    def test_auth_request_failed(self, mock_post):
        resp = self.simulate_get('/', headers={'Authorization': '1234'})
        expected_status_code = 500
        assert expected_status_code == resp.status_code

    @mock.patch('requests.Session.post', side_effect=mock_401_response)
    def test_auth_returned_401(self, mock_post):
        resp = self.simulate_get('/', headers={'Authorization': '1234'})
        expected_status_code = 401
        assert expected_status_code == resp.status_code

    @mock.patch('requests.Session.post', side_effect=mock_missing_permission_response)
    def test_missing_required_permission(self, mock_post):
        resp = self.simulate_get('/', headers={'Authorization': '1234'})
        expected_status_code = 403
        assert expected_status_code == resp.status_code

    @mock.patch('requests.Session.post', side_effect=mock_correct_permission_response)
    def test_has_correct_permission(self, mock_post):
        resp = self.simulate_get('/', headers={'Authorization': '1234'})
        expected_status_code = 200
        assert expected_status_code == resp.status_code
