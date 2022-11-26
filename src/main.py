''' Main module '''
import git_synch
import ims_synch

git_repo = "https://github.com/FlorianBuhl/GitCliTest.git"
git_repo_name = "GitCliTest"
repo = git_synch.clone_repo(git_repo, git_repo_name)
ims_branches = ims_synch.get_branches()

branches = git_synch.get_branches(repo)
print(f'branches: {branches}')
git_synch.get_last_synched_commit(repo, branches[0])

# for branchToSynch in ims_branches:
#     print(branchToSynch)
