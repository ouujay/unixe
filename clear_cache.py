import os
import shutil

# Walk through the directory tree
for root, dirs, files in os.walk("."):
    # Remove __pycache__ directories
    if "__pycache__" in dirs:
        shutil.rmtree(os.path.join(root, "__pycache__"))
    # Remove .pyc files
    for file in files:
        if file.endswith(".pyc"):
            os.remove(os.path.join(root, file))

print("Cleared all __pycache__ directories and .pyc files.")
