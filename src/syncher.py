import errno
import os
import shutil
import stat

from git import Repo


def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        raise

def synch_to_github(git_repo, repo_name, branch, src_dir):
    ''' Synchs files to github'''

    # clone repository
    clone_dir = os.path.join(os.getcwd(), repo_name)
    print(f"Clone git repo {git_repo} to {clone_dir}")
    repo = Repo.clone_from(git_repo, clone_dir)
    os.chdir(clone_dir)

    # checkout branch
    if branch not in repo.branches:
        # if branch does not exist. create one
        print("Requested branch not in git repository. Branch created")
        repo.create_head(branch)
    repo.git.checkout(branch)

    # clean up
    repo.close()
    shutil.rmtree(os.path.abspath(clone_dir), ignore_errors=False, onerror=handleRemoveReadonly)

synch_to_github("https://github.com/FlorianBuhl/GitCliTest.git", "GitCliTest", "main", "D:/Workspaces/syncher/sandbox")
