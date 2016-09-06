#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase

from requests.packages.urllib3.exceptions import ProtocolError

from jittery_retry import JitteryRetry


class TestJitteryRetry(TestCase):

    def _retry(self, retry, times, error):
        for _ in range(times):
            retry = retry.increment(error=error())
        return retry

    def test_backoff_defaults_to_zero(self):
        retry = JitteryRetry(total=3)
        assert retry.get_backoff_time() == 0

    def test_backoff_is_nonzero_after_an_error(self):
        retry = self._retry(JitteryRetry(total=3, backoff_factor=1),
                            times=2, error=ProtocolError)
        backoff = retry.get_backoff_time()

        assert backoff > 0

    def test_backoff_changes_on_every_call(self):
        retry = self._retry(JitteryRetry(total=3, backoff_factor=1),
                            times=2, error=ProtocolError)
        backoff1 = retry.get_backoff_time()
        backoff2 = retry.get_backoff_time()

        assert backoff1 != backoff2

