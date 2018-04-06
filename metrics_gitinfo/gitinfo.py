# -*- coding: utf-8 -*-
"""A metrics plugin to do extract gitinfo."""
from __future__ import unicode_literals, print_function

from metrics.metricbase import MetricBase
from git import Repo
from git.exc import InvalidGitRepositoryError

from .git_diff_muncher import parse_diff_lines


def get_file_processors():
    """plugin mechanism for file based metrics."""
    return [GitMetric]


def get_build_processors():
    """plugin mechanism for build based metrics."""
    return [GitMetric]


class GitMetric(MetricBase):
    """Extract file changes and build information from git."""

    def __init__(self, context):
        self.name = 'gitinfo'
        self._context = context
        self.reset()

    def _get_commits_contained(self, repo, source, target):
        rev = '%s..%s' % (source.hexsha, target.hexsha)
        commits = repo.iter_commits(rev=rev)
        return commits

    def _get_source_target(self):
        repo = Repo('.')
        source = None
        target = repo.head.commit
        last_build_metrics = self._context.get(
            'last_metrics', {}).get('build', None)
        if last_build_metrics:
            if last_build_metrics['sha'] == target.hexsha and \
                            'sha_start' in last_build_metrics:
                # rerun metrics case
                source = repo.commit(last_build_metrics['sha_start'])
            else:
                # found new commit(s) - get sha from last run and use it as source
                source = repo.commit(last_build_metrics['sha'])
        return repo, source, target

    def _extract_info(self):
        try:
            repo, source, target = self._get_source_target()
        except InvalidGitRepositoryError:
            return [], {}

        changed_files = {}
        build_metrics = {
            'committers': [target.committer.name],
            'committed_datetime': target.committed_datetime.isoformat(),
            'committed_ts': target.committed_date,
            'sha': target.hexsha,
            'summary': target.summary,
        }

        if source:
            for x in target.diff(source, create_patch=True):
                added, deleted = parse_diff_lines(x.diff)
                changed_files[x.b_path] = {'lines_added': added,
                                           'lines_deleted': deleted}

            committers = list(set([
                c.committer.name for c in
                self._get_commits_contained(repo, source, target)
            ]))
            build_metrics['committers'] = committers
            build_metrics['sha_start'] = source.hexsha

        return changed_files, build_metrics

    def reset(self):
        """Reset metrics."""
        self._changed_files, self._build_metrics = self._extract_info()
        self._metrics = {}

    def process_file(self, language, key, token_list):
        """extract line changes in git for a given key"""
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
