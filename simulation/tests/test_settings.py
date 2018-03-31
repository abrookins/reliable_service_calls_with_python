#!/usr/bin/env python
# encoding: utf-8
from unittest import mock

import json
from falcon.testing import TestCase

from simulation.settings import SettingsResource
from simulation.redis_helpers import redis_client
from simulation.default_settings import DEFAULT_SETTINGS


redis = redis_client()


class TestPutSettingsResource(TestCase):
    def setUp(self):
        super().setUp()
        self.api.add_route('/settings', SettingsResource())
        redis.flushdb()

    def test_sending_bad_json(self):
        resp = self.simulate_put('/settings', body='boo')
        assert resp.status_code == 400

    def test_adds_outages(self):
        data = {'outages': ['recommendations']}
        resp = self.simulate_put('/settings', body=json.dumps(data))
        assert resp.json == data
        assert redis.smembers('outages') == {'recommendations'}

    def test_clears_outages(self):
        data = {'outages': []}
        resp = self.simulate_put('/settings', body=json.dumps(data))
        assert resp.json == data
        assert redis.smembers('outages') == set()

    def test_replaces_existing_settings(self):
        self.simulate_patch('/settings', body=json.dumps({
            'timeout': 5
        }))
        # Overwrite initial settings
        resp = self.simulate_put('/settings', body=json.dumps({
            'timeout': 1
        }))

        expected = {'timeout': 1}
        assert resp.json == expected

    def test_sets_false_value(self):
        expected_settings = {
            'retries': False
        }

        data = {'retries': False}
        self.simulate_put('/settings', body=json.dumps(data))
        assert redis.hmget('settings', 'retries') == ['False']

        resp = self.simulate_get('/settings')
        assert resp.json == expected_settings

    def test_sets_true_value(self):
        expected_settings = {
            'retries': True
        }

        data = {'retries': True}
        self.simulate_put('/settings', body=json.dumps(data))
        assert redis.hmget('settings', 'retries') == ['True']

        resp = self.simulate_get('/settings')
        assert resp.json == expected_settings


class TestPatchSettingsResource(TestCase):
    def setUp(self):
        super().setUp()
        self.api.add_route('/settings', SettingsResource())
        redis.flushdb()

    def test_sending_bad_json(self):
        resp = self.simulate_patch('/settings', body='boo')
        assert resp.status_code == 400

    def test_adds_outages(self):
        data = {'outages': ['recommendations']}
        resp = self.simulate_patch('/settings', body=json.dumps(data))
        assert resp.json == data
        assert redis.smembers('outages') == {'recommendations'}

    def test_clears_outages(self):
        data = {'outages': []}
        resp = self.simulate_patch('/settings', body=json.dumps(data))
        assert resp.json == data
        assert redis.smembers('outages') == set()

    def test_replaces_existing_settings(self):
        # Set initial settings
        self.simulate_patch('/settings', body=json.dumps({
            'timeout': 5
        }))
        # Overwrite initial settings
        resp = self.simulate_patch('/settings', body=json.dumps({
            'timeout': 1
        }))

        expected = {'timeout': 1}
        assert resp.json == expected

    def test_sets_false_value(self):
        expected_settings = {
            'retries': False
        }

        data = {'retries': False}
        self.simulate_patch('/settings', body=json.dumps(data))
        assert redis.hmget('settings', 'retries') == ['False']

        resp = self.simulate_get('/settings')
        assert resp.json == expected_settings

    def test_sets_true_value(self):
        expected_settings = {
            'retries': True
        }

        data = {'retries': True}
        self.simulate_patch('/settings', body=json.dumps(data))
        assert redis.hmget('settings', 'retries') == ['True']

        resp = self.simulate_get('/settings')
        assert resp.json == expected_settings

