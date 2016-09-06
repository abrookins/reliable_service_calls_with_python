#!/usr/bin/env python
# encoding: utf-8
from unittest import mock
from falcon.testing import TestCase

from homepage import HomepageResource
from . import MockResponse


def mock_200_responses(*args, **kwargs):
    if args[0] == 'http://recommendations:8002/recommendations':
        return MockResponse([1, 2, 3], 200)
    elif args[0] == 'http://popular:8003/popular_items':
        return MockResponse([4, 5, 6], 200)
    else:
        return MockResponse({"error": "Resource not found"}, 404)


class TestAuthentication(TestCase):
    def setUp(self):
        super().setUp()
        self.api.add_route('/home', HomepageResource())

    @mock.patch('requests.Session.get', side_effect=mock_200_responses)
    def test_get_returns_expected_data(self, mock_get):
        resp = self.simulate_get('/home')
        expected_data = {
            'recommendations': [1, 2, 3],
            'popular_items': [4, 5, 6]
        }
        assert 200 == resp.status_code
        assert expected_data == resp.json
