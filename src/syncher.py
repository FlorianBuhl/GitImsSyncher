import distutils.dir_util
import os
import shutil
import sys

from git import Repo

SYS_EXIT_UNTRACKED_FILES_IN_TARGET_REPO = "1: Untracked files in target repository"

def synch_to_github(git_repo, repo_name, branch, src_dir):
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
            print("remove")
            shutil.rmtree(sub_dir.path)
        elif sub_dir.is_file() or sub_dir.is_symlink():
            os.unlink(sub_dir.path)

    # copy files from source directory
    distutils.dir_util.copy_tree(src_dir, clone_dir)

    # clean up
    repo.close()

synch_to_github("https://github.com/FlorianBuhl/GitCliTest.git",
    "GitCliTest", "main", "D:/Workspaces/syncher/sandbox")
