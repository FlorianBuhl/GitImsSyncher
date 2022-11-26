''' Module handles git side'''

###################################################################################################
# imports

import os
import shutil
import sys
import re
from git import Repo
from git import Commit

###################################################################################################
# constants

SYS_EXIT_UNTRACKED_FILES_IN_TARGET_REPO = "1: Untracked files in target repository"

###################################################################################################
# synch_dir_to_git

def synch_dir_to_git(git_repo, repo_name, branch, src_dir, commit_message):
    ''' Synchs files to github'''

    clone_dir = os.path.join(os.getcwd(), repo_name)
    if os.path.exists(clone_dir):
        # Folder already exists.
        repo = Repo(clone_dir)
    else:
        # clone repository
        print(f"Clone git repo {git_repo} to {clone_dir}")
        repo = Repo.clone_from(git_repo, clone_dir)
    os.chdir(clone_dir)

    # checkout branch
    if branch not in repo.branches:
        # if branch does not exist. create one
        print("Requested branch not in git repository. Branch created")
        repo.create_head(branch)
    print(f"Checkout branch {branch}")
    repo.git.checkout(branch)

    # untracked files would be lost. Terminate with exit code to warn the user.
    if len(repo.untracked_files) > 0:
        print("There are untracked files in the repository.")
        print("Untracked files would be lost when synchronization is done")
        print("Remove them up in front or add them to the repository")
        print(f"untracked files: {repo.untracked_files}")
        sys.exit(SYS_EXIT_UNTRACKED_FILES_IN_TARGET_REPO)

    # Remove everything but ".git" folder
    sub_dirs = os.scandir(clone_dir)
    for sub_dir in sub_dirs:
        print(sub_dir)
        if sub_dir.is_dir() and sub_dir.name != ".git":
            shutil.rmtree(sub_dir.path)
        elif sub_dir.is_file() or sub_dir.is_symlink():
            os.unlink(sub_dir.path)

    # copy files from source directory
    print(f"Copy files from {src_dir} to {clone_dir}")
    shutil.copytree(src_dir, clone_dir, dirs_exist_ok=True)

    # commit all files and push to server
    print("Add all files to index")
    repo.git.add(all=True)
    print("Commit files")
    repo.index.commit(commit_message)
    print("Push to remote")
    repo.remote().push()

    # clean up
    repo.close()

###################################################################################################
# clone_repo

def clone_repo(git_repo: str, repo_name: str) -> Repo:
    ''' Clones a git repository and return the repo handle '''

    clone_dir = os.path.join(os.getcwd(), repo_name)
    if os.path.exists(clone_dir):
        # Folder already exists.
        repo = Repo(clone_dir)
    else:
        # clone repository
        print(f"Clone git repo {git_repo} to {clone_dir}")
        repo = Repo.clone_from(git_repo, clone_dir)
    os.chdir(clone_dir)
    return repo

###################################################################################################
# get_branches

def get_branches(repo: Repo) -> list:
    ''' reports branches of the given repo '''
    return repo.branches

###################################################################################################
# get_last_synched_commit

def get_last_synched_commit(repo: Repo, branch: str):
    ''' searches for a commit which is synched with IMS '''

    branch_commits = repo.iter_commits(branch)

    # for current_commit in branch_commits[::-1]:
    for current_commit in branch_commits:
        print(current_commit)
        print(current_commit.message)

    print("get last synched commit")

###################################################################################################
# is_commit_synched_with_ims

def is_commit_synched_with_ims(commit: Commit) -> bool:
    ''' Checks if a commit is already synched to an IMS checkpoint '''
    if re.search(r".*IMS CP \d+\.\d+ .*", commit.message) is None:
        return False
    return True

# synch_dir_to_git("https://github.com/FlorianBuhl/GitCliTest.git",
#     "GitCliTest", "main", "D:/Workspaces/syncher/sandbox",
#     "Example commit message")