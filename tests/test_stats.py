#!/usr/bin/env python
# encoding: utf-8
import redis

from unittest import mock
from falcon.testing import TestCase

from stats import StatsResource


r = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)



class TestStatsResource(TestCase):
    def setUp(self):
        super().setUp()
        self.api.add_route('/stats', StatsResource())
        r.flushdb()

    def test_returns_stats(self):
        r.hincrby('stats', 'recommendations.get')
        r.hincrby('stats', 'homepage.get')

        resp = self.simulate_get('/stats')
        assert 200 == resp.status_code
        assert {
            'stats': {
                'recommendations.get': 1,
                'homepage.get': 1
            }
        } == resp.json

    def test_deletes_stats(self):
        r.hincrby('stats', 'recommendations.get')
        r.hincrby('stats', 'homepage.get')

        resp = self.simulate_delete('/stats')

        assert 200 == resp.status_code
        assert None == r.hget('stats', 'recommendations.get')
