''' Handles IMS side'''

def get_branches() -> list:
    ''' reports branches of the given repo '''
    return ["branch1", "branch2", "branch3"]

def get_checkpoints_from(repo: str, branch:str, checkpoint: int) -> list[str]:
    ''' Reports all checkpoints on a branch coming after the given checkpoint number'''

def checkout(repo: str, checkpoint: int, dir: str):
    ''' checkout of an specific IMS checkpoint into the given directory '''
    print("not implemented")
