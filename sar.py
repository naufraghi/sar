#!/usr/bin/env python
#-*- coding: utf-8 -*-

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
import re
import difflib

import argparse

def glob_files(basepath, glob_filter):
    for filename in glob.glob(basepath + '/' + glob_filter):
        if os.path.isfile(filename):
            yield filename

def recursive_dirs(basepath):
    for root, dirs, files in os.walk(basepath):
        for dir in dirs:
            yield os.path.relpath(os.path.join(root, dir), basepath)

def re_compile(regex):
    return re.compile(regex, re.DOTALL)

def iter_files(args, basepath=os.getcwd()):
    for afile in args.files:
        yield afile
    for aglob in args.globs:
        for afile in glob_files(basepath, aglob):
            yield afile
        if args.recursive:
            for adir in recursive_dirs(basepath):
                for afile in glob_files(adir, aglob):
                    yield afile

def main():
    parser = argparse.ArgumentParser(description="Search and replace utility")
    parser.add_argument("searchre", type=re_compile)
    parser.add_argument("replacere")
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("-v", "--verbose", action="store_false", default=True)
    parser.add_argument("-r", "--recursive", action="store_true", default=False) 
    parser.add_argument("-g", "--globs", nargs="+", default=[])

    args = parser.parse_args()

    if args.verbose:
        debug = sys.stderr.write
    else:
        debug = lambda x: None

    if not (args.files or args.globs):
        parser.error("Provide files or -g globs!")
    
    processed = set()
    for filename in iter_files(args):
        if filename in processed:
            continue
        processed.add(filename)
        debug("Processing file %s... " % filename)
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
