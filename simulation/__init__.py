#!/usr/bin/env python
# encoding: utf-8
import logging
import sys


# This package initializer ensures that all of our Falcon
# apps can publish and process signals.
from .signal_handlers import metric_subscriber


# Configure cross-app logging settings.
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
