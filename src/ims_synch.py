''' Handles IMS side'''

import subprocess
import re
import shutil
import os

###################################################################################################
# get_branches

def get_branches(ims_project:str) -> list:
    ''' reports branches of the given repo '''
    cmd = f"si projectinfo --project={ims_project} "
    cmd +="--noacl --noattributes --noassociatedIssues --noshowCheckpointDescription"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode("utf-8").rstrip()
    print(stdout)

    # get development paths as text
    regex = r"Development Paths:\n(.*)"
    match = re.search(regex, stdout, re.MULTILINE|re.S)

    # each line is holding one development path
    regex = r"(\S*) \(.*\)"
    pattern = re.compile(regex, re.MULTILINE)

    branches = []
    for match in pattern.finditer(stdout):
        branches.append(match.group(1))

    print(branches)
    return branches

###################################################################################################
# get_checkpoints_from

def get_checkpoints_from(ims_project: str, branch:str, lowestCheckpoint: str) -> "list[str]":
    ''' Reports all checkpoints on a branch coming after the given checkpoint number'''

    cmd = f"si viewprojecthistory --project={ims_project} "
    cmd += "--fields=revision "
    if branch == "Normal":
        cmd += "--rfilter=range:1.1-"
    else:
        cmd += "--rfilter=devpath:{branch}"

    # execute bat cmd
    print(f"cmd executed: {cmd}")
    result = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode("utf-8").rstrip()
    print(stdout)

    checkpoints = stdout.split("\n")
    checkpoints = checkpoints[1:]
    print(f"checkpoints:{checkpoints}")

    if lowestCheckpoint is not None:
        idx:int = checkpoints.index(lowestCheckpoint)
        checkpoints = checkpoints[0:idx]

    checkpoints.reverse()
    print(f"checkpoints:{checkpoints}")
    return checkpoints

###################################################################################################
# checkout

def checkout(ims_project: str, checkpoint: str, sandbox_dir: str):
    ''' checkout of an specific IMS checkpoint into the given directory '''

    cmd = f"si createsandbox --project={ims_project} --noconfirm -R -Y"
    cmd += f"--projectRevision={checkpoint} {sandbox_dir}"

    # execute bat cmd
    print(f"cmd executed: {cmd}")
    result = subprocess.run(cmd, shell=True, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode("utf-8").rstrip()
    print(stdout)

###################################################################################################
# drop_sandbox

def drop_sandbox(sandbox_project: str):
    ''' drop sandbox'''
    cmd = f"si dropsandbox --noconfirm --delete=none {sandbox_project}"

    # execute bat cmd
    print(f"cmd executed: {cmd}")
    result = subprocess.run(cmd, shell=True, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode("utf-8").rstrip()
    print(stdout)

    shutil.rmtree(os.path.dirname(sandbox_project))
