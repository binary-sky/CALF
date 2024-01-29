# Program Author: Qingxu Fu, CASIA

import os
import shutil

author = "Qingxu Fu, CASIA"
prefix = "# Program Author: " + author

# Get the current directory
current_dir = os.getcwd()

# Iterate through all files and directories in the current directory
for root, dirs, files in os.walk(current_dir):
    for file in files:
        # Check if the file is a Python file
        if file.endswith(".py"):
            # Open the file in read mode
            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                # Read the existing contents
                contents = f.read()

            # Add the prefix at the beginning of the file contents
            new_contents = prefix + "\n\n" + contents

            # Open the file in write mode and overwrite the contents
            with open(file_path, "w") as f:
                f.write(new_contents)