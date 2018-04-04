# -*- coding: utf-8 -*-
"""A metrics plugin to do get gitinfo."""
from __future__ import unicode_literals, print_function
import sys

from pygments.token import Token

from metrics.metricbase import MetricBase


def get_file_processors():
    """plugin mechanism for file based metrics."""
    return []


def get_build_processors():
    """plugin mechanism for build based metrics."""
    return [GitMetric]


class GitMetric(MetricBase):
    """Compute the position of functions and methods for the whole source file."""
    def __init__(self, context):
        self.name = 'gitinfo'
        self._context = context
        self.reset()

    def reset(self):
        """Reset metric counter."""
        pass

    #def process_token(self, tok):
    #    """"""
    #    pass

    def get_metrics(self):
        return {'foo': 'bar'}

    metrics = property(get_metrics)
