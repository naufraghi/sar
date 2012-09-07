#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright (C) 2011-2012 Matteo Bertini <matteo@naufraghi.net>
# Latest version: https://github.com/naufraghi/sar/

"""
Search and replace utility
------------------------------------------
Usage:
    sar.py ... > patch.diff
Output:
    patch -p0 < patch.diff
"""

import sys
import os
import glob
import difflib

try:
    import regex as re
except ImportError:
    # http://bugs.python.org/issue1662581
    # Avoid things like:
    #   r = re.compile(r'(\w+)*=.*')
    #   r.match("abcdefghijklmnopqrstuvwxyz")
    import re

import argparse

def glob_files(basepath, glob_filter):
    for filename in glob.glob(basepath + '/' + glob_filter):
        if os.path.isfile(filename):
            yield filename

def is_scm(adir):
    for scm in (".git", "CVS", ".svn", ".hg"):
        _, tail = os.path.split(adir)
        if scm == tail:
            return True
    return False

def recursive_dirs(basepath):
    for root, dirs, files in os.walk(basepath):
        for adir in dirs:
            if is_scm(adir):
                dirs.remove(adir)
            else:
                yield os.path.relpath(os.path.join(root, adir), os.getcwd())

def re_compile(regex):
    return re.compile(regex, re.DOTALL)

def iter_files(args):
    for aglob in args.files:
        for afile in glob_files(args.basepath, aglob):
            yield afile
        if args.recursive:
            for adir in recursive_dirs(args.basepath):
                for afile in glob_files(adir, aglob):
                    yield afile

def check_folder(adir):
    if os.path.isdir(adir):
        return adir

def main():
    parser = argparse.ArgumentParser(description="Search and replace utility")
    parser.add_argument("searchre", type=re_compile)
    parser.add_argument("replacere")
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("-q", "--quiet", action="store_true", default=False)
    parser.add_argument("-r", "--recursive", action="store_true", default=False)
    parser.add_argument("-b", "--basepath", type=check_folder, default='.')

    args = parser.parse_args()

    if not args.quiet:
        debug = sys.stderr.write
    else:
        debug = lambda x: None

    if not args.files:
        parser.error("Provide files or globs!")
    if not args.basepath:
        parser.error("Provide a valid basepath")

    debug("Searching for '%s' and replacing to '%s'\n\n" % (args.searchre.pattern, args.replacere))

    processed = set()
    for filename in iter_files(args):
        if filename in processed:
            continue
        processed.add(filename)
        debug("Processing file %s ... " % filename)
        try:
            res = orig = open(filename).read()
        except IOError:
            debug("ERROR reading file %s!\n" % filename)
            continue
        res = args.searchre.sub(args.replacere, res)

        if orig != res:
            debug("MATCH FOUND\n")
            print "Index:", filename
            print "=" * 80
            diff = ''.join(list(difflib.unified_diff(orig.splitlines(1),
                                                     res.splitlines(1),
                                                     filename + " (original)",
                                                     filename + " (modified)")))
            print diff
            if diff[-1] != "\n":
                print "\\ No newline at end of file"
        debug("\n")


if __name__ == "__main__":
    main()
