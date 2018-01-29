#!/usr/bin/env python
# encoding: utf-8
import uuid
from unittest import mock

import falcon
from falcon.testing import TestCase

from simulation.recommendations import RecommendationsResource
from simulation.tests import (
    mock_200_response
)


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

    @mock.patch('requests.Session.post', side_effect=mock_200_response)
    def test_get_returns_expected_data(self, mock_post):
        resp = self.simulate_get('/recommendations')
        assert resp.status_code == 200
        assert resp.json == [12, 23, 100, 122, 220, 333, 340, 400, 555, 654]
