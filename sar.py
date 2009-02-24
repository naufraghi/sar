#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Search and replace utility
------------------------------------------
Usage:
    sar.py searchre replacere [globfilter]
Output:
    a patch -p0 < patch.diff
"""

import sys
import os
import os.path
import glob
import re
import difflib

pjoin = os.path.join

def list_recursive_files(basepath, glob_filter):
    for filename in glob.glob(pjoin(basepath, glob_filter)):
        if os.path.isfile(filename):
            yield filename
    for root, dirs, files in os.walk(basepath):
        for dir in dirs:
            for filename in glob.glob(pjoin(pjoin(root, dir), glob_filter)):
                if os.path.isfile(filename):
                    yield filename


def main(args):
    if len(args) < 2:
        print "Provide: searchre replacere [globfilter]"
        sys.exit(0)

    if len(args) < 3:
        args.append("*")

    (searchre, replacere), glob_filters = args[:2], args[2:]
    searchre = re.compile(searchre, re.DOTALL)

    for glob_filter in glob_filters:
        for filename in list_recursive_files(os.getcwd(), glob_filter):
            sys.stderr.write("Processing file %s... " % filename)
            try:
                res = orig = open(filename).read()
            except IOError:
                sys.stderr.write("ERROR reading file %s!" % filename)
                continue
            res = searchre.sub(replacere, res)

            if orig != res:
                sys.stderr.write("MATCH FOUND")
                print "Index:", filename
                print "=" * 80
                print ''.join(list(difflib.unified_diff(orig.splitlines(1),
                                                        res.splitlines(1),
                                                        filename + " (original)",
                                                        filename + " (modified)"))),
            sys.stderr.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
