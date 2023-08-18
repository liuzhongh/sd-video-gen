import os
from modules.paths_internal import script_path
import launch


def prepare_environment():
    print(f"Git the roop to repositories")
    print(f"{script_path}")
    roop_repo = os.environ.get('ROOP_REPO', 'https://github.com/s0md3v/roop.git')

    roop_commit_hash = os.environ.get('ROOP_COMMIT_HASH', "b86cc7986afa436df1b16bc4ef68ef00437627eb")

    roop_path = os.path.join(script_path, "roop")
    print(f"Roop repo: {roop_path}")
    # launch.git_clone(roop_repo, roop_path, "Roop", roop_commit_hash)


prepare_environment()
