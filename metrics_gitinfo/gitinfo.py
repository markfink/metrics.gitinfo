# -*- coding: utf-8 -*-
"""A metrics plugin to do extract gitinfo."""
from __future__ import unicode_literals, print_function

from metrics.metricbase import MetricBase
from git import Repo

from .git_diff_muncher import parse_diff_lines


def get_file_processors():
    """plugin mechanism for file based metrics."""
    return [GitMetric]


def get_build_processors():
    """plugin mechanism for build based metrics."""
    return [GitMetric]


'''
print (target.committer)
print (target.committed_datetime)
print (target.hexsha)
print (target.summary)
'''


class GitMetric(MetricBase):
    """Extract file changes and build information from git."""
    def __init__(self, context):
        self.name = 'gitinfo'
        self._context = context
        self.reset()

    def _extract_info(self):
        repo = Repo('.')
        # TODO get source sha from last run
        source_sha = '0f3ea5dbafef04f5f79a4e7b0fbd7c6d12333a4b'
        source = repo.commit(source_sha)
        # get last commit
        #target = repo.commit(target_sha)
        target = repo.head.commit

        changed_files = {}
        build_metrics = {}

        for x in target.diff(source, create_patch=True):
            added, deleted = parse_diff_lines(x.diff)
            changed_files[x.b_path] = {'lines_added': added, 'lines_deleted': deleted}

        # TODO author etc.
        return changed_files, build_metrics

    def reset(self):
        """Reset metrics."""
        self._changed_files, self._build_metrics = self._extract_info()
        self._metrics = {}

    def process_file(self, language, key, token_list):
        """extract line changes in git for a given key"""
        print(key)
        if key in self._changed_files:
            self._metrics = self._changed_files[key]
        else:
            self._metrics = {}

    def get_metrics(self):
        return self._metrics

    def get_build_metrics(self):
        return self._build_metrics

    metrics = property(get_metrics)
    build_metrics = property(get_build_metrics)
