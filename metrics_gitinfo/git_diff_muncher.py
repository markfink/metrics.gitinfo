# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import re

# here we use parts of https://github.com/Bachmann1234/diff-cover which uses a compatible apache 2.0 license
# to be precise the implementation of parse_diff_lines is reused from here:
# https://github.com/Bachmann1234/diff-cover/blob/34c9c4c0801137413e9b955f40649a5c2c2ec724/diff_cover/diff_reporter.py


class GitDiffError(Exception):
    """
    `git diff` command produced an error.
    """
    pass


HUNK_LINE_RE = re.compile(r'\+([0-9]*)')


def parse_diff_lines(diff_lines):
    """
    Given the diff lines output from `git diff` for a particular
    source file, return a tuple of `(ADDED_LINES, DELETED_LINES)`
    where `ADDED_LINES` and `DELETED_LINES` are lists of line
    numbers added/deleted respectively.
    Raises a `GitDiffError` if the diff lines are in an invalid format.
    """
    if isinstance(diff_lines, bytes):
        # in python3 the diff comes as bytes
        diff_lines = diff_lines.decode("utf-8")
    added_lines = []
    deleted_lines = []

    current_line_new = None
    current_line_old = None

    for line in diff_lines.split('\n'):
        # If this is the start of the hunk definition, retrieve
        # the starting line number
        if line.startswith('@@'):
            line_num = _parse_hunk_line(line)
            current_line_new, current_line_old = line_num, line_num

        # This is an added/modified line, so store the line number
        elif line.startswith('+'):

            # Since we parse for source file sections before
            # calling this method, we're guaranteed to have a source
            # file specified.  We check anyway just to be safe.
            if current_line_new is not None:

                # Store the added line
                added_lines.append(current_line_new)

                # Increment the line number in the file
                current_line_new += 1

        # This is a deleted line that does not exist in the final
        # version, so skip it
        elif line.startswith('-'):

            # Since we parse for source file sections before
            # calling this method, we're guaranteed to have a source
            # file specified.  We check anyway just to be safe.
            if current_line_old is not None:

                # Store the deleted line
                deleted_lines.append(current_line_old)

                # Increment the line number in the file
                current_line_old += 1

        # This is a line in the final version that was not modified.
        # Increment the line number, but do not store this as a changed
        # line.
        else:
            if current_line_old is not None:
                current_line_old += 1

            if current_line_new is not None:
                current_line_new += 1

            # If we are not in a hunk, then ignore the line
            else:
                pass

    return added_lines, deleted_lines


def _parse_hunk_line(line):
    """
    Given a hunk line in `git diff` output, return the line number
    at the start of the hunk.  A hunk is a segment of code that
    contains changes.
    The format of the hunk line is:
        @@ -k,l +n,m @@ TEXT
    where `k,l` represent the start line and length before the changes
    and `n,m` represent the start line and length after the changes.
    `git diff` will sometimes put a code excerpt from within the hunk
    in the `TEXT` section of the line.
    """
    # Split the line at the @@ terminators (start and end of the line)
    components = line.split('@@')

    # The first component should be an empty string, because
    # the line starts with '@@'.  The second component should
    # be the hunk information, and any additional components
    # are excerpts from the code.
    if len(components) >= 2:

        hunk_info = components[1]
        groups = HUNK_LINE_RE.findall(hunk_info)

        if len(groups) == 1:

            try:
                return int(groups[0])

            except ValueError:
                msg = "Could not parse '{0}' as a line number".format(groups[0])
                raise GitDiffError(msg)

        else:
            msg = "Could not find start of hunk in line '{0}'".format(line)
            raise GitDiffError(msg)

    else:
        msg = "Could not parse hunk in line '{0}'".format(line)
        raise GitDiffError(msg)
