#!/usr/bin/env python
# encoding: utf-8
from falcon.testing import TestCase

from popular_items import PopularItemsResource


class TestPopularItems(TestCase):

    def setUp(self):
        super().setUp()
        self.api.add_route('/popular_items', PopularItemsResource())

    def test_get_returns_expected_data(self):
        resp = self.simulate_get('/popular_items')
        assert 200 == resp.status_code
        assert [1, 2, 3, 4, 5, 6, 7, 8 , 9, 10] == resp.json
