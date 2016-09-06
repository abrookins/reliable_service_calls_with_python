#!/usr/bin/env python
# encoding: utf-8
from unittest import mock

from falcon.testing import TestCase

from outage import OutageResource


class TestPermissionMiddleware(TestCase):
    def setUp(self):
        super().setUp()
        self.api.add_route('/outage/{service}', OutageResource())

    @mock.patch('redis.StrictRedis.get')
    def test_404_without_service_name(self, mock_redis_get):
        resp = self.simulate_post('/outage/')
        assert 404 == resp.status_code

    @mock.patch('redis.StrictRedis.get')
    def test_404_with_invalid_service_name(self, mock_redis_get):
        resp = self.simulate_post('/outage/ballads')
        assert 404 == resp.status_code

    @mock.patch('redis.StrictRedis.get')
    @mock.patch('redis.StrictRedis.set')
    def test_sets_false_if_true(self, mock_redis_set, mock_redis_get):
        mock_redis_get.return_value = b'true'
        resp = self.simulate_post('/outage/popular')
        assert mock_redis_get.called_with('/popular')
        assert mock_redis_set.called_with('/popular', b'false')
        assert {'outage': 'false'} == resp.json

    @mock.patch('redis.StrictRedis.get')
    @mock.patch('redis.StrictRedis.set')
    def test_sets_true_if_false(self, mock_redis_set, mock_redis_get):
        mock_redis_get.return_value = b'false'
        resp = self.simulate_post('/outage/popular')
        assert mock_redis_get.called_with('/popular')
        assert mock_redis_set.called_with('/popular', b'true')
        assert {'outage': 'true'} == resp.json
