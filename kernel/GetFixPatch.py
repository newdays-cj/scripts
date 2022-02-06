#!/usr/bin/python3
import os
import sys
import re
import GetCommit
import MultiRun
import Color

MAINLINE_RANGE = ""
STABLE_RANGE = ""

MAINLINE_URL = "https://mirrors.tuna.tsinghua.edu.cn/git/linux.git"
STABLE_URL = "https://mirrors.tuna.tsinghua.edu.cn/git/linux-stable.git"

def InitRemoteInfo():
    global MAINLINE_RANGE
    global STABLE_RANGE
    remotes = os.popen("git remote -v | grep fetch").readlines()
    for remote in remotes:
        remote = remote.replace(" ", "\t").split("\t")
        if remote[1] == MAINLINE_URL:
            MAINLINE_RANGE = "v5.10.." + remote[0] + "/master"
        if remote[1] == STABLE_URL:
            STABLE_RANGE = "v5.10.." + remote[0] + "/linux.5.10.y"

def IsFixPatch(subject, commit):
    log = os.popen("git log -n 1 " + commit + " | grep \"Fixes:\"").readlines()
    for __log in log:
        if __log[__log.find("(") + 2: __log.rfind(")") - 1] == subject:
            return True
    return False

def __GetFixPatchByCommit(commit, prefix):
    subject = os.popen("git log --pretty=oneline -n 1 " + commit).readline()[41:]
    subject = subject.strip("\n")
    subject = GetCommit.SubjectHelper(subject)
    subject_re = subject.replace("\"", "\\\"").replace("\`", "\\\`")
    ret = []

    current_commit, current_subject, current_version = GetCommit.GetBySubject(subject, "v5.10..HEAD", False)
    if current_commit is None:
        ret += [Color.red(prefix + commit + " " + subject)]
    else:
        ret += [Color.green(prefix + commit + " " + subject + " [merged]")]

    cmd = "git log --no-merges --pretty=oneline --grep=\"" + subject_re + "\" " + MAINLINE_RANGE
    fix_commits = os.popen(cmd).readlines()
    for fix_commit in fix_commits:
        __commit = fix_commit[:40]
        __subject = fix_commit[41:]
        if IsFixPatch(subject, __commit):
            ret += __GetFixPatchByCommit(__commit, prefix + "\t")
    
    return ret

def GetFixPatchByCommit(commit):
    return __GetFixPatchByCommit(commit, "")

def main():
    commits = []
    ret = []
    if os.path.exists(sys.argv[1]) == True:
        commits = os.popen("cat " + sys.argv[1]).readlines()
    else:
        commits = sys.argv[1:]

    InitRemoteInfo()
    #for commit in commits:
    #    ret.append(GetFixPatchByCommit(commit))
    ret = MultiRun.run(func = GetFixPatchByCommit, argsv = commits, thread_count = 16)
    for __ret in ret:
        for ____ret in __ret:
            print(____ret)

if __name__ == '__main__':
    main()
