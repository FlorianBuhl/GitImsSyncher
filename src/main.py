''' User CLI interface '''

###################################################################################################
# imports

import os
import logging

import typer
from git import Repo

import git_synch
import ims_synch
import util

###################################################################################################

def synch_ims_checkpoint_to_git(checkpoint: ims_synch.Checkpoint, ims_repo: str, branch_name: str,
    git_repo: Repo, sandbox_dir: str, git_dir):
    ''' synchs an ims checkpoint to git '''

    sandbox_dir_project = sandbox_dir + "project.pj"
    ims_synch.checkout(ims_repo, checkpoint.number, sandbox_dir)
    checkpoint_description = ims_synch.get_checkpoint_description(ims_repo, checkpoint.number)
    git_commit_message = ims_synch.generate_git_commit_message(checkpoint_description,
        checkpoint.author, checkpoint.number)
    git_synch.synch_dir_to_git(git_repo, branch_name, git_dir,
        sandbox_dir, git_commit_message, checkpoint.author)
    ims_synch.drop_sandbox(sandbox_dir_project)

###################################################################################################
# CLI

app = typer.Typer()

@app.command()
def synch_ims_to_git(ims_repo: str = typer.Argument(...,
            help="IMS project path"),
        git_repo_url: str = typer.Argument(...,
         help="Github repository url"),
        git_dir: str = typer.Option(...,
            help="Git working directory"),
        ims_dir: str = typer.Option(...,
            help="IMS working directory")):
    ''' synching an given ims repository to a given git repository.
        It will use temporary directories to checkout and and commit. '''

    # setup logger
    util.setup_logger()
    logger = logging.getLogger(__name__)

    # create temporary working directories for git and ims
    logger.info("setup temporary working folders")
    util.setup_temporary_working_folders(git_dir, ims_dir)

    # clone git repo
    git_repo = Repo.clone_from(git_repo_url, git_dir)

    # check if git repo is empty
    synch_everything = False
    if len(git_synch.get_branches(git_repo)) <= 0:
        synch_everything = True

    # cycle through ims branches
    ims_branches = ims_synch.get_branches_with_source(ims_repo)
    for ims_branch in ims_branches:
        print(f"Doing branch {ims_branch.name}, {ims_branch.base_checkpoint}, {ims_branch.source_dev_path_name}")
        logger.info(f"Doing branch {ims_branch.name}, {ims_branch.base_checkpoint}, {ims_branch.source_dev_path_name}")

        # is branch in target repo existing. if not create it.
        synch_complete_branch = False
        is_ims_branch_in_git = ims_branch.name in git_synch.get_branches(git_repo)
        if (ims_branch.name != "Normal") and not is_ims_branch_in_git:
            # create branch
            print(f"ims_branch.source_dev_path_name: {ims_branch.source_dev_path_name}")
            print(f"ims_branch.base_checkpoint: {ims_branch.base_checkpoint}")
            commit_to_create_branch_from = git_synch.get_commit(git_repo,
                ims_branch.source_dev_path_name, ims_branch.base_checkpoint)
            git_repo.create_head(ims_branch.name, commit_to_create_branch_from)
            # git_repo.git.checkout(ims_branch.name) # checkout branch
            synch_complete_branch = True

        # checkout branch
        if len(git_synch.get_branches(git_repo)) > 0:
            if ims_branch.name == "Normal":
                git_repo.git.checkout("main")
            else:
                git_repo.git.checkout(ims_branch.name)

        last_synched_checkpoint_number = None
        if not (synch_everything or synch_complete_branch):
            # get last synched commit in branch
            if ims_branch.name == "Normal":
                # mainline in IMS is called Normal, mainline in git is called main
                last_synched_commit = git_synch.get_last_synched_commit(git_repo, "main")
            else:
                last_synched_commit = git_synch.get_last_synched_commit(git_repo, ims_branch.name)

            if last_synched_commit is not None:
                last_synched_checkpoint_number = git_synch.get_ims_checkpoint(last_synched_commit)
                logger.info("last synched checkpoint number: %s", last_synched_checkpoint_number)

        # get checkpoints which has to be synched
        checkpoints_to_synch = ims_synch.get_checkpoints_from(ims_repo, ims_branch.name,
            last_synched_checkpoint_number)

        print(f"Number of checkpoints to synch: {len(checkpoints_to_synch)}")
        logger.info("Number of checkpoints to synch: %s", str(len(checkpoints_to_synch)))

        # cycle through checkpoints
        for checkpoint in checkpoints_to_synch:
            logger.info("Synch checkpoint: %s", checkpoint.number)
            synch_ims_checkpoint_to_git(checkpoint, ims_repo, ims_branch.name, git_repo, ims_dir, git_dir)

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
            help="Create branch in github if not existing"),
        git_dir: str = typer.Option(...,
            help="Git working directory"),
        ims_dir: str = typer.Option(...,
            help="IMS working directory")):
    ''' synch IMS to github'''
    print(f"Synch IMS project {ims_repo} branch {branch} to github {git_repo_url}")

    # create temporary git working directory
    if not os.path.exists(git_dir):
        os.makedirs(git_dir)
        print(f"Directory created: {git_dir}")

    # create temporary IMS working directory
    if not os.path.exists(ims_dir):
        os.makedirs(ims_dir)
        print(f"Directory created: {ims_dir}")

    # clone git repo
    git_repo_name = git_synch.get_repo_name_from_https(git_repo_url)
    # git_repo = git_synch.clone_repo(git_repo_url, git_repo_name)
    git_repo = Repo.clone_from(git_repo_url, git_dir)

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
    checkpoints_to_synch: "list[ims_synch.Checkpoint]"
    last_synched_commit = None
    if dest_branch in git_branches:
        last_synched_commit = git_synch.get_last_synched_commit(git_repo, branch)
        if last_synched_commit is not None:
            # get ims checkpoint information
            print("something is synched")
            ims_last_synched_checkpoint_number = git_synch.get_ims_checkpoint(last_synched_commit)
            checkpoints_to_synch = ims_synch.get_checkpoints_from(ims_repo, branch,
                ims_last_synched_checkpoint_number)

    if last_synched_commit is None:
        # complete branch has no IMS checkpoints
        print("no commit synched")
        checkpoints_to_synch = ims_synch.get_checkpoints_from(ims_repo, branch, None)

    for checkpoint in checkpoints_to_synch:
        sandbox_dir = ims_dir
        sandbox_dir_project = sandbox_dir + "project.pj"
        if not os.path.exists(sandbox_dir):
            os.makedirs(sandbox_dir)
        ims_synch.checkout(ims_repo, checkpoint.number, sandbox_dir)
        checkpoint_description = ims_synch.get_checkpoint_description(ims_repo, checkpoint.number)
        git_commit_message = ims_synch.generate_git_commit_message(checkpoint_description, checkpoint.author, checkpoint.number)
        git_synch.synch_dir_to_git(git_repo, dest_branch, git_dir, sandbox_dir, git_commit_message, checkpoint.author)
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
                checkpoints = ims_synch.get_checkpoints_from(ims_repo,
                    ims_last_synched_checkpoint_number)
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
