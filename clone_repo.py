# clone_repo.py
import os
import shutil
from git import Repo
import shutil
import os

def force_remove_readonly(func, path, _):
    os.chmod(path, 0o777)
    func(path)

def clone_repo(repo_url, save_dir="cloned_repo"):
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir, onerror=force_remove_readonly)  # 💣 Force deletion

    
    try:
        Repo.clone_from(repo_url, save_dir)
        print(f"✅ Cloned to {save_dir}")
        return save_dir
    except Exception as e:
        print(f"❌ Failed to clone: {e}")
        return None

