#!/usr/bin/env python
# encoding: utf-8
import uuid

import falcon
from falcon.testing import TestCase

from recommendations import RecommendationsResource


class MockPermissionsMiddleware:
    """A mock version of PermissionsMiddleware.

    This middleware adds the context variables 'auth_header' and 'user_details'
    as if the permissions check succeeded.
    """
    def process_request(self, req, resp):
        req.context['auth_header'] = {'Authorization': '1234'}
        req.context['user_details'] = {
            'uuid': str(uuid.uuid4()),
            'permissions': ['can_view_recommendations', 'can_view_homepage']
        }


class TestRecommendations(TestCase):
    def setUp(self):
        super().setUp()
        self.api = falcon.API(middleware=[
            MockPermissionsMiddleware()
        ])
        self.api.add_route('/recommendations', RecommendationsResource())

    def test_get_returns_expected_data(self):
        resp = self.simulate_get('/recommendations')
        assert 200 == resp.status_code
        assert [12, 23, 100, 122, 220, 333, 340, 400, 555, 654] == resp.json
