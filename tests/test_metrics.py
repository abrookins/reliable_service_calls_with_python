#!/usr/bin/env python
# encoding: utf-8
import redis

from unittest import mock
from falcon.testing import TestCase

from metrics import MetricsResource


r = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


class TestmetricsResource(TestCase):
    def setUp(self):
        super().setUp()
        self.api.add_route('/metrics', MetricsResource())
        r.flushdb()

    def test_returns_metrics(self):
        self.simulate_post('/metrics', body='recommendations.get')
        self.simulate_post('/metrics', body='homepage.get')

        resp = self.simulate_get('/metrics')
        assert resp.status_code == 200
        assert r.zrange('metrics', 0, -1) == [
            'recommendations.get',
            'homepage.get'
        ]

    def test_post_creates_metric(self):
        self.simulate_post('/metrics', body='recommendations.get')
        assert r.zrange('metrics', 0, -1) == [
            'recommendations.get',
        ]

    def test_deletes_metrics(self):
        self.simulate_post('/metrics', body='recommendations.get')
        self.simulate_post('/metrics', body='homepage.get')

        resp = self.simulate_delete('/metrics')

        assert resp.status_code == 200
        assert not r.zrange('metrics', 0, -1)
