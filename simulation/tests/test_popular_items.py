#!/usr/bin/env python
# encoding: utf-8
from unittest import mock

from falcon.testing import TestCase

from simulation.popular_items import PopularItemsResource
from simulation.tests import mock_200_response


class TestPopularItems(TestCase):

    def setUp(self):
        super().setUp()
        self.api.add_route('/popular_items', PopularItemsResource())

    @mock.patch('requests.Session.post', side_effect=mock_200_response)
    def test_get_returns_expected_data(self, mock_post):
        resp = self.simulate_get('/popular_items')
        assert 200 == resp.status_code
        assert [1, 2, 3, 4, 5, 6, 7, 8 , 9, 10] == resp.json
