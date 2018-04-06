# -*- coding: utf-8 -*-
import os
import tempfile

import pytest

from metrics_gitinfo.gitinfo import GitMetric


@pytest.fixture
def tempfolder():
    """setup tempfolder and cd into it."""
    curr_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as temp:
        os.chdir(temp)
        yield
        os.chdir(curr_dir)


def test_metrics_gitinfo_no_git_repo(tempfolder):
    gm = GitMetric({})

    gm.reset()
    gm.process_file('Python', 'tests/test_pylint_metric.py', [])

    assert gm.metrics == {}
    assert gm.build_metrics == {}


def test_metrics_gitinfo(tempfolder):
    gm = GitMetric({})

    gm.reset()
    gm.process_file('Python', 'tests/test_pylint_metric.py', [])

    assert gm.metrics == {}
    assert gm.build_metrics == {}


def test_metrics_gitinfo_no_lastrun(tempfolder):
    gm = GitMetric({})

    gm.reset()
    gm.process_file('Python', 'tests/test_pylint_metric.py', [])

    assert gm.metrics == {}
    assert gm.build_metrics == {}