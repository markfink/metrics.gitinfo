# -*- coding: utf-8 -*-
"""extract info per file"""


def get_file_info(repo, path):
    """we need change_count, last_change, nbr_committers."""
    committers = []
    last_change = None
    nbr_changes = 0

    for commit in repo.iter_commits(paths=path):
        #print(dir(commit))
        committers.append(commit.committer)
        last_change = commit.committed_date
        nbr_changes += 1

    return nbr_changes, last_change, len(set(committers))
