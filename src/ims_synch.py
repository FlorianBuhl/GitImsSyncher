''' Handles IMS side'''

import subprocess
import re
import shutil
import os
import stat

def del_rw(action, name, exc):
    ''' Removes read protection and removes a file'''
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

def get_from_number(checkpoints: "list[Checkpoint]", number:str):
    ''' Reports checkpoint from number'''
    for checkpoint in checkpoints:
        if checkpoint.number is number:
            return checkpoint
    return None
class Checkpoint:
    ''' IMS checkpoint class '''

    def __init__(self, number:str, author:str):
        self.number = number
        self.author = author

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

def get_checkpoints_from(ims_project: str, branch:str, lowest_checkpoint_number: str) -> "list[Checkpoint]":
    ''' Reports all checkpoints on a branch coming after the given checkpoint number'''

    cmd = f"si viewprojecthistory --project={ims_project} "
    cmd += "--fields=revision,author "
    if branch == "Normal":
        cmd += "--rfilter=range:1.1-"
    else:
        cmd += "--rfilter=devpath:{branch}"

    # execute bat cmd
    print(f"cmd executed: {cmd}")
    result = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode("utf-8").rstrip()
    print(stdout)

    # each line is representing a checkpoint
    # the first line holds the bat cmd
    stdout_lines = stdout.split("\n")
    stdout_lines = stdout_lines[1:]
    stdout = "\n".join(stdout_lines)
    print(f"checkpoints:{stdout_lines}")

    regex = r"(\S+)\s+(.*)"
    pattern = re.compile(regex, re.MULTILINE)

    checkpoints = []
    for match in re.finditer(pattern, stdout):
        checkpoint = Checkpoint(match.group(1), match.group(2))
        checkpoints.append(checkpoint)

    # limit list with given lowest checkpoint parameter
    if lowest_checkpoint_number is not None:
        lowest_checkpoint = get_from_number(checkpoints, lowest_checkpoint_number)
        idx:int = checkpoints.index(lowest_checkpoint)
        checkpoints = checkpoints[0:idx]

    checkpoints.reverse()
    print(f"checkpoints:{checkpoints}")
    return checkpoints

###################################################################################################
# checkout

def checkout(ims_project: str, checkpoint: str, sandbox_dir: str):
    ''' checkout of an specific IMS checkpoint into the given directory '''

    cmd = f"si createsandbox --project={ims_project} -R -Y "
    cmd += f"--projectRevision={checkpoint} {sandbox_dir}"

    # execute bat cmd
    print(f"cmd executed: {cmd}")
    result = subprocess.run(cmd, shell=True, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode("utf-8").rstrip()
    print(stdout)
    print("files which were checkout")
    print(os.listdir(sandbox_dir))

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

    ims_dir = os.path.dirname(sandbox_project)

    # Remove everything in ims_dir folder
    sub_dirs = os.scandir(ims_dir)
    for sub_dir in sub_dirs:
        print(sub_dir)
        if sub_dir.is_dir():
            shutil.rmtree(sub_dir.path, onerror=del_rw)
        elif sub_dir.is_file() or sub_dir.is_symlink():
            os.unlink(sub_dir.path)
