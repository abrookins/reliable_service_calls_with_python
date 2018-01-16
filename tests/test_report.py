#!/usr/bin/env python
# encoding: utf-8
import redis

from unittest import mock
from falcon.testing import TestCase

from report import ReportResource


r = redis.StrictRedis(host="redis", port=6379, db=0)


class TestReportResource(TestCase):
    def setUp(self):
        super().setUp()
        self.api.add_route('/report', ReportResource())
        r.flushdb()

    def test_returns_report(self):
        r.set('stats.recommendations.get', 1)
        r.set('stats.homepage.get', 1)

        resp = self.simulate_get('/report')
        assert 200 == resp.status_code
        assert {
            'report': {
                'stats.recommendations.get': 1,
                'stats.homepage.get': 1
            }
        } == resp.json
