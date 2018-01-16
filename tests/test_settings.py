#!/usr/bin/env python
# encoding: utf-8
from unittest import mock

import json
import redis
from falcon.testing import TestCase

from settings import SettingsResource


r = redis.StrictRedis(host="redis", port=6379, db=0)


class TestSettingsResource(TestCase):
    def setUp(self):
        super().setUp()
        self.api.add_route('/settings', SettingsResource())
        r.flushdb()

    def test_sending_bad_json(self):
        resp = self.simulate_put('/settings', body='boo')
        assert 400 == resp.status_code

    def test_adds_a_new_setting(self):
        data = {'outages': ['recommendations']}
        resp = self.simulate_put('/settings', body=json.dumps(data))
        assert data == resp.json
        assert r.smembers('outages') == {b'recommendations'}

    def test_replaces_existing_settings(self):
        # Set initial settings
        self.simulate_put('/settings', body=json.dumps({
            'outages': ['homepage']
        }))
        # Overwrite initial settings
        resp = self.simulate_put('/settings', body=json.dumps({
            'outages': ['recommendations']
        }))

        expected = {'outages': ['recommendations']}
        assert expected == resp.json
        assert r.smembers('outages') == {b'recommendations'}
