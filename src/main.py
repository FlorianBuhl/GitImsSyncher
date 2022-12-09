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
            help="IMS branch name which shall be synched")):
    ''' synch IMS to github'''
    print(f"Synch IMS project {ims_repo} branch {branch} to github {git_repo_url}")

    # clone git repo
    git_repo_name = git_synch.get_repo_name_from_https(git_repo_url)
    git_repo = git_synch.clone_repo(git_repo_url, git_repo_name)

    # get git branches
    git_branches = git_synch.get_branches(git_repo)
    print(f"git branches: {git_branches}")
    # get IMS branches
    ims_branches = ims_synch.get_branches()
    print(f"ims branches: {ims_branches}")

    if branch:
        if branch in git_branches:
            print("requested branch to synch found")
            last_synched_commit = git_synch.get_last_synched_commit(git_repo, branch)
            if last_synched_commit is None:
                # complete branch has no IMS checkpoints
                print("no commit synched")
                checkpoints_to_synch = ims_synch.get_checkpoints_from(ims_repo, branch, -1)
            else:
                # get ims checkpoint information
                print("something is synched")
                ims_last_synched_checkpoint_number = git_synch.get_ims_checkpoint(last_synched_commit)
                checkpoints_to_synch = ims_synch.get_checkpoints_from(ims_repo,branch, ims_last_synched_checkpoint_number)

            for checkpoint in checkpoints_to_synch:
                ims_repo_dir = os.path.join(os.path.realpath(__file__), "tmp", "ims_repo")
                ims_synch.checkout(ims_repo, checkpoint, ims_repo_dir)
                git_synch.synch_dir_to_git(git_repo, git_repo_name, branch, ims_repo_dir)
        else:
            print(f"requested branch {branch} not found in git repository")


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

    if branch:
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
                    ims_synch.checkout(ims_repo, checkpoint, "")
                    git_synch.synch_dir_to_git(git_repo, git_repo_name, branch, "")
    else:
        print(f"requested branch {branch} not found in git repository")

if __name__ == "__main__":
    app()
