#!/usr/bin/env python
# encoding: utf-8
from signals import metric_published
from apiclient import ApiClient


metrics = ApiClient('metrics')


@metric_published.connect
def metric_subscriber(key):
    metrics.post(key)

