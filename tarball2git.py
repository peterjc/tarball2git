#!/usr/bin/env python
"""Simple Python script to take a set of versioned tar balls and import them into a git repository

Source code for this script is being tracked in git on github here:
https://github.com/peterjc/tarball2git

TODO:
 - Command line API
 - Handle removal of files between tarballs
 - Handle alpha/beta/release candidate naming? 
"""
import sys
import os
import re
import git

#Usage:
#
# $ mkdir split-dist
# $ cd split-dist
# $ git init
# $ tarball2git.py
#
#Example set of tarballs from http://daimi.au.dk/~mailund/split-dist/
#turned into git repository now at https://github.com/peterjc/split-dist

repo_path = "."
tarball_path = "/Users/pjcock/Downloads/Software"
tarball_re = re.compile("sdist-(?P<major>\d+).(?P<minor>\d+).(?P<revision>\d+).tar.gz")
dir_pattern = "sdist-%(major)i.%(minor)i.%(revision)i"
tag_pattern = "v%(major)i.%(minor)i.%(revision)i"
author = "Thomas Mailund <mailund@birc.au.dk>"

tarballs = []
for f in os.listdir(tarball_path):
    match = tarball_re.match(f)
    if not match: continue
    major = int(match.group('major'))
    minor = int(match.group('minor'))
    revision = int(match.group('revision'))
    tarballs.append((major, minor, revision, f))
tarballs.sort()

assert os.path.isdir(repo_path)
assert os.path.isdir(os.path.join(repo_path, ".git"))
repo = git.Repo(repo_path)
assert not repo.bare
assert not repo.is_dirty()

def run(cmd):
    return_code = os.system(cmd)
    if return_code:
        sys.stderr.write("Return code %i from:\n%s" % (return_code, cmd))
        sys.exit(return_code)

def get_date(folder):
    dates = []
    for root, dirs, files in os.walk(folder):
        for f in files:
            dates.append(os.path.getmtime(os.path.join(root, f)))
    return max(dates)

for major, minor, revision, f in tarballs:
    values = {"major":major, "minor":minor, "revision":revision}
    tag = tag_pattern % values
    dir = dir_pattern % values
    tarball = os.path.join(tarball_path, f)
    print tag
    run("tar -zxvf %s" % tarball)
    assert os.path.isdir(dir)
    commit_date = get_date(dir)
    run("mv %s/* ." % dir)
    os.rmdir(dir)
    repo.index.add(repo.untracked_files)
    repo.git.commit("-m", 'Committing %s' % f,
                    "--author", '"%s"' % author,
                    "--date", commit_date)
    repo.git.tag(tag)
