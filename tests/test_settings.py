#!/usr/bin/env python
# encoding: utf-8
from unittest import mock

import json
from falcon.testing import TestCase

from settings import SettingsResource


class TestSettingsResource(TestCase):
    def setUp(self):
        super().setUp()
        self.api.add_route('/settings', SettingsResource())

    def test_sending_bad_json(self):
        resp = self.simulate_put('/settings', body='boo')
        assert 400 == resp.status_code

    @mock.patch('redis.StrictRedis.get')
    @mock.patch('redis.StrictRedis.set')
    def test_adds_a_new_setting(self, mock_redis_set, mock_redis_get):
        mock_redis_get.return_value = {}
        data = {'outages': {'recommendations': True}}
        resp = self.simulate_put('/settings', body=json.dumps(data))
        assert mock_redis_get.called_with('settings')
        assert mock_redis_set.called_with('settings', data)
        assert data == resp.json

    @mock.patch('redis.StrictRedis.get')
    @mock.patch('redis.StrictRedis.set')
    def test_replaces_existing_settings(self, mock_redis_set, mock_redis_get):
        mock_redis_get.return_value = {'outages': {'homepage': True}}
        data = {'outages': {'recommendations': True}}
        resp = self.simulate_put('/settings', body=json.dumps(data))

        expected = {
            'outages': {
                'recommendations': True
            }
        }

        assert mock_redis_get.called_with('settings')
        assert mock_redis_set.called_with('settings', data)
        assert expected == resp.json
