''' Main module '''
import git_synch
import ims_synch

# parameters
ims_repo = "0C/bsw/iopt/spi/project.pj"
git_repo = "https://github.com/FlorianBuhl/GitCliTest.git"
git_repo_name = "GitCliTest"

repo = git_synch.clone_repo(git_repo, git_repo_name)
ims_branches = ims_synch.get_branches()

git_branches = git_synch.get_branches(repo)
print(f'branches: {git_branches}')
branch = git_branches[0]
commits = git_synch.get_commits(repo, branch)

last_synched_commit = git_synch.get_last_synched_commit(repo, branch)

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

