import os
import launch


def prepare_environment():
    print(f"Git the roop to repositories")
    roop_repo = os.environ.get('ROOP_REPO', 'https://github.com/s0md3v/roop.git')

    roop_commit_hash = os.environ.get('ROOP_COMMIT_HASH', "1a8d37126174bb4e281acad35a258afe3a98e667")

    print(f"Roop repo: {launch.repo_dir('roop-repo')}")
    launch.git_clone(roop_repo, launch.repo_dir('roop-repo'), "Roop", roop_commit_hash)


prepare_environment()
