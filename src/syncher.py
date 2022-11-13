import os
import shutil
from git import Repo


def synch_to_github(git_repo, repo_name, branch, srcDir):
    ''' Synchs files to github'''

    # clone repository
    clone_dir = os.path.join(os.path.curdir + repo_name)
    if os.path.exists(clone_dir) is False:
        os.mkdir(clone_dir)
    os.chdir(clone_dir)
    repo = Repo.clone_from(git_repo, clone_dir)

    if branch not in repo.branches:
        print("Requested branch not in git repository")
        repo.create_head(branch)

    repo.git.checkout(branch)

    shutil.rmtree(clone_dir)
git_repo = "https://github.com/FlorianBuhl/GitCliTest.git"
synch_to_github(git_repo, "GitCliTest", "main", "D:/Workspaces/syncher/sandbox")
