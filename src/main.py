''' User CLI interface '''

###################################################################################################
# imports

import os
import typer
import git_synch
import ims_synch

###################################################################################################
# CLI

app = typer.Typer()

@app.command()
def synch_ims_to_github(ims_repo: str = typer.Argument(...,
            help="IMS project path"),
        git_repo_url: str = typer.Argument(...,
         help="Github repository url"),
        branch: str = typer.Option(...,
            help="IMS branch name which shall be synched"),
        dest_branch: str = typer.Option(None,
            help="Branch name in github"),
        create_dest_branch: bool = typer.Option(False,
            help="Create branch in github if not existing")):
    ''' synch IMS to github'''
    print(f"Synch IMS project {ims_repo} branch {branch} to github {git_repo_url}")

    # clone git repo
    git_repo_name = git_synch.get_repo_name_from_https(git_repo_url)
    git_repo = git_synch.clone_repo(git_repo_url, git_repo_name)

    # get git branches
    git_branches = git_synch.get_branches(git_repo)
    print(f"git branches: {git_branches}")
    # get IMS branches
    ims_branches = ims_synch.get_branches(ims_repo)
    print(f"ims branches: {ims_branches}")

    # check git dest branch
    if len(git_branches) == 0:
        # git repo is empty a new branch needs to be created with the first commit
        create_git_branch_on_commit = True
    else:
        # git repo is not empty
        if dest_branch:
            if not dest_branch in git_branches:
                print(f"requested branch {dest_branch} not found in git repository")
                typer.Abort(1)
        else:
            dest_branch = branch
            if not branch in git_branches:
                print(f"requested branch {dest_branch} not found in git repository")
                typer.Abort(2)

    print(f"destination git branch: {dest_branch}")

    # determine checkpoints to be synched
    last_synched_commit = None
    if dest_branch in git_branches:
        last_synched_commit = git_synch.get_last_synched_commit(git_repo, branch)
        if last_synched_commit is not None:
            # get ims checkpoint information
            print("something is synched")
            ims_last_synched_checkpoint_number = git_synch.get_ims_checkpoint(last_synched_commit)
            checkpoints_to_synch = ims_synch.get_checkpoints_from(ims_repo,branch, ims_last_synched_checkpoint_number)

    if last_synched_commit is None:
        # complete branch has no IMS checkpoints
        print("no commit synched")
        checkpoints_to_synch = ims_synch.get_checkpoints_from(ims_repo, branch, None)

    for checkpoint in checkpoints_to_synch:
        ims_repo_dir = os.path.join(os.path.dirname(__file__), "tmp", "ims_repo")
        sandbox_dir = "d:/uidtemp/checkouts/test1/"
        sandbox_dir_project = sandbox_dir + "project.pj"
        if not os.path.exists(sandbox_dir):
            os.makedirs(sandbox_dir)
        ims_synch.checkout(ims_repo, checkpoint, sandbox_dir)
        git_synch.synch_dir_to_git(git_repo_url, git_repo_name, branch, sandbox_dir, "test commits" + checkpoint)
        ims_synch.drop_sandbox(sandbox_dir_project)


###################################################################################################
# Synch Github to IMS

@app.command()
def synch_github_to_ims(git_repo_url: str = typer.Argument(...,
            help="Github repository url"),
          ims_repo: str = typer.Argument(...,
            help="IMS project path"),
          branch: str = typer.Option(None,
            help="IMS branch name which shall be synched")):
    ''' Synch Github to IMS'''
    print(f"Synch Github project {git_repo_url} branch {branch} to ims {ims_repo}")

    # clone git repo
    git_repo_name = git_synch.get_repo_name_from_https(git_repo_url)
    git_repo = git_synch.clone_repo(git_repo_url, git_repo_name)

    # get IMS branches
    ims_branches = ims_synch.get_branches()
    print(f"ims branches: {ims_branches}")
    # get git branches
    git_branches = git_synch.get_branches(git_repo)
    print(f"git branches: {git_branches}")

    if branch or len(git_branches)==0:
        if branch in git_branches:
            print("requested branch to synch found")
            last_synched_commit = git_synch.get_last_synched_commit(git_repo, branch)
            if last_synched_commit is None:
                # complete branch has no IMS checkpoints
                print("no commit synched")
            else:
                # get ims checkpoint information
                print("something is synched")
                ims_last_synched_checkpoint_number = git_synch.get_ims_checkpoint(last_synched_commit)
                checkpoints = ims_synch.get_checkpoints_from(ims_repo, ims_last_synched_checkpoint_number)
                for checkpoint in checkpoints:
                    sandbox_dir = "d:/uidtemp/checkouts/test1/"
                    sandbox_dir_project = sandbox_dir + "project.pj"
                    ims_synch.checkout(ims_repo, checkpoint, sandbox_dir)
                    # git_synch.synch_dir_to_git(git_repo, git_repo_name, branch, "")
                    ims_synch.drop_sandbox(sandbox_dir_project)
    else:
        print(f"requested branch {branch} not found in git repository")

if __name__ == "__main__":
    app()
