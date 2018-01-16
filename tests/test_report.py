#!/usr/bin/env python
# encoding: utf-8

from unittest import mock

from falcon.testing import TestCase

from report import ReportResource


class TestReportResource(TestCase):
    def setUp(self):
        super().setUp()
        self.api.add_route('/report', ReportResource())

    @mock.patch('redis.StrictRedis.keys')
    @mock.patch('redis.StrictRedis.get')
    def test_returns_report(self, mock_redis_get, mock_redis_keys):
        keys = [
            'stats.recommendations.get',
            'stats.homepage.get'
        ]
        mock_redis_keys.return_value = keys
        mock_redis_get.return_value = 1

        resp = self.simulate_get('/report')
        assert 200 == resp.status_code
        assert {'report': {key: 1 for key in keys}} == resp.json
