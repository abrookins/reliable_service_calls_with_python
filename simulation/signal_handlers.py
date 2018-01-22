#!/usr/bin/env python
# encoding: utf-8
from .signals import publish_metric
from .apiclient import ApiClient


metrics = ApiClient('metrics')

import logging
log = logging.getLogger(__name__)

@publish_metric.connect
def metric_subscriber(key):
    """Send published metrics to the Metrics service."""

    log.debug("Sending metrics key: {}".format(key))

    # Avoid recursion problems by skipping metrics service failures.
    # In a real system, you'll want to use a dedicated stats/metrics
    # library, probably the one provided by your monitoring service.
    if 'metrics.' in key:
        return

    metrics.post(key)
